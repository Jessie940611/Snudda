# python3 Network_plot_traces.py save/traces/network-voltage-0.csv save/network-connect-synapse-file-0.hdf5


import sys
import os
import numpy as np
from snudda.load import SnuddaLoad
import re
import ntpath
import time

class ComparePlotTraces():

  ############################################################################
  
  def __init__(self,fileNameOne,fileNameTwo,networkFileOne=None,networkFileTwo=None):
      
    self.fileNameOne = fileName
    self.networkFileOne = networkFile

    self.fileNameTwo = fileName
    self.networkFileTwo = networkFile

    self.timeOne = []
    self.voltageOne = dict([])

    self.timeTwo = []
    self.voltageTwo = dict([])

    self.neuronNameRemap = {"FSN" : "FS"}
    
    self.readCSV()

    try:
      self.ID = int(re.findall('\d+', ntpath.basename(fileName))[0])
    except:
      print("Unable to guess ID, using 666.")
      self.ID = 666

    if(self.networkFile is not None):
      self.networkInfoOne = SnuddaLoad(self.networkFileOne)
      self.networkInfoTwo = SnuddaLoad(self.networkFileTwo)
      # assert(int(self.ID) == int(self.networkInfo.data["SlurmID"]))
   
    else:
      self.networkInfo = None
    

  ############################################################################
    
  def readCSV(self):

    dataOne = np.genfromtxt(self.fileNameOne, delimiter=',')

    assert(dataOne[0,0] == -1) # First column should be time

    self.timeOne = dataOne[0,1:] / 1e3

    self.voltageOne = dict()
    
    for rows in dataOne[1:,:]:
      cID = int(rows[0])
      self.voltageOne[cID] = rows[1:] * 1e-3
    
    dataTwo = np.genfromtxt(self.fileNameTwo, delimiter=',')

    assert(data[0,0] == -1) # First column should be time

    self.timeTwo = dataTwo[0,1:] / 1e3

    self.voltageTwo = dict()
    
    for rows in dataTwo[1:,:]:
      cID = int(rows[0])
      self.voltageTwo[cID] = rows[1:] * 1e-3

  ############################################################################

  def neuronName(self,neuronType):

    if(neuronType in self.neuronNameRemap):
      return self.neuronNameRemap[neuronType]
    else:
      return neuronType

  ############################################################################
  
  
  def plotTraces(self,traceID=None,offset=150e-3,colours=None,skipTime=None,
                 title=None):

    if(skipTime is not None):
      print("!!! Excluding first " + str(skipTime) + "s from the plot")
    
    if(colours is None):
      colours = {"dSPN" : (77./255,151./255,1.0),
                 "iSPN" : (67./255,55./255,181./255),
                 "FSN" : (6./255,31./255,85./255),
                 "ChIN" : [252./255,102./255,0],
                 "LTS" : [150./255,63./255,212./255]}
    
    print("Plotting traces: " + str(traceID))
    print("Plotted " + str(len(traceID)) + " traces (total " \
      + str(len(self.voltage)) + ")")
      
    import matplotlib.pyplot as plt

    typesInPlot = set()
    
    if(self.networkInfo is not None):
      cellTypesOne = [n["type"] for n in self.networkInfoOne.data["neurons"]]
      cellIDcheckOne = [n["neuronID"] for n in self.networkInfoOne.data["neurons"]]

      cellTypesTwo = [n["type"] for n in self.networkInfoTwo.data["neurons"]]
      cellIDcheckTwo = [n["neuronID"] for n in self.networkInfoTwo.data["neurons"]]
      try:
        assert (np.array([cellIDcheck[x] == x for x in traceID])).all(), \
          "Internal error, assume IDs ordered"
      except:
        import traceback
        tstr = traceback.format_exc()
        print(tstr)
        print("This is strange...")
        import pdb
        pdb.set_trace()
      
      cols = [colours[c] if c in colours else [0,0,0] for c in cellTypes]
    
    #import pdb
    #pdb.set_trace()
    
    fig = plt.figure()
    
    ofs = 0

    if(skipTime is not None):
      timeIdxOne = np.where(self.timeOne >= skipTime)[0]
      timeIdxTwo = np.where(self.timeTwo >= skipTime)[0]
    else:
      skipTime = 0.0
      timeIdx = range(0,len(self.time))

    plotCount = 0
    
    for r in traceID:

      if(r not in self.voltage):
        print("Missing data for trace " + str(r))
        continue


      plotCount += 1
      typesInPlot.add(self.networkInfoOne.data["neurons"][r]["type"])
      typesInPlot.add(self.networkInfoTwo.data["neurons"][r]["type"])
      if(colours is None or self.networkInfoOne is None):
        colour = "black"
      else:
        try:
          colour = cols[r]
        except:
          import traceback
          tstr = traceback.format_exc()
          print(tstr)
          import pdb
          pdb.set_trace()
          
        
      plt.plot(self.time[timeIdx]-skipTime,
               self.voltageOne[r][timeIdx] + ofs,
               color=colour)

      plt.plot(self.time[timeIdx]-skipTime,
               self.voltageTwo[r][timeIdx] + ofs,
               color=colour)

      ofs += offset


    if(plotCount == 0):
      plt.close()
      return
      
    plt.xlabel('Time')
    plt.ylabel('Voltage')

    if(title is not None):
      plt.title(title)
    
    if(offset != 0):
      ax = fig.axes[0]
      ax.set_yticklabels([])

    plt.tight_layout()
    plt.ion()
    plt.show()
    plt.draw()
    plt.pause(0.001)

    #plt.savefig('figures/Network-spikes-' + str(self.ID) + "-colour.pdf")

    figPath = os.path.dirname(self.networkFile) + "/figs"
    if(not os.path.exists(figPath)):
      os.makedirs(figPath)
 
    
    
    if(len(typesInPlot) > 1):
      figName = figPath + '/Network-spikes-' + str(self.ID) \
        + "-".join(typesInPlot) + "-colour.png"
    else:
      figName = figPath + '/Network-spikes-' + str(self.ID) \
        + "-" + typesInPlot.pop() + "-colour.png"
      
    plt.savefig(figName,
                dpi=300)
    print("Saving to figure " + str(figName))


  ############################################################################

  def plotTraceNeuronType(self,neuronType,nTraces=10,offset=0,skipTime=0.0):

    assert self.networkInfo is not None, "You need to specify networkInfo file"
    
    neuronTypesOne = [x["type"] for x in self.networkInfoOne.data["neurons"]]

    neuronTypesTwo = [x["type"] for x in self.networkInfoTwo.data["neurons"]]
    # Find numbers of the relevant neurons
    
    traceIDOne = [x[0] for x in enumerate(neuronTypesOne) if x[1] == neuronType]
    
    traceIDTwo = [x[0] for x in enumerate(neuronTypesTwo) if x[1] == neuronType]

    nTracesOne = min(len(traceIDOne),nTraces)

    nTracesTwo = min(len(traceIDTwo),nTraces)

    if(nTraces <= 0):
      print("No traces of " + str(neuronType) + " to show")
      return
    
    self.plotTraces(offset=offset,traceID=traceID[:nTraces],skipTime=skipTime,
                    title=self.neuronName(neuronType))

                                   
    time.sleep(1)
    
  ############################################################################
    
if __name__ == "__main__":

  if(len(sys.argv) > 1):
    fileName = sys.argv[1]

  if(len(sys.argv) > 2):
    networkFile = sys.argv[2]
  else:
    networkFile = None

  if(fileName is not None):
    npt = NetworkPlotTraces(fileName,networkFile)
    #npt.plotTraces(offset=0.2,traceID=[17,40,11,18])
    # npt.plotTraces(offset=0.2,traceID=[0,1,2,3,4,5,6,7,8,9])
    # npt.plotTraces(offset=0,traceID=[0,1,2,3,4,5,6,7,8,9])
    # npt.plotTraces(offset=0,traceID=[0,5,55]) #,5,55])
    #npt.plotTraces(offset=0,traceID=np.arange(0,100)) #,5,55])
    #npt.plotTraces(offset=-0.2,traceID=np.arange(0,20),skipTime=0.5)
    #npt.plotTraces(offset=-0.2,traceID=[5,54],skipTime=0.5)    
    #npt.plotTraces(offset=0.2,traceID=[1,5,7,15,16],skipTime=0.2)

    plotOffset = 0 # -0.2
    skipTime = 0 #0.5
    nTracesMax = 5
    
    npt.plotTraceNeuronType(neuronType="dSPN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
    npt.plotTraceNeuronType(neuronType="iSPN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
    npt.plotTraceNeuronType(neuronType="FSN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
    npt.plotTraceNeuronType(neuronType="LTS",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
    npt.plotTraceNeuronType(neuronType="ChIN",nTraces=nTracesMax,offset=plotOffset,skipTime=skipTime)
    
    
    
  else:
    print("Usage: " + sys.argv[0] + " network-voltage-XXX.csv")
    
  #import pdb
  #pdb.set_trace()
