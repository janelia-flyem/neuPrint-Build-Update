#!/bin/env
# ------------------------- imports -------------------------
import json
import sys
import os
import io
import time
import numpy as np
from tqdm import trange
from neuclease.dvid import *
import incremental_update_test as up

def write_annots (annotfile, annots):
    annotfile_fh = open(annotfile,'w')
    annotfile_fh.write(str(annots))
    annotfile_fh.close()

if __name__ == '__main__':
    dvid_server = "emdata6.int.janelia.org:9000"
    keyvalue = "segmentation_annotations"
    master_uuid = "f3969"

    neuprint_server = "neuprint-cns.janelia.org"
    dataset_name = "cns"
    updater = up.NeuPrintUpdater(neuprint_server, dataset_name, verify=False)
    
    dvid_uuid = find_master(dvid_server,master_uuid)
    print("Using uuid:", dvid_uuid)
    this_pid = os.getpid()
    node = (dvid_server, dvid_uuid)
    all_keys = fetch_keys(*node, keyvalue)
    seg_annot_count = len(all_keys)

    all_values = fetch_keyvalues(*node, keyvalue, all_keys, as_json=True)

    previous_cns_annot = "previous_cns_annotations.txt"
    backup = "previous_cns_annotations.bak." + str(this_pid)
    bak_cmd = "cp " + previous_cns_annot + " " + backup
    os.system(bak_cmd)
    check_annot = {}
    annotList = open(previous_cns_annot,'r')
    
    for line in annotList:
        clean_line = line.rstrip('\n')
        annot_data = clean_line.split("~~~~~")
        body_id = annot_data[0]
        annot_entry = annot_data[1]
        check_annot[body_id] = annot_entry
    
    out_str = ""

    for bodyId in all_values:
        try:
        #int(bodyId)
            annot_data_dvid = all_values[bodyId]
            update_neuprint_neuron = {}

            if 'group' in annot_data_dvid:
                neuronGroup = annot_data_dvid['group']
                update_neuprint_neuron['group'] = int(neuronGroup)
            else:
                update_neuprint_neuron['group'] = None
            
            if 'cell body fiber' in annot_data_dvid:
                cellBodyFiber_val = annot_data_dvid['cell body fiber']
                update_neuprint_neuron['cellBodyFiber'] = cellBodyFiber_val
            else:
                update_neuprint_neuron['cellBodyFiber'] = None

            if 'synonym' in annot_data_dvid:
                synonym_val = annot_data_dvid['synonym']
                update_neuprint_neuron['notes'] = synonym_val
            else:
                update_neuprint_neuron['notes'] = None

            if 'class' in annot_data_dvid:
                type_class = annot_data_dvid['class']
                update_neuprint_neuron['type'] = type_class
                #temp change status
                if len(type_class) > 0:
                    update_neuprint_neuron['status'] = "Anchor"
                    update_neuprint_neuron['statusLabel'] = "Anchor"
                    update_neuprint_neuron['cropped'] = False
            else:
                update_neuprint_neuron['type'] = None

            if 'type' in annot_data_dvid:
                type_type = annot_data_dvid['type']
                update_neuprint_neuron['type'] = type_type
                #temp change status
                if len(type_type) > 0:
                    update_neuprint_neuron['status'] = "Anchor"
                    update_neuprint_neuron['statusLabel'] = "Anchor"
                    update_neuprint_neuron['cropped'] = False
            else:
                update_neuprint_neuron['type'] = None
                
            if 'instance' in annot_data_dvid:
                instance_val = annot_data_dvid['instance']
                update_neuprint_neuron['instance'] = instance_val
            else:
                update_neuprint_neuron['instance'] = None

            check_bodyId = 0
            if 'status' in annot_data_dvid:
                status_dvid = annot_data_dvid['status']
                update_neuprint_neuron['status'] = status_dvid
                update_neuprint_neuron['statusLabel'] = status_dvid
            
                if status_dvid == "Traced":
                    update_neuprint_neuron['status'] = status_dvid
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = False
                    check_bodyId = 1
                if "traced" in status_dvid:
                    update_neuprint_neuron['status'] = "Traced"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = False
                    check_bodyId = 1
                if status_dvid == "Leaves":
                    update_neuprint_neuron['status'] = "Traced"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = True
                    check_bodyId = 1
                if status_dvid == "Anchor":
                    update_neuprint_neuron['status'] = "Anchor"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = False
                    check_bodyId = 1
                if status_dvid == "Cleaved Anchor":
                    update_neuprint_neuron['status'] = "Anchor"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = False
                    check_bodyId = 1
                if status_dvid == "Soma Anchor":
                    update_neuprint_neuron['status'] = "Anchor"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = False
                    check_bodyId = 1
                if status_dvid == "Sensory Anchor":
                    update_neuprint_neuron['status'] = "Anchor"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = False
                    check_bodyId = 1
                if status_dvid == "Primary Anchor":
                    update_neuprint_neuron['status'] = "Anchor"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    update_neuprint_neuron['cropped'] = False
                    check_bodyId = 1
                if status_dvid == "Orphan hotknife":
                    update_neuprint_neuron['status'] = "Orphan"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    check_bodyId = 1
                if status_dvid == "Orphan-artifact":
                    update_neuprint_neuron['status'] = "Orphan"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    check_bodyId = 1
                if status_dvid == "0.1assign":
                    update_neuprint_neuron['status'] = "Assign"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                if status_dvid == "0.5assign":
                    update_neuprint_neuron['status'] = "Assign"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                if status_dvid == "Orphan":
                    update_neuprint_neuron['status'] = "Orphan"
                    update_neuprint_neuron['statusLabel'] = status_dvid
                    check_bodyId = 1
        except Exception as ex:
            print (str(ex))
            continue
            
        str_annot_data = json.dumps(annot_data_dvid)
        out_str += bodyId + "~~~~~" + str_annot_data + "\n"
        if bodyId in check_annot:
            prev_annot = check_annot[bodyId]
            if prev_annot != str_annot_data:
                print("Detect Change:", bodyId, str_annot_data)
                str_update = json.dumps(update_neuprint_neuron)
                print("Push Update:", bodyId, str_update)
                try:
                    updater.update_segment_properties(int(bodyId), update_neuprint_neuron, debug=False)
                except Exception as ex:
                    print("Neuprint Update Error:",str(ex), bodyId)
                    continue
        else:
            print("New Entry:", bodyId, str_annot_data)
            str_update = json.dumps(update_neuprint_neuron)
            print("Update New:", bodyId, str_update)
            try:
                updater.update_segment_properties(int(bodyId), update_neuprint_neuron, debug=False)
            except Exception as ex:
                print("Neuprint Update Error:",str(ex), bodyId)
                continue

            
    #update annot cache
    write_annots(previous_cns_annot,out_str)
    
