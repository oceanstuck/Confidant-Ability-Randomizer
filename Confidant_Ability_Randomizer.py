import ctypes, pickle, random

class AbilityEntry:
    padding = 0

    def SerializeEntry(file):


    def DeserializeEntry():

class ConfidantEntry:
    def SerializeEntry(file):


    def DeserializeEntry():

with open("cmmFunctionTable.ctd", "r+b") as file:
    for i in range(0, 38):
        file.seek(32 + i * 120)
