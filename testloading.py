import pickle

with open("./results/BRITZ_20190314_014500.pkl", "rb") as f:
    resultDict = pickle.load(f)
print((resultDict["segmentDuration"]))
print(len(resultDict["startTimes"]))
print(len(resultDict["probs"]))
print(len(resultDict["probs"][0]))
