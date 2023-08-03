import numpy as np
import matplotlib.pyplot as plt
# import random 
import itertools 

from optimizing import *



'''
In this file, the so called tabu search is performed. 



'''




'''
General note: 

manchmal habe ich nicht auf dem Schirm, ob funktionen schon die debugging sachen (die listen zum plotten zum Beispiel) mit zuruckgeben, 
daran koennte es also immer liegen 


'''





def reconstructBlocksFromArrangements(BP, Fsizes, Qmax, Mmax, Nq, Y, zonesTbl, s1Tbl, s2Tbl):
    '''
    Returns: 
        bNew: an updatet B-list 
    '''

    bNew = []

    qbTbl = [q for q in range(Nq)]

    for step in range(len(Y)):
        
        qbTblSort = qbTbl


        # GP = BP[step][1]


        SPNew = [[[], []] for m in range(Mmax)]

        FPNew = [[] for f in range(len(Fsizes))]

        cNew = [[] for q in range(Nq)]

        kpTbl = [1] * Mmax

        kiTbl = [1] * len(Fsizes)


        for qi in range(Nq):
            q = qbTblSort[qi]
            s1 = s1Tbl[step][q]
            s2 = s2Tbl[step][q]

            z = zonesTbl[step][q]

            if s1 == 'i':
                cNew[q] = [s1, z, kiTbl[z], s2]

                kiTbl[z] += 1

                FPNew[z] = FPNew[z] + q 

            else: 
                cNew[q] = [s1, z, kpTbl[z], s2]

                kpTbl[z] += 1

                if s2 == 'a':
                    SPNew[z][1].append(q)
                else: 
                    SPNew[z][2].append(q)


    return bNew



def improvePlacementTabuSearch(BP, Fsizes, Qmax, Mmax, Nq, TSiterations, TSlen, swapNumMax, processingZoneSwapFraction, greedySpread, soreAllBestBP, echo):
    '''
    This function performs the Tabu search! 
    '''

    # initialize all variables
    numF = len(Fsizes)

    numSteps = len(BP)

    idlePools = []
    
    processingPools = []

    zonesTbl = []

    s1Tbl = []

    s2Tbl = []

    QBTbl = [[q for q in range(Nq)]]


    for step in range(numSteps):
        SP = BP[step][0]
        c = BP[step][3]
        idleList = []

        processingList = [[] for _ in range(BP[step][1])]

        zonesList = [0] * Nq

        s1List = [0] * Nq

        s2List = [0] * Nq

        for q in range(Nq):
            if c[q][3] == 'i': 
                idleList.append(q)
            else: 
                processingList[c[q][1]].append{q}
            
            zonesList[q] = c[q][1]

            s1List[q] = c[q][0]

            s2List[q] = c[q][3]

        idlePools.append(idleList)

        processingPools.append(processingList)

        zonesTbl.append(zonesList)

        s1Tbl.append(s1List)
        s2Tbl.append(s2List)




    Y = computeArrangements(BP, Fsizes, Qmax, Mmax)
    costTot = computeTotalCost(Y, Nq)


    if echo == True:

        print('Debug output')


    '''
    This is the point where the Tabu search starts 
    '''

    TSList = [0] * TSlen

    TSFill = 1 

    numImprovements = 0

    tabuCtr = 0 

    noUpdateCtr = 0

    memberQqueries = 0

    numImprovementMultiSwaps = 0
    numImprovementTwoSwaps = 0
    numProcessingZoneSwaps = 0
    numImprovementProcessingZonesSwaps = 0
    costBest = costTot
    YBest = Y
    costProgressTbl = [[] for _ in range(TSiterations)]
    bestCostProgressTbl = [[] for _ in range(TSiterations)]
    YBest = Y
    zonesTblBest = zonesTbl
    s1TblBest = s1Tbl
    s2TblBest = s2Tbl

    # at this point, the stuff is also timed 
    # and reap and sow again due to displaying and developement reasons 

    for i in range(TSiterations): 
        
        # generate random number in range numSteps 
        step = random.randint(0, numSteps-1) 

        if i>processingZoneSwapFraction:

            # generate random integer between 0 and Nq-1 (both included)
            q1 = random.randint(0, Nq-1) 

            s1Swap = s1Tbl[step][q1]
            s2Swap = s2Tbl[step][q1]

            processingZoneIndex = zonesTbl[step][q1];
             
            swapQBnum = random.randint(1, swapNumMax-1)

            if s2Swap == "i":
                swapPool = idlePools[step]
                if s1Swap == 'p' and swapQBnum == 2: 
                    swapPool = swapPool + processingPools[step][processingZoneIndex]

            else: 
                if processingZoneIndex > Mmax:
                    print('Eror, ...')
                    break 

                swapPool = processingPools[step][processingZoneIndex]

            
            swapPool.remove(q1)

            swapPoolSize = len(swapPool)

            if swapPoolSize < swapQBnum - 1:
               
                
                swapQBnum = swapPoolSize
                subsets = list(itertools.combinations(swapPool, swapQBnum - 1))

                numPossibleSwaps = len(subsets)

                rot = random.randint(0, swapQBnum-2)

                swapQBLists = [[q1] + list(subset) for subset in subsets]

                swapQBListsSwapped = [swapQBLists[ssi][rot:] + swapQBLists[ssi][:rot] for ssi in range(len(swapQBLists))]



        else: 
            
            # swap two entire processing zones 
            swapProcessingZones = True 
            numProcessingZoneSwaps += 1 

            processingZonesSwap = random.sample(range(Mmax), 2)

            processingZone1 = [q for q in QBTbl if s1Tbl[step][q] == "p" and zonesTbl[step][q] == processingZonesSwap[0]]

            processingZone2 = [q for q in QBTbl if s1Tbl[step][q] == "p" and zonesTbl[step][q] == processingZonesSwap[1]]

            swapQBLists = [processingZone1 + processingZone2]

            swapQBListsSwapped = [processingZone2 + processingZone1]

            swapQBnum = len(swapQBLists[0])

            numPossibleSwaps = 1 

        
        # initialize single iteration step 
        deltaCostBestLocal = 1000000 
        Yc = Y[step]

        if step > 1: 
            Yp = Y[step-1]
        else: 
            Yp = [0] * Nq

        if step < numSteps: 
            Yf = Y[step + 1]
        else: 
            Yf = [0] * Nq

        deltaCostTbl = [2 * np.dot(Yp[swapQBLists[ssi]] + Yf[swapQBLists[ssi]], Yc[swapQBLists[ssi]] - Yc[swapQBListsSwapped[ssi]]) for ssi in range(numPossibleSwaps)]

        ord = np.argsort(deltaCostTbl)

        deltaCostTbl = np.array(deltaCostTbl)[ord]

        swapQBLists = [swapQBLists[ssi] for ssi in ord]

        swapQBListsSwapped = [swapQBListsSwapped[ssi] for ssi in ord]

        flag = False 

        for ssi in range(numPossibleSwaps):
               
            YTest = Y 

            YTest[step][swapQBLists[ssi]] = YTest[step][swapQBListsSwapped[ssi]]

            memberQqueries += 1

            if YTest in TSList:
                tabuCtr += 1 
                continue 


            # if not in tabu list update best local cost, set update flag true and save swapped arrangement 

            flag = True 

            deltaCostBestLocal = deltaCostTbl[ssi]

            YBestUpdate = YTest
            zonesTblBestUpdate = zonesTbl
            s1TblBestUpdate = s1Tbl
            s2TblBestUpdate = s2Tbl

            zonesTblBestUpdate[step][swapQBLists[ssi]] = zonesTblBestUpdate[step][swapQBListsSwapped[ssi]]
            s1TblBestUpdate[step][swapQBLists[ssi]] = s1TblBestUpdate[step][swapQBListsSwapped[ssi]]



            if greedySpread == False:
                break

            stepp = step + 1 

            while stepp < numSteps: 
                

                if s2Tbl[step][swapQBLists[ssi]] != s2Tbl[step][swapQBLists[ssi]] or  zonesTbl[step][swapQBLists[ssi]] != zonesTbl[stepp][swapQBLists[ssi]]:
                    break

                Yc = YBestUpdate[stepp]
                Yp = YBestUpdate[stepp - 1]
              
                if stepp < numSteps: 
                    Yf = YBestUpdate[stepp + 1]
                else: 
                    Yf = [0] * Nq
              
                deltaCost2 = 2 * (Yp[swapQBLists[ssi]] + Yf[swapQBLists[ssi]]) * (Yc[swapQBLists[ssi]] - Yc[swapQBListsSwapped[ssi]])
              

                if deltaCost2 < 0: 
                    deltaCostBestLocal += deltaCost2
                
                    YBestUpdate[stepp][swapQBLists[ssi]] = YBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    zonesTblBestUpdate[stepp][swapQBLists[ssi]] = zonesTblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                    s1TblBestUpdate[stepp][swapQBLists[ssi]] = s1TblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    for sqbi in range(swapQBLists[ssi]): 
                        sqb = swapQBLists[ssi][sqbi]
                 
                    if s1TblBestUpdate[stepp][sqb] == "i" and s2TblBestUpdate[stepp][sqb] == "a":
                        print("  ERROR in greedy expansion, step: ", step)
                else: 
                    stepp = numSteps
                
                stepp += 1 



            stepp = step - 1 

            while stepp > 1: 


                # Muss noch geandert werden!! 


                if s2Tbl[step][swapQBLists[ssi]] != s2Tbl[step][swapQBLists[ssi]] or  zonesTbl[step][swapQBLists[ssi]] != zonesTbl[stepp][swapQBLists[ssi]]:
                    break

                Yc = YBestUpdate[stepp]
                Yp = YBestUpdate[stepp - 1]
              
                if stepp < numSteps: 
                    Yf = YBestUpdate[stepp + 1]
                else: 
                    Yf = [0] * Nq
              
                deltaCost2 = 2 * (Yp[swapQBLists[ssi]] + Yf[swapQBLists[ssi]]) * (Yc[swapQBLists[ssi]] - Yc[swapQBListsSwapped[ssi]])
              

                if deltaCost2 < 0: 
                    deltaCostBestLocal += deltaCost2
                
                    YBestUpdate[stepp][swapQBLists[ssi]] = YBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    zonesTblBestUpdate[stepp][swapQBLists[ssi]] = zonesTblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                    s1TblBestUpdate[stepp][swapQBLists[ssi]] = s1TblBestUpdate[stepp][swapQBListsSwapped[ssi]]
                
                    for sqbi in range(swapQBLists[ssi]): 
                        sqb = swapQBLists[ssi][sqbi]
                 
                    if s1TblBestUpdate[stepp][sqb] == "i" and s2TblBestUpdate[stepp][sqb] == "a":
                        print("  ERROR in greedy expansion, step: ", step)
                else: 
                    stepp = 1
                
                stepp -= 1 

            # this loop is breaked here:  for ssi in range(numPossibleSwaps)
            break  


        if flag == False: 
            noUpdateCtr += 1 

        if flag == True: 
            TSList[TSFill] = YBestUpdate

            TSFill += 1

            if TSFill > TSlen: 
                TSFill = 1 

            Y = YBestUpdate 

            zonesTbl = zonesTblBestUpdate

            s1Tbl = s1TblBestUpdate

            s2Tbl = s2TblBestUpdate

            costTot = deltaCostBestLocal

            if costTot < costBest: 
                costBest = costTot 

                YBest = YBestUpdate

                zonesTblBest = zonesTblBestUpdate

                s1TblBest = s1TblBestUpdate

                s2TblBest = s2TblBestUpdate

                numImprovements += 1 

                if storeAllBestBP = True: 
                    bNew = reconstructBlocksFromArrangements(BP, Fsizes, Qmax, Mmax, Nq, YBest, zonesTblBest, s1TblBest, s2TblBest)

                if swapProcessingZones == False: 
                    if swapQBnum > 2: 
                        numImprovementMultiSwaps += 1 

                    else: 
                        numImprovementTwoSwaps += 1

                if swapProcessingZones == True:
                    numImprovementProcessingZonesSwaps += 1

            
            else: 
                deltaCostBestLocal = 0 

        costProgressTbl[i] = [i, costTot]

        bestCostProgressTbl[i] = [i, costBest]



    # here is still a lot missing for I guess graphic and debugging purposes, first I have to try to understand this algorithm 



    return bNew, costProgressTbl, bestCostProgressTbl, YBest, numImprovements, tabuCtr, noUpdateCtr
            

'''
Now, for the alternating optimization.

'''

def optimizeArrangements(BP, Nq, Fsizes, Qmax, Mmax, numOptimizationSteps, TSiterations, TSlen, echo, visualOutput):
    bNew = BP 

    totalBestCostTbl = [[] for _ in range(2 * numOptimizationSteps)]

    grPtbl = [[] for _ in range(2 * numOptimizationSteps)]

    grPBest = []

    YTemp = computeArrangements(bNew, Nq, Fsizes, Qmax, Mmax)

    costTotInitial = computeTotalCost(YTemp, Nq)

    costTotBest = 10 ** 9 

    for optimizationstep in range(numOptimizationSteps): 





        bNew, costTotTbl, bNewTbl = improvePlacement(bNew, Nq, Fsizes, Qmax, Mmax, False)

        if echo == True: 
            print('echo')

        if visualOutput == True:
            print('visualoutput')

        bNew, costProgressTbl, bestCostProgressTbl, YBest, numImprovements, tabuCtr, noUpdateCtr = improvePlacementTabuSearch(bNew, Fsizes, Qmax, Mmax, Nq, TSiterations, TSlen, 3, 0, False, visualOutput, False)

        if echo == True: 
            print('echo')

        if visualOutput == True: 
            print('visualoutput')

        # still needs to be returned by tabusearch 
        if bestCostUpdateAll[-1] < costTotBest:

            if visualOutput == True: 
                print('visualoutput')

            # last element in list 
            costTotBest = bestCostUpdateAll[-1]


    # this gets flattened in the mathematica code 
    grPtbl = grPtbl 

    # this as well 
    totalBestCostTbl = totalBestCostTbl



    return grPBest, costTotBest, grPtbl, totalBestCostTbl, costTotInitial



'''
Alternating algorithm over 

Now, the displaying shall be done. 
'''



    