import sys, random

confidantList = []

class AbilityEntry:
    def __init__(self, rank = -1, abilityId = 0, reqs = 0, bitflag = 0):
        self.rank = rank
        self.abilityId = abilityId
        self.reqs = reqs
        self.bitflag = bitflag

    def from_bytes(abilityBytes):
        reqs = int.from_bytes(abilityBytes[:2]) # dont really intend to randomize additional reqs, so just treat this as an int
        rank = int.from_bytes(abilityBytes[2:4])
        abilityId = int.from_bytes(abilityBytes[4:6])
        # abilityBytes.seek(8)
        bitflag = int.from_bytes(abilityBytes[8:])

        return AbilityEntry(rank, abilityId, reqs, bitflag)

    def write(self, file):
        entryBytes = self.reqs.to_bytes(2) + self.rank.to_bytes(2) + self.abilityId.to_bytes(2) + b'\x00\x00' + self.bitflag.to_bytes(4)
        file.write(entryBytes)

    def empty():
        return AbilityEntry()

    def is_empty(self):
        return self == AbilityEntry.empty()

class ConfidantEntry:
    def __init__(self, abilities = []):
        self.abilities = abilities

    def from_bytes(confidantBytes):
        abilities = []
        for i in range(10):
            start = i * 12
            end = (i + 1) * 12
            abilities.append(AbilityEntry.from_bytes(confidantBytes[start:end]))
        return ConfidantEntry(abilities)

    def write(self, file):
        for ability in self.abilities:
            ability.write(file)

def ReadCmmFunctionTable(file):
    for i in range(38):
        file.seek(32 + i * 120)
        confidantList.append(ConfidantEntry.from_bytes(file.read(120)))

def ShuffleAbilities():
    platonicIdDict = { 3: 23, 4: 24, 7: 25, 10: 26, 11: 27, 14: 28, 15: 29, 16: 30, 18: 31, 21: 32, 33: 34, 36: 37 }

    trimmedConfidantDict = {}

    for i in range(1, 21):
        trimmedConfidantDict[i] = confidantList[i]
    trimmedConfidantDict[35] = confidantList[35]
    trimmedConfidantDict[36] = confidantList[36]

    allAbilityEntries = []
    for confidant in trimmedConfidantDict.values():
        for ability in confidant.abilities:
            if ability.abilityId != 0:
                allAbilityEntries.append(ability)

    newConfidantDict = {}
    availableConfidants = list(trimmedConfidantDict)
    for i in range(38):
        newConfidantDict[i] = ConfidantEntry()

    for ability in allAbilityEntries:
        confidantId = availableConfidants[random.randint(0, len(availableConfidants) - 1)]
        print(f"confidant id {confidantId}")

        maxAbilities = 10
        if preserveRank:
            maxAbilities = GetNumAbilities(confidantId)
        print(f"max abilities {maxAbilities}")

        if not preserveRank:
            ability.rank = random.randint(1, 10)
        newConfidantDict[confidantId].abilities.append(ability)
        print(f"appended ability to confidant {confidantId}, ability length {len(newConfidantDict[confidantId].abilities)}")
        if len(newConfidantDict[confidantId].abilities) >= maxAbilities:
            availableConfidants.remove(confidantId)
            print(f"removed {confidantId} from available confidants")

    for confidant in newConfidantDict.values():
        while len(confidant.abilities) < 10:
            confidant.abilities.append(AbilityEntry.empty())

    newConfidantDict[33] = newConfidantDict[36]
    for id1, id2 in platonicIdDict.items():
        newConfidantDict[id2] = newConfidantDict[id1]

    for i in range(1, 38):
        if preserveRank:
            for j in range(10):
                newConfidantDict[i].abilities[j].rank = confidantList[i].abilities[j].rank
        confidantList[i] = newConfidantDict[i]

def GetNumAbilities(confidantId):
    abilities = 0
    for ability in confidantList[confidantId].abilities:
        if not ability.is_empty():
            abilities += 1

    return abilities

def WriteCmmFunctionTable(file):
    for i in range(1, 38):
        file.seek(32 + i * 120)
        confidantList[i].write(file)

preserveRank = sys.argv[-1] == "preserve_rank"
with open("cmmFunctionTable.ctd", "r+b") as file:
    ReadCmmFunctionTable(file)
    ShuffleAbilities()
    WriteCmmFunctionTable(file)