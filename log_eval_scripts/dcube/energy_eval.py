import sys
import numpy as np
import matplotlib.pyplot as plt
import csv

def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (s[n//2-1]/2.0+s[n//2]/2.0, s[n//2])[n % 2] if n else None

# check if there is one argument
if not(len(sys.argv) == 2):
    print('usage: energy_eval.py <location to file>')
    exit()

ids = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
       110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
       200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 
       210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 
       220, 221, 222, 223, 224, 225, 226, 227]

with open(str(sys.argv[1]), newline='') as csvfile:
    #gpio file handler
    filereader = csv.reader(csvfile)
    amps = [[] for x in range(len(ids))]

    for row in filereader:
        if len(row) < 2:
            continue
        if row[0] == "Time":
            continue
        
        for i in range(1,len(row)):
            try:
                amps[i-1].append(float(row[i]))
            except ValueError:
                print("Random Error")
        

    #node names
    names = [str(x) for x in ids]

    #sort this mess
    new_names = []
    new_amps = []
    medians = []
    total = 0
    number = 0
    #get median
    for amp in amps:
        total += sum(amp)
        number += len(amp)
        medians.append(median(amp))
        
    #median line
    med_line = [(total/number) for x in ids]

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
        new_amps.append(amps[index])
        del medians[index]
        del names[index]
        del amps[index]

    #generate figure
    plt.figure(figsize=(20, 10))
    plt.boxplot(x=np.array(new_amps).tolist(), labels=np.array(new_names).tolist(), whis=[5,95], showfliers=False)
    plt.plot(med_line, label='Median of Medians')
    plt.legend() 
    plt.xlabel("Node ID")
    plt.ylabel("Amperage in mA")
    plt.savefig(str(sys.argv[1]).split(".csv")[0] + ".png", bbox_inches='tight')