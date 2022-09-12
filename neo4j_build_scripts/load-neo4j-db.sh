#!/bin/bash

UUID=$1
#EXPORT_BASE_DIR=/groups/flyem/data/neuprint_exports
#EXPORT_DIR=/mb6
EXPORT_BASE_DIR=/groups/flyem/data/neuprint_exports/syn_base_v5j
EXPORT_DIR=/neuprint_imports_csv_${UUID}
#EXPORT_DIR=/neuprint_imports_csv_52a133_1.0.1

NEO4J_DIR=/opt/neo4j
IMPORT_BASE_DIR=/opt/neo4j/import

NEO4J_DB=${UUID}.db

META_NODE_CMD="--nodes=import/Neuprint_Meta_${UUID}.csv"

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
date
echo "................"
echo "done!"

