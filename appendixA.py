import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
import itertools
from scipy.spatial.distance import cdist, pdist
from itertools import combinations

S= np.random.rand(100, 2)

'''--------------------Del(P)-----------------------'''
Del = Delaunay(S)
simplices=Del.simplices

lines = set()
for simplex in Del.simplices:
    for i in range(len(simplex)):
        for j in range(i+1, len(simplex)):
            if (simplex[i], simplex[j]) and (simplex[j], simplex[i]) not in lines:
                lines.add((simplex[i], simplex[j]))

plt.scatter(S[:, 0], S[:, 1])
for line in lines:
    plt.plot([S[line[0], 0], S[line[1], 0]], [S[line[0], 1], S[line[1], 1]], c='black')
    plt.gca().set_aspect('equal', adjustable='box')
plt.show()

'''----------GABRIEL 1-simplices, Del1(P)------------'''
def is_gabriel(line, P):
    midpoint = 0.5 * (P[line[0]] + P[line[1]])
    radius = 0.5 * np.sqrt(np.sum((P[line[0]] - P[line[1]])**2))
    true=1
    for point in P:
        if (point==P[line[0]]).all() or (point==P[line[1]]).all():
            continue
        else:
            if cdist([midpoint],[point])<=radius:
                true=0
    return true

gabriel_lines = set()
for line in lines:
    if is_gabriel(line, S):
        gabriel_lines.add(line)

plt.scatter(S[:, 0], S[:, 1])
for line in gabriel_lines:
    plt.plot([S[line[0], 0], S[line[1], 0]], [S[line[0], 1], S[line[1], 1]],c='black')
    plt.gca().set_aspect('equal', adjustable='box')
plt.show()

'''---PERSISTENT HOMOLOGY, DELAUNAY---'''
K =[]
for face in range(len(S)):
    K.append(frozenset((face,)))
for face in lines:
    K.append(frozenset(face))
for face in simplices:
    K.append(frozenset(face))

#FILTRATION
def filt_value_fct(face):
    if len(face) == 1: #If it is a vertex (0-simplex)
        return 0
    return np.max(pdist(S[list(face)]))

filtration_values = []
for face in K:
    filtration_values.append(filt_value_fct(face))

order = np.argsort(filtration_values,kind='mergesort')

K = np.array(K)
filtration_values = np.array(filtration_values)
K = K[order]
filtration_values = filtration_values[order]

face_index_dictionary = {face: index for index, face in enumerate(K)}
#BOUNDARY MATRIX
n=len(K)
partial=np.zeros((n,n))
for j in range(0,n):
    if len(K[j]) == 1:
        continue
    else:
        boundary = list(face_index_dictionary[frozenset(facet)] for facet in combinations(K[j], len(K[j]) - 1))
        for i in range(0,n):
            if face_index_dictionary[K[i]] in boundary:
                partial[i][j]=1
            else:
                continue

def persistent_homology(D):
    R=D
    low=[]
    n=len(D)
    for j in range(0, n):
        count=0
        for i in range(n-1,-1,-1):
            if D[i][j]==1:
                low.append(i)
                count=1
                break
            else:
                continue
        if count==0:
            low.append('undefined')

        for j0 in range(len(low)-1):
            if low[j0]==low[j] and low[j]!='undefined':
                for i in range(n):
                    R[i][j]=(R[i][j0]+R[i][j])% 2
                persistent_homology(R)
    low=[]
    for j in range(0, n):
        count=0
        for i in range(n-1,-1,-1):
            if D[i][j]==1:
                low.append(i)
                count=1
                break
            else:
                continue
        if count==0:
            low.append('undefined')
    return R,low


'''---PERSISTENT HOMOLOGY, GABRIEL---'''
K1 =[]
for face in range(len(S)):
    K1.append(frozenset((face,)))
for face in gabriel_lines:
    K1.append(frozenset(face))
for face in simplices:
    K1.append(frozenset(face))

filtration_values1 = []
for face in K1:
    filtration_values1.append(filt_value_fct(face))

order1 = np.argsort(filtration_values1,kind='mergesort')

K1 = np.array(K1)
filtration_values1 = np.array(filtration_values1)
K1 = K1[order1]
filtration_values1 = filtration_values1[order1]

face_index_dictionary1 = {face: index for index, face in enumerate(K1)}
#BOUNDARY MATRIX
m=len(K1)
partial1=np.zeros((m,m))
for j in range(0,m):
    if len(K1[j]) == 1:
        continue
    else:
        combinations=[]
        for facet in itertools.combinations(K1[j], len(K1[j]) - 1):
            if frozenset(facet) in K1:
                combinations.append(frozenset(facet))
        boundary1 = list(face_index_dictionary1[frozenset(facet)] for facet in combinations )
        for i in range(0,m):
            if face_index_dictionary1[K1[i]] in boundary1:
                partial1[i][j]=1
            else:
                continue

#PERSISTENT 0-HOMOLOGY:
pers0_homology=dict()
for i in range(len(S)):
    if i in  persistent_homology(partial)[1]:
        x=persistent_homology(partial)[1].index(i)
        pers0_homology[i]=K[x]
    else:
        pers0_homology[i] = None

pers0_homology1=dict()
for i in range(len(S)):
    if i in persistent_homology(partial1)[1]:
        x=persistent_homology(partial1)[1].index(i)
        pers0_homology1[i]=K1[x]
    else:
        pers0_homology1[i] = None

#PERSISTENT 1-HOMOLOGY:
pers1_homology=dict()
for element in K:
    if len(element)==2: #the births are the edges
        i=np.where(K==element)[0][0]
        if i in persistent_homology(partial)[1]:  #not all the edges are a birth
            x = persistent_homology(partial)[1].index(i)
            pers1_homology[element] = K[x]
        else:
            pers1_homology[element]=None

pers1_homology1=dict()
list(K1)
for element in K1:
    if len(element)==2:
        i=np.where(K1 == element)[0][0]
        if i in persistent_homology(partial1)[1]:
            x = persistent_homology(partial1)[1].index(i)
            pers1_homology1[element] = K1[x]
        else:
            pers1_homology1[element] = None

print(persistent_homology(partial)[0],persistent_homology(partial1)[0],
pers0_homology,pers0_homology1,
pers1_homology,pers1_homology1)



