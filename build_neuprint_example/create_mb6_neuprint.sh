
python generate_Synapse_Connections_All_ftr.py mb6_synapse_data_example.ftr mb6_synapse_connections_example.ftr > All_Neuprint_Synapse_Connections_mb6.csv

python ../dvid_to_neuprint/detect_downstream_synapses.py All_Neuprint_Synapse_Connections_mb6.csv > downstream_synapses.csv

python ../dvid_to_neuprint/detect_downstream_roiInfo.py All_Neuprint_Synapse_Connections_mb6.csv > downstream_synapses_roiInfo.csv

# Create Synapse csv
python generate_Neuprint_Synapses_ftr.py mb6_synapse_data_example.ftr mushroombody all_ROIs.txt > Neuprint_Synapses_mb6.csv

# Create Synapse Connections csv
python ../dvid_to_neuprint/generate_Synapse_Connections.py All_Neuprint_Synapse_Connections_mb6.csv > Neuprint_Synapse_Connections_mb6.csv

# generate Neurons connections file
python ../dvid_to_neuprint/generate_Neuron_connections.py All_Neuprint_Synapse_Connections_mb6.csv 0.5 0.5 > Neuprint_Neuron_Connections_mb6.csv

# generate Synapse Set file
python ../dvid_to_neuprint/generate_SynapseSet_to_SynapseSet.py All_Neuprint_Synapse_Connections_mb6.csv > Neuprint_SynapseSet_to_Synapses_mb6.csv

# generate Synapse Set collection
python ../dvid_to_neuprint/generate_SynapseSets.py All_Neuprint_Synapse_Connections_mb6.csv mushroombody > Neuprint_SynapseSet_mb6.csv

# generate Neuron to Synapse Set
python ../dvid_to_neuprint/generate_Neuron_to_SynapseSet.py All_Neuprint_Synapse_Connections_mb6.csv > Neuprint_Neuron_to_SynapseSet_mb6.csv

# generate Synapse Set to Synapse Set
python ../dvid_to_neuprint/generate_SynapseSet_to_SynapseSet.py All_Neuprint_Synapse_Connections_mb6.csv > Neuprint_SynapseSet_to_SynapseSet_mb6.csv

# generate roiInfo, pre, post counts
python generate_Neurons_roiInfo_ftr.py mb6_synapse_data_example.ftr > synapse_bodies_mb6.csv

# generate Neurons
python generate_Neurons_ftr.py synapse_bodies_mb6.csv mb6_neuron_data_example.ftr neurons.yaml > Neuprint_Neurons_mb6.csv

# generate Neuprint Meta
python generate_Neuprint_Meta_ftr.py mb6_synapse_data_example.ftr meta.yaml > Neuprint_Meta_mb6.csv

./neo4j_3_5_import.sh mb6

cat index-mb6.cypher | ./bin/cypher-shell -u neo4j  --format plain
cat warmup-cache.cypher | ./bin/cypher-shell -u neo4j  --format plain
