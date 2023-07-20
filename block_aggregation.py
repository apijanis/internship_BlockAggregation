import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.lines import Line
# from matplotlib.patches import Circle
import random
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import math 

import networkx as nx


from randomcircuit import * 
from layeredcircuit import * 

'''
In this file, the mathematica file ... 
will be transcripted into python, extended and commented in order for other people to be able to use it. 

There are a few important files involved in this project. 
The first one is randomcircuit.py - it creates a random circuit and plots it using qiskit. 

The second one is layeredcircuit.py - it creates a layered circuit given a raw circuit as input 

The third one is blockprocessing.py - it applies the block aggregation algorithm to the layered circuit. 

'''


circuit_of_qubits = random_circuit(10, 20)

# show_circuit(10,circuit_of_qubits)

layeredcircuit = LayerCircuit(10, circuit_of_qubits)

# show_layeredCircuit(10, circuit_of_qubits, layeredcircuit)
print(layeredcircuit)
'''
Now that we have the layered circle going, we can focus on the block aggregation. 
This will be done ... 

Structure: 
Aggregation step - Postprocessing step - Qubit Placement - ...
repeat until termination condition is satisfied 

'''

def EvaluateGateCoverage(S, G, Nq, Qmax, Mmax):
    '''
    evaluates gate coverage given: 
        1. A set of qubit sets S
        2. A gate Coverage set G
        3. The total number of qubits 
        4. The maximal number of qubits in a processing zone Qmax  
        5. The maximal number of processing zones Mmax

    returns two ints gateCoverage and qubitNonCoverage, indicating 1. how many gates are covered with this constellation and 2. the number of qubits that are not covered given the current constellation 



    '''

    # initialize variables of interest to zero 
    gateCoverage = 0
    qubitNonCoverage = 0

    # define running variable 
    processingzone_no = 1

    # iterate over elements in qubit sets 
    for n in range(len(S)):

        # if one specific set of qubits has more elements than can be stored in the processing zone, the number of qubits that cannot be covered is increased 
        if len(S[n]) > Qmax: 
            qubitNonCoverage += len(S[n])

        # if the number of qubits in a set is still in the range of possible qubits in a processing zone, and we populate one of the possible processing zones whose number is limited by Mmax:
        if len(S[n]) <= Qmax and processingzone_no <= Mmax: 

            # we increase the gatecoverage 
            gateCoverage += len(G[n])

            # and we jump to the next processing zone 
            processingzone_no += 1  

    return gateCoverage, qubitNonCoverage



def InitBlockAggregation():
    S = []
    G = []
    c = []
    S_b = []
    G_b = []
    return S, G, c, S_b, G_b


'''
Pseudocode for Blockaggregation 

G_n, so one specific element of the G list indicates what gates are covered by the Qubit Set S_n  
Mmax is the number of processing zones 

'''

def AggregateBlocksStep(layeredCirc, circ, Nq, Qmax, Mmax):
    '''
    The goal is to find the set of S and G that produce the best GateCoverage!!
    '''
    
    
    # Initialize 
    # S, G, c, S_best, G_best = InitBlockAggregation()

    # S is a list of lists! G is a list of lists! 
    # At the beginning, S is of length Nq, but in the course of the algorithm, the qubits as well as the gates are merged together and S gets shorter

    # before starting the iteration over layers and gates, initialize the S and G lists
    # The s list, the list containing the qubits, will be initialized as follows: S = [[1],[2],...], so the first qubit set contains only the first qubit, the second set only the second qubit and so on
    S = [[n] for n in range(Nq)]

    # same for the gate coverage sets
    G = [[] for _ in range(Nq)]

    # also the pointer variables will be initialized, in the beginning cn = n, because every qubit has its own set S_n, later the sets will get merged and more qubits will have the same cn
    ctbl = [n for n in range(Nq)]

    print(S, G, ctbl)

    S_best = []
    G_best = []

    # initialize gate coverage counter 
    bestGateCoverage = 0


    # iterate over layers 
    for layer_no in range(len(layeredCirc)):
        print(layer_no)
        
        # iterate over gates in layers 
        for gate_no in range(len(layeredCirc[layer_no])):
            print('gateno', gate_no)
            gate = layeredCirc[layer_no][gate_no]
            
            # define qubit one and two, that are part of the gate gate_no in layer layer_no 
            QB_n = circ[gate][1][0]
            QB_m = circ[gate][1][1]

            # print("Qubits one and two: ", QB_n, QB_m)
            # print('belonging to gate ', gate)

            # now we define, for this specific for loop, the two pointers cm and cn. We get them from the pointer list ctbl
            # Remember: cm and cn are just two numbers. 
            # To what qubit set do the two qubits belong? 
            cn = ctbl[QB_n]
            cm = ctbl[QB_m]

            # print('Corresponding pointers to qubit sets: ', cn, cm)
            
            # append gate (which is just a number) to gate coverage set of qubit set corresponding to cn
            if G[cn] != []:
                G[cn].append(gate)
            if G[cn] == []:
                G[cn] = [gate]

            # if cn and cm are equal, meaning they are part of the same qubit set, continue
            if cn == cm: 
                continue        # we don't have to merge the Qubit sets 

            # Merge Qubit sets
            # We always merge the smaller to the larger set. So if the set belonging to cm is larger than the set belonging to cn, swap them 
            if len(S[cn]) < len(S[cm]):
                temp = cm
                cm = cn 
                cn = temp

            # We merge the qubit sets together
            S[cn] = S[cn] + S[cm]

            # And we merge the gate coverage sets together
            # Remember: Gate n connects qubits n and m, so we dont have to append the gate to G[cm] as well, if we did, we would have it twice 
            G[cn] = G[cn] + G[cm]

            # All the pointers that belonged to the qubits in set S[cm] will now be pointing to set S[cn]
            for i in range(len(S[cm])):

                # qubits are just numbers in the code, so S[cm][i] returns exactly the n-th qubit of all qubits. 
                ctbl[S[cm][i]] = cn     # all elements in S[cm] which represent qubits stored as numbers are assigned an element in the ctbl list corresponding to cn

            # The qubit set S[cm] is emptied 
            S[cm] = []

            # The gate coverage set corresponding to Set cm is emptied, because it was merged above
            G[cm] = []

            # print('the list looks like this:', S)
            # print('the gatelist looks like this:', G)
            # print('the pointerlist looks like: ', ctbl)

            # Remember: S is sorted list and G is a sorted list
            # They are sorted by size; biggest qubits sets as first elements, biggest gate coverage sets as first elements

            # first, let's take care of the set cn that we appended stuff to:
            # if cn is not the first element in the list already (if we append something to the biggest element, it stays the biggest element), we dont have to do anything 
            if cn > 0:

                # we want to move S[cn] to the appropriate position in S. Compare to the element that is one element after it in the list. If it is bigger, move S[cn] up one element
                while len(S[cn]) > len(S[cn-1]) and cn != 0:
                    
                    # in the pointer list ctbl, assign cn to all elements that are assigned cn - 1

                    # What's happening here is essentially swapping all the elements in the lists ctbl, G and S accordingly. 

                    # remember: We effectively move S[] up in the set of qubits S, so upon moving up one step, we effectively replace S[cn] and S[cn-1] as well as the pointers that point to them;
                    # the pointers of the qubits that are stored in set cn will become cn-1 and vice versa 
                    for k in range(len(S[cn])):
                        ctbl[S[cn][k]] = cn - 1

                    for k in range(len(S[cn-1])):
                        ctbl[S[cn-1][k]] = cn


                    # swap the two elements S[cn] and S[cn-1], effectively moving S[cn] up one element in the list. 
                    templist = S[cn]
                    S[cn] = S[cn-1]
                    S[cn-1] = templist

                    # swap the two elements G[cn] and G[cn-1]
                    templist = G[cn]
                    G[cn] = G[cn-1]
                    G[cn-1] = templist 

                    cn -= 1

            # now, for the second list element corresponding to the pointer cm 
            # if cm is not the last element in the list already (if we clear the last element of the list, )
            # We cannot just append [] to the end of S and G, since we have to move the stuff inside the ctbl list as well

            # LOOK AT THIS AGAIN!!!

            if cm < Nq-1:

                # if cm < len(S):
                #     break 

                while len(S[cm+1]) > 0:
                    for k in range(len(S[cm+1])):
                        ctbl[S[cm+1][k]] = cm

                    S[cm] = S[cm+1]
                    S[cm+1] = []

                    G[cm] = G[cm+1]
                    G[cm+1] = []        

                    cm += 1

                    if cm >= len(S) - 1:
                        break


            '''
            At this point, the sets have been merged and sorted. Now, to evaluate how well the gates are covered by these particular sets. 
            '''        

                
            # Now that the qubit set as well as the gate coverage set are updatet, check the gate coverage
            # So: How many gates are covered by the Qubit sets S = [S_1, S_2, ...] ?

            gateCoverage, qubitNonCoverage = EvaluateGateCoverage(S, G, Nq, Qmax, Mmax)

            # termination condition: 
            # if the remaining qubits - those that can be covered by the constellation (excluding these that cannot be covered because they are more than Q) - are less than the qubits that can be stored in the processing zones 
            # in total, so Mmax (no of processing zones) times Qmax (no of qubits in processing zones)
            if Nq - qubitNonCoverage < Mmax * Qmax: 

                print('Termination condition reached!')
                # function returns S_best and G_best, because we're running out of space 
                return S_best, G_best
            
            # compute number of gates covered by Mmax largest Qubit sets of size Q 
            print('Gatecoverage 1:', gateCoverage)

            zoneCtr = 1
            gateCoverage = 0



            # essentially the same as is done in EvaulateGateCoverage???


            # evaluate the gate coverage for this specific constellation of sets 
            for qubitset_no in range(len(G)):
                if len(S[qubitset_no]) < Qmax and zoneCtr <= Mmax:
                    gateCoverage += len(G[qubitset_no])

            print('Gatecoverage 2:', gateCoverage)


            # if the gatecoverage for this particular constellation of sets is better than for the last constellation of sets
            if gateCoverage > bestGateCoverage: 
                bestGateCoverage = gateCoverage
                
                # also, this particular constellation of Qubit sets and of Gate sets are updatet as the best ones so far 
                S_best = S
                G_best = G

    return S_best, G_best        
            


AggregateBlocksStep(layeredcircuit, circuit_of_qubits, 10, 4, 1)



def AggregateBlocksStepPostProcess(S, G, Nq, Qmax, Mmax):
    '''
    After the block aggregation step, this function does a couple of things: 
    1. It selects the sets to be used as processing zone sets 
    2. It pads these sets with additional idle qubits 
    3. It fills all the remaining qubits into a global Idle pool
    4. It builds a new structure of pointer variables for further processing 

    '''

    SP = []
    GP = []

    c = [[] for _ in range(Nq)]

    # apparently a collection of all qubit sets in S that satisfy a certain condition 
    Iset = []

    # essentially a processing zone counter 
    m = 1 

    for n in range(len(S)):
        if len(S[n]) <= Qmax and m <= Mmax: 
            SP.append(S[n])
            GP.append(G[n])

            k = 1

            for qi in range(len(S[n])):
                q =  S[n][qi]
                c[q] = ['p', m, k, 'a']
                k += 1 

            m += 1   
            Iset = Iset + S[n]  

    # now, all the processing zone sets with good sizes are padded with qubits from the idle pool 
    for m in range(Mmax):
        SPi = []
        if len(SP[m]) == 1:
            q = SP[m][1]
            SP[m] = []
            SPi = [q]
            c[q] = ['p', m, 1, 'i']
        
        k = len(SP[m]) + len(SPi) + 1
        while len(SP[m])+ len(SPi) < Qmax:
            q = Iset[1]
            SPi.append(q)
            c[q] = ['p', m, k, 'i']

            # drop first element in the Iset list 
            Iset = Iset[1:]
            k += 1 
        

        SP[m].append(SPi)

    # end of for loop 

    # now, as a last step, assign the poiniter variables for all qubits remaining in the global idle pool 
    for qi in range(len(Iset)):
        q = Iset[qi]
        c[q] = ['i', 1, qi, 'i']


    return SP, GP, Iset, c







def PlaceIdlePoolQB(Fsizes, Iset, c):
    '''
    this function places qubits from a global idle pool into idle storage zones with max capacities specified by F sizes 
    The qubits, in this version, are placed starting from the middle, outwards. 
    '''

    # number of idle zones: 
    numF = len(Fsizes)

    # first idle zone to be filled up, remember: we're starting in the middle 
    f = math.floor(numF / 2)

    # initialize empty idle zones, list of empty lists
    Fset = [[] for _ in range(numF)]


    Isetnew = Iset
    
    cnew = c 

    # Now, to fill up these idle zones. We start in the starting zone, moving left and right, filling up the zones 
    fm = f
    fp = f+1 
    ctr = 1 

    while len(Isetnew) > 0: 

        # start with right zone
        # check if size exceeded: 
        if fp <= numF and len(Fset[fp]) >= Fsizes[fp]:
            fp += 1
        if fp <= numF and len(Fset[fp]) < Fsizes[fp]:
            q = Isetnew[1]
            Fset[fp].append(q)
            cnew[q] = ['i', fp, len(Fset[fp]), 'i']

            # get rid of all cases of q in the list Isetnew 
            Isetnew = [x for x in Isetnew if x != q]

        # if all idle zones are filled up and there is idle qubits left, error 
        if fp == numF and len(Fset[fp]) >= Fsizes[fp] and fm == 1 and len(Fset[fm]) >= Fsizes[fm] and len(Isetnew) > 0:
            print('No more idle zones left, but not all qubits placed.')
            return Fset, cnew

    return Fset, cnew          


def BlockProcessCircuit(CrawInp, Nq, Fsizes, Qmax, Mmax):
    '''
    Keine Ahnung
    '''

    Craw = CrawInp

    B = []

    while len(Craw) > 0:
        C                   = LayerCircuit(Nq, Craw)
        S_best, G_best      = AggregateBlocksStep(C, Craw, Nq, Qmax, Mmax)
        SP, GP, Iset, c     = AggregateBlocksStepPostProcess(S_best, G_best, Nq, Qmax, Mmax)
        FP, cnew            = PlaceIdlePoolQB(Fsizes, Iset, c)

        for gpi in range(len(GP)):
            for gi in range(len(GP[gpi])):
                Craw = [x for x in Craw if x != GP[gpi][gi]]
        
        B.append([SP, GP, FP, cnew])

    return B 



# testlist = BlockProcessCircuit()




'''
Now, for the visualization. 

Use networkx, the same thing I used for the first project as well. 
The method used here gets a list of layers in the format [['1', ...], ['1', ...], ..., [...]]
and plots them in different colors, connecting 
'''



# Create an empty directed graph
G = nx.MultiDiGraph()

# Add nodes to the graph
layers = [
    ['1', '2', '3'],     # Layer 0
    ['1*', '3*', '2*'], # Layer 1
    ['3**', '2**', '1**'],          # Layer 2
]

for layer_idx, layer in enumerate(layers):
    G.add_nodes_from(layer)
    if layer_idx > 0:
        for node in layers[layer_idx - 1]:
            for neighbour in layer:
                if node[0] == neighbour[0]: 
                    G.add_edge(node, neighbour)

# Add edges to connect nodes between layers


# Set the position of the nodes based on their layers
pos = {}
for layer_idx, layer in enumerate(layers):
    for node_idx, node in enumerate(layer):
        pos[node] = (layer_idx, -node_idx)

# Draw the graph with different colors for each layer
plt.figure(figsize=(8, 6))

# Assign different colors to each layer
layer_colors = ['skyblue', 'lightgreen', 'lightcoral']

for layer_idx, layer in enumerate(layers):
    nx.draw_networkx_nodes(G, pos, nodelist=layer, node_color=layer_colors[layer_idx], node_size=1000, label=f'Layer {layer_idx}')

nx.draw_networkx_edges(G, pos, arrows=True)
nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
# plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
plt.axis('off')
plt.show()




# # Draw the graph
# plt.figure(figsize=(8, 6))
# nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=12, font_weight='bold')
# plt.show()





