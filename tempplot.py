
from snudda.plotting.Compare_plot_traces import ComparePlotTraces
from snudda.plotting.Network_plot_traces import NetworkPlotTraces

networkFile = "SNcVirtualAxon/network-pruned-synapses.hdf5"
fileName = "SNcVirtualAxon/simulation/volt-DA.csv"

DopamineNetwork = NetworkPlotTraces(fileName,networkFile)

plotOffset = 0 
skipTime = 0 
nTracesMax = 100

DopamineNetwork.plotTraceNeuronType(neuronType="dSPN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
DopamineNetwork.plotTraceNeuronType(neuronType="iSPN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)



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
