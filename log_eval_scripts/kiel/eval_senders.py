import sys
import numpy as np
import matplotlib.pyplot as plt
import math

#get median of list
def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (s[n//2-1]/2.0+s[n//2]/2.0, s[n//2])[n % 2] if n else None

# store max_seq
max_seq = -1
data_sender_id = -1

# check if there is one argument
if not(len(sys.argv) == 4):
    print('usage: log_eval <location to folder> <sender node_ids []> <iterations>')
    exit()

# array with all node ids
ids = [1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10,
       12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

# store data for all
# data is indexed by data[node_id][seq_num], basically only stores the timestamps, but ordered
data = [dict() for x in range(len(ids))]

# get file location
folder = str(sys.argv[1])
# get the sender nodes id
arr = sys.argv[2].split('[')[1].split(']')[0].split(',')
senders = [int(x) for x in arr]


iterations = int(sys.argv[3])

# get the txt file as string
enc = 'iso-8859-15'

#latency data structure
latency = [[] for x in range(len(ids))]
#Reliability data structure
reliability = [0 for x in range(len(ids))]
total = 0

for it in range(1,iterations+1):

    if it >= 10:
        extendedfolder = folder + "0" + str(it) + "/"
    else:
        extendedfolder = folder + "00" + str(it) + "/"

    #gpio file handler
    file = open(extendedfolder + "logs/combined-traces.vcd", "r", encoding=enc).read()
    lines = file.split("\n")

    #store identifiers for gpio
    if(it <= 1):
        ident = dict()
    else:
        ident.clear()


    substring = "-ch2"
    for line in lines:
        if substring in line:
            x = line.split(substring)[0].split(" ")
            id = int(x[4].split("raspi")[1])
            x = x[3]
            ident[x] = id

    gpio_data = [[] for x in range(len(ids))]
    gpio_missing = []

    #iterating over gpio-file
    i = 0
    start = False
    while i < len(lines):
        #check for line identifier
        if len(lines[i]) == 5:
            #get ident of line
            lid = lines[i][-4:]
            #check if lid is relevant
            if lid in ident:
                #get timestamp for lid
                timestamp = int(lines[i-1][1:])/1000000
                id = ident[lid]
                id = id-1 if id < 11 else id-2
                gpio_data[id].append(timestamp)
        #increment i
        i += 1

    #iterate for each sender
    for sender in senders:
        #iterate over all node ids
        for a in range(len(ids)):
            #get real id of node
            id = ids[a]
            if (id == sender):
                data_sender_id = a
                data[a] = gpio_data[a]
                max_seq = len(data[a])
                total += max_seq + 1
                reliability[a] += total
            else:
                #skip other senders
                if id in senders:
                    continue
                #build file location and read file
                if id < 10:
                    location = extendedfolder + "logs/raspi0" + str(id) + "/log.txt"
                else:
                    location = extendedfolder + "logs/raspi" + str(id) + "/log.txt"
                
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
                
                substring = "sender:" + str(sender)

                new_lines = []
                # eliminate not needed lines from log
                for line in lines:
                    if substring in line:
                        new_lines.append(line)
                
                lines = new_lines
                reliability[a] += len(lines)
                
                no_gpio = [4,17,18,19]
                if id in no_gpio:
                    continue

                try:            
                    max_gpio = int(lines[-1].split(" ")[2].split("gpio:")[1])
                except:
                    print("Node " + str(id) + " had an GPIO error, try rebooting")
                    gpio_missing.append(a)
                    continue

                #get gpio events
                gpio_events = gpio_data[a]
                if(len(gpio_events) == 0) or (len(gpio_events) <= max_gpio):
                    print("Node " + str(id) + " had an GPIO error, try rebooting")
                    gpio_missing.append(a)
                    continue

                for line in lines:
                    #split into parts
                    parts = line.split(" ")
                    #get sequence number from string
                    seq = int(parts[1].split("seq:")[1])

                    gpio = int(parts[2].split("gpio:")[1].split(" ")[0])
                    #put into data
                    data[a][seq] = gpio_events[gpio]

        #evaluate data

        #get sender dictionary
        sender_dict = data[data_sender_id]

        # iterate over each element
        for a in range(len(ids)):
            delays = []

            if(ids[a] == sender):
                delays = [0 for x in range(max_seq)]
            else:   
                # get dict from data
                dict = data[a]
                # if the dict is empty, the node doesnt exits or didnt produce data
                if bool(dict):
                    for seq in range(len(sender_dict)):
                        if seq in dict:
                            delay = dict[seq] - sender_dict[seq]
                            if delay > 0 and delay < 10000000:
                                # append to array of delays
                                delays.append(delay)
                else:
                    delays = []    
            latency[a].extend(delays)

#node names
names = [str(x) for x in ids]
new_names = []

#purify latencies
lat = []
while len(latency) > 0:
    if len(latency[0]) > 0:
        lat.append(latency[0])
        new_names.append(names[0])
    
    del latency[0]
    del names[0]

#node names
names = new_names
#order this mess
new_names = []
new_lat = []
medians = []
#get median
for l in lat:
    medians.append(median(l))

#median line
med_line = [median(medians) for x in ids]

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
saveloc = folder + "latency.png"
print(saveloc)
plt.savefig(saveloc, bbox_inches='tight')

#node names
names = [str(x) for x in ids]
#order this mess
rel = []
for a in range(len(ids)):
    id = ids[a]
    if id in senders:
        rel.append(100.0)
    else:
        rel.append((reliability[a]/total)*100)

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
plt.ylim([min(80.0,math.floor(min(new_rel)-5)), 100.0])
saveloc = folder + "reliability.png"
print(saveloc)
plt.savefig(saveloc, bbox_inches='tight')