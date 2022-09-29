
import os, re, os.path
from os import path


if not path.exists('MinerFiles'):
    os.makedirs('MinerFiles')
f=open("MinerFiles/addedTX.json","w")
f.write("{}")
f.close
f=open("MinerFiles/blockDict.json","w")
f.write("{}")
f.close
f=open("MinerFiles/blockchainOrderRef","w")
f.write("")
f.close

if not path.exists('Cache'):
    os.makedirs('Cache')

f=open("Cache/BKCache.json","w")
f.write("{}")
f.close
f=open("Cache/CIDTracker.json","w")
f.write("{}")
f.close
f=open("Cache/TXCache.json","w")
f.write("{}")
f.close


f=open("blocklog.txt","w")
f.write("")
f.close

f=open("transactionlog.txt","w")
f.write("")
f.close
mypath = "TX"
for root, dirs, files in os.walk(mypath):
    for f in files:
        if f=="TempTX.json":
            pass
        else:
            os.remove(os.path.join(root, f))

mypath = "Blocks"
for root, dirs, files in os.walk(mypath):
    for f in files:
        os.remove(os.path.join(root, f))

mypath = "Blocks/Temp"
for root, dirs, files in os.walk(mypath):
    for f in files:
        os.remove(os.path.join(root, f))