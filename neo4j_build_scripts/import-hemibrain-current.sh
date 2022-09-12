#!/bin/bash

UUID=$1
#EXPORT_BASE_DIR=/groups/flyem/data/neuprint_exports
#EXPORT_DIR=/mb6
EXPORT_BASE_DIR=/groups/flyem/data/neuprint_exports/syn_base_v5f
EXPORT_DIR=/neuprint_imports_csv_${UUID}
#EXPORT_DIR=/neuprint_imports_csv_20631_v1.1

NEO4J_DIR=/opt/neo4j
IMPORT_BASE_DIR=/opt/neo4j/import

NEO4J_DB=${UUID}_0_9_0_b.db
#NEO4J_DB=${UUID}_mito_7.db

META_NODE_CMD="--nodes=import/Neuprint_Meta_${UUID}.csv"

#MITO_NODE_CMD="--nodes=import/Neuprint_Mitochondria_${UUID}.csv"
#MITOSET_NODE_CMD="--nodes=import/Neuprint_MitoSet_${UUID}.csv"
#MITO_REL_CMD="--relationships:Contains=import/Neuprint_Neuron_to_MitoSet_${UUID}.csv"
#MITOSET_REL_CMD="--relationships:Contains=import/Neuprint_MitoSet_to_Mito_${UUID}.csv"
#MITOSYNSET_REL_CMD="--relationships:CloseTo=import/Neuprint_Synapses_to_Mito_${UUID}.csv"


NEURON_NODE_CMD="--nodes=import/Neuprint_Neurons_${UUID}.csv"
NEURON_REL_CMD="--relationships:ConnectsTo=import/Neuprint_Neuron_Connections_${UUID}.csv"

SYNSET_NODE_CMD="--nodes=import/Neuprint_SynapseSet_${UUID}.csv"
SYNSET_REL_CMD="--relationships:ConnectsTo=import/Neuprint_SynapseSet_to_SynapseSet_${UUID}.csv --relationships:Contains=import/Neuprint_Neuron_to_SynapseSet_${UUID}.csv"

SYNAPSE_NODE_CMD="--nodes=import/Neuprint_Synapses_${UUID}.csv"
SYNAPSE_REL_CMD="--relationships:SynapsesTo=import/Neuprint_Synapse_Connections_${UUID}.csv --relationships:Contains=import/Neuprint_SynapseSet_to_Synapses_${UUID}.csv"

ROI_NODE_CMD="--nodes=import/Neuprint_ROIs_${UUID}.csv"
ROI_REL_CMD="--relationships:FoundIn=import/Neuprint_Neuron_ROI_${UUID}.csv --relationships:SynFoundIn=import/Neuprint_SynapseSet_ROI_${UUID}.csv"


echo "................"
echo "cp files"
echo "................"
date
cp ${EXPORT_BASE_DIR}${EXPORT_DIR}/Neuprint*${UUID}.csv ${IMPORT_BASE_DIR}
date
cd ${NEO4J_DIR}
echo "................"
echo "import data"
echo "................"
date
pwd

/var/lib/neo4j/bin/neo4j-admin import --database=${NEO4J_DB} ${META_NODE_CMD} ${NEURON_NODE_CMD} ${NEURON_REL_CMD} ${SYNSET_NODE_CMD} ${SYNSET_REL_CMD} ${SYNAPSE_NODE_CMD} ${SYNAPSE_REL_CMD}

#sudo -s -u neo4j ./bin/neo4j-admin import --database=${NEO4J_DB} ${META_NODE_CMD} ${NEURON_NODE_CMD} ${NEURON_REL_CMD} ${SYNSET_NODE_CMD} ${SYNSET_REL_CMD} ${SYNAPSE_NODE_CMD} ${SYNAPSE_REL_CMD} ${MITO_NODE_CMD} ${MITOSET_NODE_CMD} ${MITO_REL_CMD} ${MITOSET_REL_CMD} ${MITOSYNSET_REL_CMD}

date

##echo "................"
##echo "clean copy"
##echo "................"
##cp -R /data/db/neo4j/databases/${NEO4J_DB} /data/db/neo4j/databases/${NEO4J_DB}.copy

#Load neo4j
#echo "................"
#echo "stop neo4j"
#echo "................"
#sudo -u neo4j ./bin/neo4j status
#sudo -u neo4j ./bin/neo4j stop
#sleep 60
#sudo -u neo4j ./bin/neo4j status
#rm -rf /data/db/neo4j/databases/graph.db
#ln -s  /data/db/neo4j/databases/${NEO4J_DB} /data/db/neo4j/databases/graph.db
#sudo -u neo4j ./bin/neo4j start
#sleep 90
#sudo -u neo4j ./bin/neo4j status
#echo "................"
#echo "build indices"
#echo "................"
#date
#cat /opt/neo4j-scripts/index-hemibrain.cypher | sudo -u neo4j ./bin/cypher-shell -u neo4j -p n304jT35t --format plain
#date
#echo "warmup cache"
#echo "................"
#date
#cat /opt/neo4j-scripts/warmup-cache.cypher | sudo -u neo4j ./bin/cypher-shell -u neo4j -p n304jT35t --format plain
#echo "................"
#echo "done!"

## sudo -u neo4j ./bin/neo4j-admin import --database=dd7b7_roi_6.db --nodes="import/Neuprint_Neurons_roiInfo_dd7b7.csv" --relationships:ConnectsTo="import/Neuprint_Neuron_Connections_roiInfo_dd7b7.csv" --nodes="import/Neuprint_SynapseSet_roiInfo_dd7b7.csv" --relationships:ConnectsTo="import/Neuprint_SynapseSet_to_SynapseSet_dd7b7.csv"  --relationships:Contains="import/Neuprint_Neuron_to_SynapseSet_dd7b7.csv"  --nodes="import/Neuprint_Synapses_dd7b7.csv"  --relationships:SynapsesTo="import/Neuprint_Synapse_Connections_dd7b7.csv"  --relationships:Contains="import/Neuprint_SynapseSet_to_Synapses_dd7b7.csv"  --nodes:ROI="import/Neuprint_roiInfo_dd7b7.csv"  --relationships:FoundIn="import/Neuprint_Neuron_ROI_dd7b7.csv"  --relationships:SynFoundIn="import/Neuprint_SynapseSet_ROI_dd7b7.csv" 
