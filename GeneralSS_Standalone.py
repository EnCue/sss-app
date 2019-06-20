import random

"""
This script can be run through the python command-line interpreter, by calling
the 'initiateScheme' method declared below, or run directly through the
python shell.

When initiated, the script will generate a general sharing scheme according to
provided specifications. The following three items are required as input for
the scheme:
-Number of participants (n)
-Complete list of minimal authorized subsets
-A prime field

With these three inputs, the program will generate the values of the
corresponding access structure, maximal unauthorized subsets, cumulative array,
and participant shares for the generated scheme. These values will be displayed
on the command-line / Python shell.


"""

def initiateScheme():
    print("New scheme started")

    #*Prompts user for number of participants
    n = int(input("Enter number of participants: \n"))
    

    #*Prompts user for minimal authorized subsets (basis)
    basis = compileMinAS([])
    print("\nBasis of Access Structure:")
    print(basis)
    

    #*Creates access structure based on basis
    Gamma = generateGamma(basis, n)
    print("Access Structure:")
    print(Gamma)
    

    #*Creates maximal unauthorized subsets from access structure
    MUS = generateMUS(Gamma, n)
    print("Maximal Unauthorized Subset:")
    print(MUS)
    

    width = len(MUS)
    #*Prompts user for secret and prime field
    p, k = getSecret(True, True, width)
    #*Creates shares
    kShares = generateKShares(k, p, width)
    print(kShares)


    #*Creates and displays cumulative array
    CArray = generateCArray(MUS, n)
    mapList = displayMaps(CArray, MUS)
    bitmap = convertToList(mapList)
    
    #*Distributes secret shares according to cumulative array
    secretMaps = distributeSecrets(bitmap, kShares)
    print("Distributed secret shares:")
    print(secretMaps)
    

    #*Allows user to test participant groups
    recoverK(secretMaps, n, p, k)



def getSecret(PGate, KGate, width):
    p = 0
    k = 0
    if(PGate):
        p_str = input("Enter prime modulus larger than " + str(width+1) + "\n")
        try:
            p = int(p_str)
            if(p < width):
                p, k = getSecret(True, False, width)
        except:
            p, k = getSecret(True, False)

    if(KGate):
        k_str = input("Enter secret between 0 and p-1\n")
        try:
            k = int(k_str)
        except:
            p, k = getSecret(False, True)

    return p, k

def generateKShares(k, p, width):
    kShares = []
    kShares.append(k)
    for i in range(width - 1):
        newK = getNewK(p, kShares)
        kShares.append(newK)
    
    finalK = 0
    for n in kShares:
        finalK += n
    finalK = finalK % p
    kShares.remove(k)
    kShares.append(finalK)

    return kShares

def getNewK(p, kShares):
    k = random.randint(0, (p-1))
    if(k in kShares):
        k = getNewK(p, kShares)

    return k

def convertToList(mapList):
    bitmaps = []
    for strMap in mapList:
        parse = list(strMap)
        bitmap = []
        for b in parse:
            b_int = int(b)
            bitmap.append(b_int)
        bitmaps.append(bitmap)

    return bitmaps

def distributeSecrets(maps, kShares):
    kMaps = []
    for bMap in maps:
        kMap = []
        for i, b in enumerate(bMap):
            entry = b * kShares[i]
            kMap.append(entry)
        kMaps.append(kMap)

    return kMaps

def recoverK(kMaps, N, mod, secret):
    AS = getAccessStruct(N)
    recoveredShares = [0] * len(kMaps[0])
    for i, P in enumerate(AS):
        kMap = kMaps[(P-1)]
        for j, k in enumerate(kMap):
            if(k != 0):
                recoveredShares[j] = k

    print(recoveredShares)
    SumK = recoveredShares[-1]
    recK = SumK
    for i, share in enumerate(recoveredShares):
        if(i != (len(recoveredShares)-1)):
            recK -= share
            if(recK < 0):
                recK += mod

    print(recK)
    if(recK != secret):
        print("Recovered secret incorrect. \nEntered group must not be recognized by the access structure")

    r = input("\nTry another group? (Y or N)\n")

    if(r.lower() == "y"):
        recoverK(kMaps, N, mod, secret)
    else:
        print("\nProgram completed.")
    

def getAccessStruct(N):
    AS = []
    AS_str = input("\nEnter list of participants to retrieve secret (of the form P#1 P#1 ... P#i). \n")
    strArr = AS_str.split()
    for s in strArr:
        try:
            i = int(s)
            if(i > N):
                AS = getAccessStruct(N)
                break
            else:
                AS.append(i)
        except:
            AS = getAccessStruct(N)
            break

    return AS

def compileMinAS(basis):
    newMAS = input("Enter new minimal authorized subset (of the form P#1 P#2 ... P#i):\n")
    newMAS = newMAS.split()
    newEntry = []
    for char in newMAS:
        try:
            P = int(char)
            newEntry.append(P)
        except:
            print("Enter numerical values for participants")

    newEntry.sort()
    basis.append(newEntry)
    
    rspns = input("Add another minimal authorized subset: Y or N \n")
    if(rspns.lower() == "y"):
        basis = compileMinAS(basis)

    return basis


def generateGamma(basis, i):
    Gamma = []
    IOrders = [None] * (i+1)
    
    for MAS in basis:
        Gamma.append(MAS)
        
        l = len(MAS)
        orderDelta = i - l
        foundation = [MAS]
        for j in range(1, (orderDelta + 1)):
            for element in foundation:
                remainder = newField(i)
            
                for P in element:
                    remainder.remove(P)
                newIs = []
                for P in remainder:
                    newI = element.copy()
                    newI.append(P)
                    newI.sort()
                    
                    if newI not in newIs:
                        newIs.append(newI)
                o = j + l
                if(IOrders[o] == None):
                    IOrders[o] = newIs
                else:
                    IOrders[o].extend(newIs)
                foundation = newIs

    for IOrd in IOrders:
        if(IOrd != None):
            for I in IOrd:
                if I not in Gamma:
                    Gamma.append(I)
            
    return Gamma


def generateMUS(Gamma, n):
    GammaD = {}
    MUS = []
    for I in Gamma:
        Key = len(I)
        try:
            GammaD[Key].append(I)
        except:
            GammaD[Key] = [I]
    
    orders = GammaD.keys()

    for order in orders:
        OrderedI = GammaD[order]
        spread = len(OrderedI)
        if(spread >= (n - order)):
            for I in OrderedI:
                MUSOrd = order - 1
                if(MUSOrd > 0):
                    field = newField(n)
                    for P in I:
                        field.remove(P)
                    l = len(I)
                    for i in range(0, l):
                        tester = I.copy()
                        del tester[i]

                        if(len(tester) == 1):
                            if tester not in MUS:
                                matches = 0
                            
                                for P in field:
                                    virtTest = tester.copy()
                                    virtTest.append(P)
                                    virtTest.sort()
                                    if virtTest in GammaD[order]:
                                        matches += 1

                                if(matches == len(field)):
                                    MUS.append(tester)
                                    
                        elif tester not in GammaD[order-1]:
                            
                            if tester not in MUS:
                                matches = 0
                            
                                for P in field:
                                    virtTest = tester.copy()
                                    virtTest.append(P)
                                    virtTest.sort()
                                    if virtTest in GammaD[order]:
                                        matches += 1

                                if(matches == len(field)):
                                    MUS.append(tester)

    return MUS


def generateCArray(MUS, n):
    Maps = [""] * n
    for P in range(1, (n+1)):
        PMap = ""
        for entry in MUS:
            if P in entry:
                PMap += "0"
            else:
                PMap += "1"
        Maps.append(PMap)

    return Maps


def displayMaps(CArray, MUS):
    CArray = stripCArray(CArray)
    print("\nCumulative array:")
    print(CArray)
    
    return CArray


def stripCArray(CA):
    newCA = []
    for entry in CA:
        if(entry != ""):
            newCA.append(entry)

    return newCA


def newField(i):
    Field = []
    for ind in range(1, i+1):
        Field.append(ind)

    return Field


initiateScheme()




