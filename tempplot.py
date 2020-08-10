
from snudda.plotting.Compare_plot_traces import ComparePlotTraces

networkFile = "SNcVirtualAxon/network-pruned-synapses.hdf5"
fileNameDopamine = "SNcVirtualAxon/simulation/volt.csv"

networkFileDopamineReceptor = "SNcVirtualAxon/network-pruned-synapses.hdf5"
fileNameDopamineReceptor = "SNcVirtualAxon/simulation/volt-DA.csv"


fileNames = [fileNameDopamine, fileNameDopamineReceptor]
plotLabels = ['No modulation', 'Dopamine Modulation with Virtual axon']

DopamineNetwork = ComparePlotTraces(fileNames= fileNames,networkFiles = networkFile,labels=plotLabels)

plotOffset = 0 
skipTime = 0 
nTracesMax = 100

DopamineNetwork.plotTraceNeuronType(neuronType="dSPN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
DopamineNetwork.plotTraceNeuronType(neuronType="iSPN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
