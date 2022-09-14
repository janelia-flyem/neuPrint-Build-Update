import json
import time
import subprocess
import requests
import os
from neuprint import Client
from neuprint.admin import Transaction
from neuclease.dvid import *
#from requests.auth import HTTPBasicAuth
from libdvid import DVIDNodeService, ConnectionMethod
from kafka import KafkaConsumer, KafkaProducer
import incremental_update as up

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imx1bWF5YW1AZ21haWwuY29tIiwibGV2ZWwiOiJyZWFkd3JpdGUiLCJpbWFnZS11cmwiOiJodHRwczovL2xoNC5nb29nbGV1c2VyY29udGVudC5jb20vLWJVc2dKUk5sSy1VL0FBQUFBQUFBQUFJL0FBQUFBQUFBQUM4LzlrWHF0UkU0QU5VL3Bob3RvLmpwZz9zej01MCIsImV4cCI6MTc1NTU3ODM5N30.85bQqf8PKbevaktA0vqYFxp--1xF7yecDgB-6-QXiWM"

def update_mutationId (dataset, mut_ID):
    #dataset = "cns-Segment"
    neuprint_bodyId = 0
    query_set = "MATCH (m:Meta) SET m.latestMutationId = " + str(mut_ID)
    print("Update latestMutationId",query_set)
    with Transaction(dataset) as t:
        t.query(query_set)

def check_neuron_exists_neuprint (neuprint_client, dataLabel, neuron_ID):
    #dataset = "cns-Segment"
    neuprint_bodyId = 0
    query = "MATCH (n:" + dataLabel + "{bodyId:" + str(neuron_ID) + "}) RETURN n.bodyId"
    print(query)
    retry_toggle = 0

    try:
        dfresults = neuprint_client.fetch_custom(query)
    except Exception as ex:
        print("NP GET Error",str(ex))
        retry_toggle = 1

    if retry_toggle == 1:
        time.sleep(10)
        print("NP GET Retry")
        dfresults = neuprint_client.fetch_custom(query)

    dfToList = dfresults['n.bodyId'].tolist()
    #print(dfToList)
    if len(dfToList) > 0:
        neuprint_bodyId = dfToList[0]
    return(neuprint_bodyId)

def test_performance (neuprint_client, debug_file):
    query = "WITH [644001906] AS TARGETS MATCH(n:`cns_Neuron`)<-[x:ConnectsTo]-(m:`cns_Neuron`) WHERE n.bodyId in TARGETS AND m.status=\"Traced\" AND x.weight >= 3 RETURN n.bodyId AS body1, x.roiInfo AS info, m.bodyId AS body2, m.roiInfo AS minfo"

    #query = "WITH [644001906] AS TARGETS MATCH(n:`cns_Neuron`)<-[x:ConnectsTo]-(m:`cns_Neuron`) USING INDEX SEEK n:cns_Neuron(bodyId) WHERE n.bodyId in TARGETS AND m.status=\"Traced\" AND x.weight >= 3 RETURN n.bodyId AS body1, x.roiInfo AS info, m.bodyId AS body2, m.roiInfo AS minfo"

    start = time.time()
    dfresults = neuprint_client.fetch_custom(query)
    nowtime = time.time()
    run_time = nowtime - start
    log_test = "Test Query Runs in: " +  str(run_time) + " seconds"
    log_debug_message(debug_file, log_test)

def log_debug_message (debug_file, debug):
    debug_fh = open(debug_file,'a')
    debug_fh.write(debug + "\n")
    debug_fh.close()

def log_mutation_id (mutationIDfile, mutation_id):
    mutation_fh = open(mutationIDfile,'w')
    mutation_fh.write(str(mutation_id) + "\n")
    mutation_fh.close()

def get_body_size ( ns, bodyID ):
    body_size_voxels = 0
    try:
        get_body_size = "segmentation/size/" + str(bodyID)
        print("EP", get_body_size)
        dvid_resp = ns.custom_request(get_body_size, b'' , ConnectionMethod.GET)
        dvid_json = json.loads(dvid_resp)
        body_size_voxels = dvid_json["voxels"]
    except Exception as ex:
        print (str(ex))
        body_size_voxels = 0
    print("Returning Body Size", body_size_voxels)
    return(body_size_voxels)

if __name__ == '__main__':
    neuprint_server = sys.argv[1]
    dvid_uuid = sys.argv[2]
    dataset = sys.argv[3]
    datatmp = dataset.split(":")
    data_version = ""
    if len(datatmp) > 1:
        data_version = datatmp[1]
    dataset_name = datatmp[0]
    print("Using uuid:", dvid_uuid)
    print("DataSet:", dataset_name)
    print("DataVersion:", data_version)
    print("Updating Neuprint Server:", neuprint_server)

    #np_client = Client(neuprint_server)
    #np_client = Client(neuprint_server, verify=False)
    np_client = Client(neuprint_server, 'cns', TOKEN)
    
    if len(data_version) > 0:
        updater = up.NeuPrintUpdater(neuprint_server, dataset_name, tag=data_version, verify=False)
    else:
        updater = up.NeuPrintUpdater(neuprint_server, dataset_name, verify=False)

    log_mutation_file = "last_mutation_id-" + neuprint_server + "-" + dataset + ".txt"
    debug_file = "neuprint_neuron_update-" + neuprint_server + "-" + dataset + ".log"
    log_file = "segmentation-kafka-" + dvid_uuid + "-" + neuprint_server + "-" + dataset + ".log"

    dvid_server = "emdata6.int.janelia.org:9000"
    ns = DVIDNodeService(dvid_server, dvid_uuid, 'flyem', 'update_neuprint_neurons')

    mutList = open(log_mutation_file,'r')
    last_run_mutation_id = 0
    for line in mutList:
        last_run_mutation_id = int(line.rstrip('\n'))
    log_mutation_id_msg = "Last Mutation ID: " + str(last_run_mutation_id)
    log_debug_message(debug_file,log_mutation_id_msg)

    start = time.time()
    this_pid = os.getpid()
    #enable_auto_commit=False,
    group_id_name = "cns_synapses_mutations_kafka_neuprint_" + str(this_pid)
    print("GroupID:", group_id_name)

    consumer = KafkaConsumer(bootstrap_servers=['kafka.int.janelia.org:9092','kafka2.int.janelia.org:9092','kafka3.int.janelia.org:9092'],
                             group_id=group_id_name,
                             enable_auto_commit=False,
                             auto_offset_reset='earliest')

    dvid_sub_list = ['cns3dvidrepo-f3969dc575d74e4f922a8966709958c8-data-cec65cb1382d4a0f9f24cfb3dd9f493a']

    start = time.time()
    consumer.subscribe(dvid_sub_list)

    merge_count = 0
    split_count = 0
    mutation_count = 0
    for message in consumer:
        #print("LOG ENTRY:", message.value)
        mutation_log = json.loads(message.value)
        action = mutation_log["Action"]
        if action == "element-post":
            continue
        if action == "element-delete":
            continue
        
        #if mutation_log["UUID"] == dvid_uuid:
        #print("LOG ENTRY:", message.value)
        #this_dvid_server = dvid_servers[message.topic]
        #this_synapse_annot = dvid_body_annot[message.topic]
        if "MutationID" in mutation_log:
            mutation_log_str = json.dumps(mutation_log)
            mutation_id = mutation_log["MutationID"]
            mutation_uuid = mutation_log["UUID"]
            uniq_mutation_id = mutation_uuid + "_" + str(mutation_id)

            if mutation_id <= last_run_mutation_id:
                skip_msg = "Skipping MutationID: " + str(mutation_id) + ", already processed"
                print(skip_msg)
                log_debug_message(debug_file,skip_msg)
                continue
                
            mutation_count += 1
            log_fh = open(log_file,'a')
            log_fh.write(mutation_log_str + "\n")
            log_fh.close()


            if "Delta"in mutation_log:
                delta = mutation_log["Delta"]
            else:
                print("Delta not found", mutation_log_str)
                continue

            if delta is None:
                print("Delta returned empty", mutation_log_str)
                continue
                                    
            add_data = delta["Add"]
            add_labels = {}
            add_synapse_list = []
            for add_syn in add_data:
                if add_syn is not None:
                    add_label_id = add_syn["Label"]
                    add_labels[add_label_id] = 1
                    add_syn_pos = tuple(add_syn["Pos"])
                    add_synapse_list.append(add_syn_pos)

            del_labels = {}
            del_synapse_list = []
            del_data = delta["Del"]
            for del_syn in del_data:
                if del_syn is not None:
                    del_label_id = del_syn["Label"]
                    del_labels[del_label_id] = 1
                    del_syn_pos = tuple(del_syn["Pos"])
                    del_synapse_list.append(del_syn_pos)

            add_labels_list = list(add_labels.keys())
            del_labels_list = list(del_labels.keys())

            if action == "merge":
                merge_count += 1
                target_neuron = add_labels_list[0]
                target_list = []
                target_list.append(int(target_neuron))
                #merge_neurons = target_list + del_labels_list

                debug = "Mutation ID " + str(mutation_id) + " Merge bodies " + str(del_labels_list) + " into " + str(target_neuron) + " Add Syn "+ str(add_synapse_list)
                print(debug)
                log_debug_message(debug_file,debug)

                check_targetID = check_neuron_exists_neuprint(np_client, "cns_Segment", target_neuron)
                if check_targetID == 0:
                    merge_neurons = del_labels_list
                    update_neuron = {}
                    update_neuron["bodyId"] = int(target_neuron)
                    new_target_neuron = del_labels_list[0]
                    new_size = get_body_size(ns,target_neuron)
                    log_size = str(target_neuron) + " size " + str(new_size)
                    log_debug_message(debug_file,log_size)
                    if new_size > 0:
                        update_neuron["size"] = new_size
                    if len(del_labels_list) > 1:
                        retry_toggle = 0
                        try:
                            debug = "Merge del_labels_list: " + str(del_labels_list) + ", Change bodyID: " + str(new_target_neuron) + " to " + str(update_neuron)
                            log_debug_message(debug_file,debug)
                            start = time.time()
                            updater.merge_segments(merge_neurons, debug=False)
                            updater.update_segment_properties(new_target_neuron, update_neuron, debug=False)
                            time_to_run = time.time() - start
                            log_time = "Time to run merge: " + str(time_to_run)
                            log_debug_message(debug_file,log_time)
                            test_performance(np_client,debug_file)
                            log_mutation_id(log_mutation_file,mutation_id)
                            last_run_mutation_id = mutation_id
                            update_mutationId(dataset,mutation_id)
                        except Exception as ex:
                            print("Merge A Error:",str(ex))
                            #sys.exit()
                    elif len(del_labels_list) == 1:
                        # just update the bodyId
                        try:
                            debug = "Change bodyID:" + str(new_target_neuron) + " to " + str(update_neuron)
                            log_debug_message(debug_file,debug)
                            start = time.time()
                            updater.update_segment_properties(new_target_neuron, update_neuron, debug=False)
                            time_to_run = time.time() - start
                            log_time = "Time to run update body: " + str(time_to_run)
                            log_debug_message(debug_file,log_time)
                            test_performance(np_client,debug_file)
                            log_mutation_id(log_mutation_file,mutation_id)
                            last_run_mutation_id = mutation_id
                            update_mutationId(dataset,mutation_id)
                        except Exception as ex:
                            print("Merge B Error:",str(ex))
                            #sys.exit()
                else:
                    merge_neurons = target_list + del_labels_list
                    retry_toggle = 0
                    try:
                        debug = "Merging:" + str(merge_neurons) + " mutationID: " +  str(mutation_id)
                        log_debug_message(debug_file,debug)
                        start = time.time()
                        updater.merge_segments(merge_neurons, debug=False)
                        time_to_run = time.time() - start
                        log_time = "Time to run merge: " + str(time_to_run)
                        log_debug_message(debug_file,log_time)
                        test_performance(np_client,debug_file)
                        log_mutation_id(log_mutation_file,mutation_id)
                        last_run_mutation_id = mutation_id
                        update_mutationId(dataset,mutation_id)
                    except Exception as ex:
                        print("Merge C Error:",str(ex))
                        #sys.exit()

            elif action == "cleave":
                split_count += 1
                new_neuron_id = int(add_labels_list[0])
                cleave_from_neuron = int(del_labels_list[0])
                #print("Cleave", new_neuron_id, "from target", cleave_from_neuron, "give it these synapses", add_synapse_list)
                new_neuron_props = {}
                new_neuron_props["bodyId"] = new_neuron_id
                new_neuron_props["status"] = "Assign"
                new_neuron_props["statusLabel"] = "0.5assign"
                new_neuron_props["instance"] = None
                new_neuron_props["type"] = None
                
                new_size = get_body_size(ns,new_neuron_id)
                log_size = str(new_neuron_id) + " size " + str(new_size)
                log_debug_message(debug_file,log_size)
                new_target_size = get_body_size(ns,cleave_from_neuron)
                if new_size > 0:
                    new_neuron_props["size"] = new_size
                try:
                    debug = "Cleave from neuron target: " + str(cleave_from_neuron) + " Add Syns: " + str(add_synapse_list) + " new_neuron_props " + str(new_neuron_props)
                    print(debug)
                    log_debug_message(debug_file,debug)
                    start = time.time()
                    updater.split_segment(cleave_from_neuron, add_synapse_list, new_neuron_props, debug=False)
                    time_to_run = time.time() - start
                    log_time = "Time to run cleave: " + str(time_to_run)
                    log_debug_message(debug_file,log_time)
                    log_mutation_id(log_mutation_file,mutation_id)
                    test_performance(np_client,debug_file)
                    last_run_mutation_id = mutation_id
                    update_mutationId(dataset,mutation_id)
                    if new_target_size > 0:
                        update_target = {}
                        update_target['size'] = int(new_target_size)
                        updater.update_segment_properties(cleave_from_neuron, update_target, debug=False)
                except Exception as ex:
                    print("Cleaving Error:",str(ex))
                    #sys.exit()

            elif action == "split":
                split_count += 1
                new_neuron_id = int(add_labels_list[0])
                cleave_from_neuron = int(del_labels_list[0])
                #print("Split", new_neuron_id, "from target", cleave_from_neuron, "give it these synapses", add_synapse_list)
                new_neuron_props = {}
                new_neuron_props["bodyId"] = new_neuron_id
                new_neuron_props["status"] = "Assign"
                new_neuron_props["statusLabel"] = "0.5assign"
                new_neuron_props["instance"] = None
                new_neuron_props["type"] = None
                
                new_size = get_body_size(ns,new_neuron_id)
                log_size = str(new_neuron_id) + " size " + str(new_size)
                log_debug_message(debug_file,log_size)
                new_target_size = get_body_size(ns,cleave_from_neuron)
                if new_size > 0:
                    new_neuron_props["size"] = new_size
                try:
                    debug = "Split from neuron target: " + str(cleave_from_neuron) + "Add Syns: " + str(add_synapse_list) + " new_neuron_props " + str(new_neuron_props)
                    print(debug)
                    log_debug_message(debug_file,debug)
                    start = time.time()
                    updater.split_segment(cleave_from_neuron, add_synapse_list, new_neuron_props, debug=False)
                    time_to_run = time.time() - start
                    log_time = "Time to run split: " + str(time_to_run)
                    log_debug_message(debug_file,log_time)
                    test_performance(np_client,debug_file)
                    log_mutation_id(log_mutation_file,mutation_id)
                    last_run_mutation_id = mutation_id
                    update_mutationId(dataset,mutation_id)
                    if new_target_size > 0:
                        update_target = {}
                        update_target['size'] = int(new_target_size)
                        updater.update_segment_properties(cleave_from_neuron, update_target, debug=False)
                except Exception as ex:
                    print("Split Error:",str(ex))
                    #sys.exit()

