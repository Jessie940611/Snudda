from os import linesep
import numpy as np
from tqdm import tqdm

input_id_cad_list = []
input_id_list = []
input_id_write_list = []

loc_file = "/home/zmd/Snudda/10000Sim_input/n_simulation_1000n_10Hz/3d_point_location.txt"
input_neuron_id_file = "/home/zmd/Snudda/10000Sim_input/simulation/input_neuron_id.txt"
input_file = "./1w_two_dense_input.json"

with open(loc_file, "r") as f:
    line = f.readlines()[9999].split(" ")
    center = np.array([float(line[0]), float(line[1]), float(line[2])])
    print("center", center)

for line in tqdm(open(loc_file, "r")):
    x,y,z,d,i,_,j,k = line.replace("\n", "").split(" ")
    if i == '-1' and j == '0':
        point = np.array([float(x), float(y), float(z)])
        dist = np.sum((point - center) ** 2) ** 0.5
        input_id_cad_list.append([float(k), float(dist)])

input_id_cad_list = np.array(input_id_cad_list, dtype=float)

print(len(input_id_cad_list))

for i in range(20):
    print(input_id_cad_list[i])

input_id_cad_list = input_id_cad_list[np.lexsort(input_id_cad_list.T)]

print(len(input_id_cad_list))
for i in range(20):
    print(input_id_cad_list[i])


for i in range(500):
    input_id_list.append(int(input_id_cad_list[i][0]))
    input_id_write_list.append(str(int(input_id_cad_list[i][0])) + "\n")

with open(input_neuron_id_file,"a") as f:
    f.writelines(input_id_write_list)

print(input_id_list)



with open(input_file, 'r') as f:
    data = f.readlines()[170:181]

data0 = data[0]

with open(input_file, 'a') as f:
    for i in tqdm(input_id_list):
        f.writelines('\n')
        data[0] = data0.replace("0", str(i))
        f.writelines(data)
