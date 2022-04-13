import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import math

#get median of list
def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (s[n//2-1]/2.0+s[n//2]/2.0, s[n//2])[n % 2] if n else None

#timestamp format
fmt = '%Y-%m-%d %H:%M:%S.%f'

# array with all node ids
ids = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
       110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
       200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 
       210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 
       220, 221, 222, 223, 224, 225, 226, 227]

# check if there is one argument
if not(len(sys.argv) == 4):
    print('usage: log_eval <location to folder> <sender node_id> <iterations>')
    exit()

# get file location
folder = str(sys.argv[1])
# get the sender nodes id
sender = int(sys.argv[2])
# get the amount of iteration
iterations = int(sys.argv[3])

# set encryption
enc = 'iso-8859-15'

# store data for all
# data is indexed by data[node_id][seq_num], basically only stores the timestamps, but ordered
data = [[dict() for x in range(len(ids))] for x in range(iterations)]

for iteration in range(iterations):

    #store max_seq
    max_seq = -1
    data_sender_id = -1

    #iterate over all node ids
    for a in range(len(ids)):
        #get real id of node
        id = ids[a]
        #build file location and read file
        location = folder + "00" + str(iteration + 1) + "/" + "log_" + str(id) + ".txt"
        file = open(location, "r", encoding=enc).read()

        # check if file was read successfully
        if len(file) < 0:
            print('File could not be read.')
            exit()

        #split file into single lines
        lines = file.split("\n")

        #differentiate substring for sender node
        if(sender == id):
            data_sender_id = a
            substring = "Sending OnOff Set:"
        else:
            substring = "seq: "

        new_lines = []
        # eliminate not needed lines from log
        for line in lines:
            
            if(sender == id):
                if substring in line:
                    new_lines.append(line)
            else:
                if substring in line:
                    new_lines.append(line)

        lines = new_lines

        #sender part
        if (sender == id):
            # iterate over the log and add every index to data
            seq = 0
            for line in lines:
                if(seq > max_seq):
                    max_seq = seq
                #split into parts
                parts = line.split("|")
                #calculate timestamp from string
                timestamp = datetime.strptime(parts[0], fmt).timestamp()
                #put into data
                data[iteration][a][seq] = timestamp
                #increment sequence number
                seq += 1
        else:
            for line in lines:
                #split into parts
                parts = line.split("|")
                #calculate timestamp from string
                timestamp = datetime.strptime(parts[0], fmt).timestamp()
                
                #get sequence number from string
                #seq = int(parts[1].split("seq:")[1].split(" ")[0])
                seq = int(parts[1].split("seq: ")[1])
                
                #put into data
                data[iteration][a][seq] = timestamp
                #increment sequence number

#compute delays
for iteration in range(iterations):
    for seq in range(max_seq+1):
        #get sender timestamp
        ts_sender = data[iteration][data_sender_id][seq]
        for a in range(len(ids)):
            if seq in data[iteration][a]:
                #multiply by 1000 for ms
                data[iteration][a][seq] = (data[iteration][a][seq] - ts_sender) * 1000

#data to be stored
latencies = [[] for x in range(len(ids))]
reliability = [x for x in range(len(ids))]
#compute latencies and reliability for each node
for a in range(len(ids)):

    latency = [] 
    arrived = 0
    
    #iterate through iterations and sequence numbers
    for it in range(iterations):
        for seq in range(max_seq + 1):
            if seq in data[it][a]:
                if data[it][a][seq] >= 0:
                    latency.append(data[it][a][seq])
                    arrived += 1

    latencies[a] = latency
    reliability[a] = (arrived/(5 * (max_seq+1)))*100

#node names
names = [str(x) for x in ids]
#order this mess
lat = latencies
new_names = []
new_lat = []
medians = []
#get median
for l in latencies:
    medians.append(np.median(l))

#median line
med_line = [np.median(medians) for x in ids]

while len(medians) > 0:
    #go thorugh medians and find smallest index
    helper = -1
    index = -1
    for i in range(0,len(medians)):
        med = medians[i]
        if med > helper:
            helper = med
            index = i
    
    #append smallest found median
    new_names.append(names[index])
    new_lat.append(lat[index])
    del medians[index]
    del names[index]
    del lat[index]

#generate figure
plt.figure(figsize=(20, 10))
plt.boxplot(x=np.array(new_lat).tolist(), labels=np.array(new_names).tolist(), whis=[5,95], showfliers=False)
plt.plot(med_line, label='Median of Medians')
plt.legend() 
plt.xlabel("Node ID")
plt.ylabel("Latency in ms")
plt.savefig(folder + "latency.png", bbox_inches='tight')

#node names
names = [str(x) for x in ids]
#order this mess
rel = reliability
new_names = []
new_rel = []

while len(rel) > 0:
    #go thorugh medians and find smallest index
    helper = 101
    index = -1
    for i in range(0,len(rel)):
        r = rel[i]
        if r < helper:
            helper = r
            index = i
    
    #append smallest found median
    new_names.append(names[index])
    new_rel.append(rel[index])
    del names[index]
    del rel[index]

#generate figure
plt.figure(figsize=(20, 10))
plt.bar(new_names, new_rel)
plt.xlabel("Node ID")
plt.ylabel("Reliability in %")
plt.ylim([min(60.0,math.floor(min(new_rel)-5)), 100.0])
plt.savefig(folder + "reliability.png", bbox_inches='tight')