Create neuPrint from flat files (feather) using mushroombody (MB6) as an example
=====
An example of the data and format you data needs to be in to import your connectome data into a neuprint neo4j database

## Prerequisite Python Libraries
To run these scripts you will need to install the following python packages and Python 3.7 or greater::
* [pandas](https://pandas.pydata.org/)

## Example feather (ftr) files for mushroombody (MB6)
* mb6_synapse_data_example.ftr - synapses data which includes unique synapse ID (synId), synapse coordinate location (x,y,z), synapse type (type), synapse confidence (confidence), segmentation/body mapping (body)
* mb6_synapse_connections_example.ftr - defines all synapse relationship from pre (synId_pre) to post (synId_post)
* mb6_neuron_data_example.ftr - neuron annotation/properties data. unique neuron ID (body), neuron annotation status (statusLabel), is neuron truncated (cropped), neuron name (instance), neuron class or type (type), neuron size ex. voxels (size)
