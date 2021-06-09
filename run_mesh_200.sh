pip3 install --upgrade -e ."[dev]"
#rm -rf network x86_64
#snudda init network --size 50
#snudda place network
#snudda detect network --hvsize 100
#snudda prune network
#snudda input network --input snudda/data/input_config/input-tinytest-v4.json
#nrnivmodl -coreneuron snudda/data/neurons/mechanisms_nochin/
#mpiexec -np 8 ./x86_64/special -mpi -python ./snudda/simulate/simulate.py network/network-putative-synapses-MERGED.hdf5 network/input-spikes.hdf5  --time 1 --voltOut network/simulation/volt.txt  --distributePolicy RoundRobin --coreneuron --gpu
mpiexec -np 8 ./x86_64/special -mpi -python ./snudda/simulate/simulate.py 200Sim/network-synapses.hdf5 200Sim/input-spikes.hdf5  --time 1 --voltOut ./200Sim/simulation/volt.txt  --distributePolicy RoundRobin --configFile 200Sim/network-config.json --recordMode all  --coreneuron --gpu
