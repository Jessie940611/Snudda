path = "./1000neuron_10Hz_focus.json"

with open(path, 'r') as f:
    data = f.readlines()[121:132]

data0 = data[0]

with open(path, 'a') as f:
    for i in range(1,1000,1):
        f.writelines('\n')
        data[0] = data0.replace("0", str(i))
        f.writelines(data)
