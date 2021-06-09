pip3 install --upgrade -e ."[dev]"

#snudda input 10000Sim_input --input snudda/data/input_config/1w_input_100n_50Hz.json --position_file ./10000Sim_input/network-neuron-positions.hdf5 --network_path ./10000Sim_input/ --network_config ./10000Sim_input/network-config.json

#nrnivmodl -coreneuron snudda/data/neurons/mechanisms_nochin/

mpiexec -np 8 ./x86_64/special -mpi -python ./snudda/simulate/simulate.py 10000Sim_input/network-synapses.hdf5 10000Sim_input/input-spikes.hdf5  --time 0.4 --voltOut ./10000Sim_input/simulation/volt.txt  --distributePolicy RoundRobin --configFile 10000Sim_input/network-config.json --recordMode all --disableGJ --coreneuron --gpu
