import random
import math


"""
This program generates a Shamir (t,n)-Threshold Scheme, with the desired
settings - as set by the user. The scheme can be initiated by running this
python script through the command line, or run directly via the python shell.

For specifications, the program requires the following 4 parameters:
-Prime field, over which all calculations will be conducted
-Desired secret, in the form of some number less than the prime field
-Number of total participants
-Size of threshold
"""

def initiateScheme(predefinedVars):
    kField = []
    n = 0
    t = 0
    #*Allows scheme to be run multiple times with different secret
    if not predefinedVars:
        Elements = input("Enter prime field (q)\n")

        q = int(Elements)
        q = testPrimality(q)
        
        Field = createField(q)
        print("\nField created:")
        print(Field)

        kField = Field
        
        n = input("Enter number of participants (less than field order)\n")
        t = input("Enter access structure length (less than participant number)\n")
        
        predefinedVars = [n, t, q, Field]
        
        if(n >= t):
            print("Creating new (" + t + ", " + n + ")-Threshold Scheme")
        
        else:
            print("Access structure length must be less than number of participants")
            initiateScheme()
    else:
        kField = predefinedVars[3]
        q = predefinedVars[2]
        t = predefinedVars[1]
        n = predefinedVars[0]
    
    secretInd = input("\nEnter index of desired secret (k) in field (0 to (q-1))\n")
    secret_k = kField[int(secretInd)]
    print(secret_k)
    recovered_k = runScheme(t, n, secret_k, q, Field)
    
    return predefinedVars, recovered_k


def testPrimality(q):
    i = q
    q = math.sqrt(q)
    q = int(q)
    for p in range(2, (q+1)):
        f = i / p
        if(f.is_integer()):
            #print(f)
            #print(i)
            #print(p)
            newQ = input("Enter prime number")
            newQ = int(newQ)
            newQ = testPrimality(newQ)
            i = newQ
            break
    return i


def createField(q):
    ModuloK = []
    for i in range(0, q):
        ModuloK.append(i) 
    
    return ModuloK
    


def runScheme(t_str, n_str, k, q, Field):
    x_subi = [0]
    a_subj = [0]
    pShares = [0]
    pShares_regex = [0]
    
    t = int(t_str)
    n = int(n_str)
    
    for i in range(1, n+1):
        #print("ran")
        x = getDistinctX(x_subi, Field)
        x_subi.append(x)

    print(x_subi)
    
    for j in range(1, t):
        ind = random.randint(0, q)
        a_subj.append(Field[ind])
    print(a_subj)
    
    for i in range(1, n+1):
        x = x_subi[i]
        polynomialSum = k
        #print(k)
        for j in range(1, t):
            a = a_subj[j]
            exponent = math.pow(x, j)
            polynomialSum += a * exponent
        
        regEx = polynomialSum % q
        pShares_regex.append(regEx)
        
        pShares.append(polynomialSum)
    
    print("Shares generated")
    displayShares_i(pShares_regex)

    generatedK = tryAccessStructure(k, pShares, x_subi, t_str, q)
    
    return generatedK


def reduce(integer, F):
    F.sort(reverse=True)
    print(F)
    binary = []
    regEx = []
    for i, f in enumerate(F):
        if(integer >= f):
            integer -= f

            binary.append(1)
            regEx.append(f)
        else:
            binary.append(0)

    return binary, regEx


def tryAccessStructure(k, pShares, x_subi, t_str, q):
    P_Subset = getSubset()

    generatedK = generateK(pShares, x_subi, P_Subset, q)
    if(generatedK != k):
        print("Incorrect secret; access structure must be of length: " + t_str)
    else:
        print("Secret recovered")
    r = input("Try different access structure (Y or N)\n")
    if(r.upper() == "Y"):
        generatedK = tryAccessStructure(k, pShares, x_subi, t_str, q)

    return generatedK


def getDistinctX(x_subi, F):
    #x_subi = []
    ind = random.randint(0, (len(F)-1))
    x = F[ind]
    if not x in x_subi:
        return x
    else:
        x = getDistinctX(x_subi, F)
        return x
    

def displayShares_i(pShares):
    P_ID_str = input("Enter participant number to see share (number from 1 - n)\n")
    P_ID = int(P_ID_str)
    try:
        Share = pShares[P_ID]
        Share = int(Share)
        print("Share for participant #" + P_ID_str + ": " + str(Share))
        Repeat = input("Display another share (Y, or N)\n")
        if(Repeat.upper() == "Y"):
            displayShares_i(pShares)
    except:
        print("Index out of range: \nEnter number between 1 and access structure length.")
        displayShares_i(pShares)
    
    return


def getSubset():
    Subset_RAWstr = input("\nEnter list of participants who wish to recover the secret\nEnter in form 'ID#1 ID#2 ... ID#T' where ID#i is the number of\nparticipant i \n")
    Subset_str = Subset_RAWstr.split()
    Subset = [0]
    for ID in Subset_str:
        try:
            ID = int(ID)
            Subset.append(ID)
        except:
            print("Error in list entered, try again")
            Subset = getSubset()
            #ADD RECURSIVE FUNCTION
        
    return Subset


def generateK(pShares, x_subi, Subset, q):
    y_subset = []
    x_subset = []
    
    Subset.sort()
    for ID in Subset:
        y_i = pShares[ID]
        x_i = x_subi[ID]
        y_subset.append(y_i)
        x_subset.append(x_i)
    
    print(x_subset)
    recoveredK = 0
    for j in range(1, (len(x_subset))):
        x_j = x_subset[j]
        b_j = 1
        for L in range(1, len(x_subset)):
            if(L != j):
                x_L = x_subset[L]
                newCoeff = float(x_L)/(x_L - x_j)
                b_j = b_j * newCoeff
        recoveredK += y_subset[j] * (b_j)

    recoveredK_int = int(round(recoveredK))
    print(recoveredK_int)
    
    return recoveredK_int


def runPackage(predefinedVars, recoveredKs):
    predefinedVars, returnK = initiateScheme(predefinedVars)
    if returnK in predefinedVars[2]:
        print("New secret found:" + str(returnK))
        recoveredKs.append(returnK)
        print(recoveredKs)
    else:
        print("Invalid access structure")

    response = input("Run process again for different k in field (Y or N).\n")
    if(response.upper() == "Y"):
        runPackage(predefinedVars, recoveredKs)
    
#initiateScheme()

runPackage([], [])



