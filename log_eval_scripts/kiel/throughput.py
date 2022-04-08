import sys
import numpy as np
import matplotlib.pyplot as plt
import math

# array with all node ids
ids = [1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10,
       12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

# store data for all
# data is indexed by data[node_id][seq_num], basically only stores the timestamps, but ordered
data = [dict() for x in range(len(ids))]

# get file location
folder = "./"

sender = 5

# get the txt file as string
enc = 'iso-8859-15'

#file = open(location, "r", encoding=enc).read()

periods = [0.1, 0.5, 1.0]
bytes   = [3, 7, 11, 15, 19]

labels = [str(x) + " Bytes" for x in bytes] #labels
x = np.arange(len(labels))  # the label locations
width = 0.2  # the width of the bars

fig, ax = plt.subplots()
rects = []
i=-1
#iterate over time
for period in periods:
    #iterate over bytes
    data = []
    for byte in bytes:
        path = "./" + "{:02d}".format(int(period*10)) + "/" + str(byte) + "/logs/"

        sent = 0
        arrived = 0
        #iterate over node id .txt
        for id in ids:
            file = open(path + "raspi" + "{:02d}".format(id) + "/log.txt", "r", encoding=enc).read()
            
            #split file into single lines
            lines = file.split("\n")

            #sender code
            if id == 5:
                substring = "Sending OnOff Set:"
                for line in lines:
                    if substring in line:
                        sent += 1
            #normal code
            else:
                substring = "seq:"
                for line in lines:
                    if substring in line:
                        arrived += 1

        #-1 because of sender node
        reliability = arrived / (sent * len(ids)-1)
        #expected throughput
        general_throughput = byte/period
        #real throughput
        actual_througput = general_throughput * reliability
        data.append(actual_througput)
    rects.append(ax.bar(x - (width)*i, data, width, label=str(period) + "seconds", align='center')) 
    i += 1


ax.set_xlabel("Amount of Bytes")
ax.set_ylabel("Throughput in Bytes per second")
ax.set_xticks(x, labels)
ax.legend()


fig.tight_layout()

plt.savefig("./throughput.png", bbox_inches='tight')
'''
#generate figure
plt.figure(figsize=(15, 10))
plt.bar(new_names, new_rel)

plt.ylim([min(80.0,math.floor(min(new_rel)-5)), 100.0])
saveloc = folder + "reliability.png"
print(saveloc)
plt.savefig(saveloc, bbox_inches='tight')
'''