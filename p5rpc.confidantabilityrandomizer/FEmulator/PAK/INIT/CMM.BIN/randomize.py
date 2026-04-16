import sys, random, copy

confidantList = []

class AbilityEntry:
    def __init__(self, rank = 65535, abilityId = 0, reqs = 0, bitflag = 0):
        self.rank = rank # in templates/patterns default rank value will appear as -1, but using signed value causes an OverflowError when writing bytes so ive represented it as ushort max instead
        self.abilityId = abilityId
        self.reqs = reqs
        self.bitflag = bitflag

    def from_bytes(abilityBytes):
        reqs = int.from_bytes(abilityBytes[:2], 'big') # this is a bitfield in the actual file but i dont want to mess with it so just treat this as an int
        rank = int.from_bytes(abilityBytes[2:4], 'big')
        abilityId = int.from_bytes(abilityBytes[4:6], 'big')
        # abilityBytes.seek(8)
        bitflag = int.from_bytes(abilityBytes[8:], 'big')

        return AbilityEntry(rank, abilityId, reqs, bitflag)

    def to_bytes(self):
        # print(f"ability id {self.abilityId}, rank {self.rank}")
        entryBytes = self.reqs.to_bytes(2, 'big') + self.rank.to_bytes(2, 'big') + self.abilityId.to_bytes(2, 'big') + b'\x00\x00' + self.bitflag.to_bytes(4, 'big')
        return entryBytes

    def empty():
        return AbilityEntry()

    def is_empty(self):
        return self.abilityId == 0

class ConfidantEntry:
    def __init__(self, maxAbilities = None, abilityPosDict = None, abilities = None):
        if maxAbilities is None:
            self.maxAbilities = 10
        else:
            self.maxAbilities = maxAbilities

        if abilities is None:
            self.abilities = []
        else:
            self.abilities = abilities

        if abilityPosDict is None:
            self.abilityPosDict = {}
        else:
            self.abilityPosDict = abilityPosDict
            for ability in self.abilityPosDict.values():
                self.add_ability(ability)

    def from_bytes(confidantBytes, maxAbilities = None, abilityPosDict = None):
        abilities = []
        for i in range(10):
            start = i * 12
            end = (i + 1) * 12
            abilities.append(AbilityEntry.from_bytes(confidantBytes[start:end]))
        return ConfidantEntry(maxAbilities, abilityPosDict, abilities)

    def to_bytes(self):
        confidantBytes = b''
        for ability in self.abilities:
            confidantBytes += ability.to_bytes()
        return confidantBytes

    def add_ability(self, ability, index = None):
        numAbilities = len(self.abilities)

        if index is None:
            emptyIndex = self.find_first_empty()
            if emptyIndex is not None:
                self.abilities[emptyIndex] = ability
            else:
                self.abilities.append(ability)
        elif numAbilities == index:
            self.abilities.append(ability)
        elif numAbilities < index:
            self.pad_abilities(index)
            self.abilities.append(ability)
        else:
            currentAbilityAtIndex = self.abilities[index]
            if not currentAbilityAtIndex.is_empty():
                self.abilities.append(ability)
            else:
                self.abilities[index] = ability

    def find_first_empty(self):
        for i in range(len(self.abilities)):
            if self.abilities[i].is_empty():
                return i
        return None

    def sort(self):
        self.abilities.sort(key = lambda ability : ability.rank)
        for index, ability in self.abilityPosDict.items():
            self.force_ability_at_index(ability, index)

    def force_ability_at_index(self, ability, pos):
        initialPos = self.abilities.index(ability)
        otherAbility = self.abilities[pos]

        self.abilities[pos] = ability
        self.abilities[initialPos] = otherAbility

    def pad_abilities(self, length = 10):
        while len(self.abilities) < length:
            self.abilities.append(AbilityEntry.empty())

    # def trim_abilities(self):
    #     while len(self.abilities) > 10:
    #         firstEmpty = self.find_first_empty()
    #         if firstEmpty is None:
    #             raise ValueError
    #         else:
    #             self.abilities.pop(firstEmpty)

def ReadCmmFunctionTable(file):
    for i in range(38):
        file.seek(48 + i * 120)
        confidantList.append(ConfidantEntry.from_bytes(file.read(120)))

def ShuffleAbilities():
    excludedAbilityIds = [2, 11]
    platonicIdDict = { 3: 23, 4: 24, 7: 25, 10: 26, 11: 27, 14: 28, 15: 29, 16: 30, 18: 31, 21: 32, 33: 34, 36: 37 }

    trimmedConfidantDict = {}
    excludedAbilityDict = {}

    for i in range(1, 22):
        trimmedConfidantDict[i] = confidantList[i]
        excludedAbilityDict[i] = {}
    trimmedConfidantDict[35] = confidantList[35]
    trimmedConfidantDict[36] = confidantList[36]

    validAbilityEntries = []
    for confidantId, confidant in trimmedConfidantDict.items():
        for ability in confidant.abilities:
            if excludedAbilityIds.count(ability.abilityId) > 0:
                excludedAbilityDict[confidantId][confidant.abilities.index(ability)] = copy.copy(ability)
            elif not ability.is_empty():
                validAbilityEntries.append(copy.copy(ability))

    newConfidantDict = {}
    availableConfidants = list(trimmedConfidantDict.keys())
    for i in range(38):
        if list(excludedAbilityDict.keys()).count(i) > 0:
            abilityPosDict = excludedAbilityDict[i]
        else:
            abilityPosDict = None

        maxAbilities = None
        if preserveRank:
            maxAbilities = GetNumAbilities(i)
        newConfidantDict[i] = ConfidantEntry(maxAbilities, abilityPosDict)

    for ability in validAbilityEntries:
        # print(f"ability id {ability.abilityId}")
        confidantId = availableConfidants[random.randint(0, len(availableConfidants) - 1)]
        print(f"confidant id {confidantId}")

        if not preserveRank:
            ability.rank = random.randint(1, 10)
        newConfidantDict[confidantId].add_ability(ability)
        print(f"appended ability to confidant {confidantId}, ability length {len(newConfidantDict[confidantId].abilities)}")

        if len(newConfidantDict[confidantId].abilities) >= newConfidantDict[confidantId].maxAbilities:
            availableConfidants.remove(confidantId)
            print(f"removed {confidantId} from available confidants")

    for confidant in newConfidantDict.values():
        confidant.sort()
        confidant.pad_abilities()
        # confidant.trim_abilities()

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
        file.seek(48 + i * 120)
        file.write(confidantList[i].to_bytes())

preserveRank = sys.argv[-1] == 'preserve_rank'
print(f"preserve rank is {preserveRank}")
with open("cmmFunctionTable.ctd", "r+b") as file:
    ReadCmmFunctionTable(file)
    ShuffleAbilities()
    WriteCmmFunctionTable(file)