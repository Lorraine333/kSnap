
# coding: utf-8

# In[1]:

import math
import sys
import re 
import heapq
from sets import Set
from matplotlib import cm
import itertools
import numpy as np
import pandas as pd
import matplotlib as mpl
import pydotplus
from graphviz import Digraph
from sklearn import linear_model
from __future__ import division
mpl.rc('figure', figsize=[10,6]) 


# In[2]:

def updateFlag(val,sorted_attr_row):
    for i in range(len(sorted_attr_row)-1):
        val[i] = sorted_attr_row[i+1]

def defineT(attr):
    dtype = [('Id',int)]
    for i in range(len(attr)):
        dtype.append((attr[i],'S10'))
    return dtype


# In[3]:

def ACompatible(graph,edge,attr):
    dtype = defineT(attr)
    value = list(graph[attr].itertuples())
    original_table = np.asarray(value,dtype=dtype)
    groupArr = []

    sorted_attr = np.sort(original_table, order=attr)  
    val = ['','']
    for i in range(len(sorted_attr)):
        for j in range(len(attr)):
            if(sorted_attr[i][j+1]==val[j]):
                if(j == len(attr)-1):
                    newGroup.append(sorted_attr[i])
            else:
                newGroup = [(sorted_attr[i])]
                groupArr.append(newGroup)
                updateFlag(val,sorted_attr[i])
                break
    return groupArr


# In[4]:

def DataStruture(result1,edge,attr,graph):
    print "update data structure"
    print "groupnumber",len(result1)
    groupNum = len(result1)
    nodeNum = graph.shape[0]
    mapsize = (nodeNum,groupNum)
    bitMap = np.zeros(mapsize)
    PArraySize = (groupNum,groupNum)
    PArray = np.zeros(PArraySize)
    edge = np.asarray(edge)
    
    #initialize bit map
    for i in range(groupNum):
        groupSet = result1[i]
        for j in range(len(groupSet)):
            CurrentNode = groupSet[j]
            index = CurrentNode[0]
            for m in range(groupNum):
                if(m!=i):
                    groupSet1 = result1[m]
                    for n in range(len(groupSet1)):
                        CurrentNode2 = groupSet1[n]
                        index2 = CurrentNode2[0]
                        if(not pd.isnull(edge[index2,index+1])):
                            if(edge[index2,index+1]==1):
                                bitMap[index][m]=1

    #initialize participation array
    for i in range(groupNum):
        groupSet = result1[i]
        temp = np.zeros(groupNum)
        for j in range(len(groupSet)):
            CurrentNode = groupSet[j]
            index = CurrentNode[0]
            for k in range(groupNum):
                temp[k] += bitMap[index][k]
        PArray[i] = temp
        
    return PArray,bitMap


# In[5]:

def condition(SubGroup,PArray):
    GroupNum = len(SubGroup);
    for i in range(GroupNum):
        setSize = len(SubGroup[i])
        for j in range(GroupNum):
            if ((PArray[i][j]!=setSize) & (PArray[i][j]!=0.0)):
                return False,i+1
    return True,0         


# In[150]:

def GetMaxHeap(TempResult,PArray):
    h = []
    result = 0
    groupT = 0
    for i in xrange(len(TempResult)):
        #print 'CT of group',str(i)
        CTval, groupT = calCT(TempResult,i,PArray)
        value = 0-CTval
        heapq.heappush(h, (value,i,groupT))
    result = heapq.heappop(h)
    #print 'update group',result[1],'groupT',result[2],'ctvalue',0-result[0]
    return result[1]+1,result[2]


# In[151]:

def calRatio(PArray,i,j,TempResult):
    gNum1 = len(TempResult[i])
    #gNum2 = len(TempResult[j])
    pNum1 = PArray[i][j]
    #pNum2 = PArray[j][i]
    return pNum1/gNum1
    #return (pNum1+pNum2)/(gNum1+gNum2)
    


# In[152]:

def calCT(TempResult,i,PArray):
    result = 0
    t = 0
    for j in xrange(len(PArray)):
        ratio = calRatio(PArray,i,j,TempResult)
        if(ratio<=0.5):
            current = PArray[i][j]
            #print 'delta',current,'with group',j
        else:
            current = len(TempResult[i])-PArray[i][j]
            #print 'delta',current,'with group',j
        if(current>result):
            result = current
            t = j
    #print 'current CT of group',i,result,t
    return result,t


# In[153]:

def Split(BitMap,fixedGNum,groupT,TempResult,graph,attr):
    groupNum = len(TempResult)
    WaitingGroup = TempResult[fixedGNum-1]
    tempBitMapsize = (len(WaitingGroup),groupNum)
    tempBitMap = np.zeros(tempBitMapsize)
    NodeIndex = []
    subGroup1 = []
    subGroup2 = []
    
    dtype = defineT(attr)
    value = list(graph[attr].itertuples())
    original_table = np.asarray(value,dtype=dtype)
    for i in range(len(WaitingGroup)):
        NodeIndex.append(WaitingGroup[i][0])
        tempBitMap[i][:] = BitMap[WaitingGroup[i][0]][:]
    table = np.concatenate((np.asarray(NodeIndex).reshape(len(np.asarray(NodeIndex)),1),tempBitMap),axis=1)

    typename = []
    for i in range(groupNum):
        typename.append("attr"+str(i))
    
    dtype = [('Id',int)]
    for i in range(groupNum):
        dtype.append((typename[i],float))

    value = []
    for i in range(len(NodeIndex)):
        value.append(tuple(table[i].tolist()))

    waitingSortTable = np.asarray(value,dtype=dtype)
    
    k=groupT
    temp = np.sort(waitingSortTable, order=[typename[k],'Id'])
    for m in range(len(temp)-1):
        if(temp[m][k+1]!=temp[m+1][k+1]):
            for j in range(m+1):
                subGroup1.append(original_table[temp[j][0]])
            for n in range(m+1,len(temp)):
                subGroup2.append(original_table[temp[n][0]])
            TempResult.remove(WaitingGroup)
            TempResult.append(subGroup1)
            TempResult.append(subGroup2)
            return TempResult
    return None


# In[154]:

def kSNAP(graph,edge,attr,k):
    TempResult = ACompatible(graph,edge,attr)
    PArray,BitMap = DataStruture(TempResult,edge,attr,graph)
    for i in range(len(TempResult)):
        print "group"+str(i)
        #print len(TempResult[i])
        print TempResult[i]
    print 'Parray:'
    print PArray,'\n'
    groupNum, groupT = GetMaxHeap(TempResult,PArray)
    cond,UseLessGN = condition(TempResult,PArray)
    while((k>len(TempResult)) & (not cond)):
        print 'groupNum',groupNum,'groupT',groupT
        TempResult = Split(BitMap,groupNum,groupT,TempResult,graph,attr)
        PArray,BitMap = DataStruture(TempResult,edge,attr,graph)
        for i in range(len(TempResult)):
            print "group"+str(i)
            #print len(TempResult[i])
            print TempResult[i]
        print 'Parray:'
        print PArray,'\n'
        groupNum, groupT = GetMaxHeap(TempResult,PArray)
        cond,UseLessGN = condition(TempResult,PArray)
    return TempResult,PArray


# In[158]:

graph = pd.read_csv('studentTestData/graph.csv')
edge = pd.read_csv('studentTestData/relation.csv')
attr = ['Department','Gender']
kSNAP(graph,edge,attr,8)


# In[143]:

attr = ['type']
vertex = pd.read_csv('SwiftData/vertex.csv')
edge = pd.read_csv('SwiftData/edge.csv')
vertex['index'] = vertex.index

#make the adjencent matrix
NodeNum = len(vertex)
EdgeNum = len(edge)
vertex = np.asarray(vertex)
edge = np.asarray(edge)
Size = (NodeNum,NodeNum+1)
AdjMatrix = np.zeros(Size)

for k in range(NodeNum):
    AdjMatrix[k][0] = k+1
    
for i in range(len(edge)):
    if(edge[i][2]==1):
        for j in range(len(vertex)):
            if (vertex[j][0] == edge[i][0]): 
                startV = vertex[j][15]
            if(vertex[j][9] == edge[i][1]):
                endV = vertex[j][15]
    else:
        for j in range(len(vertex)):
            if (vertex[j][9] == edge[i][1]):      
                startV = vertex[j][15]
            if(vertex[j][0] == edge[i][0]):
                endV = vertex[j][15]
    AdjMatrix[endV][startV+1] = 1


# In[147]:

vertex = pd.read_csv('SwiftData/vertex.csv')
SMRnode,PArray = kSNAP(vertex,AdjMatrix,attr,)


# In[148]:

dot2 = Digraph(comment='ColorGraph')
vertex = pd.read_csv('SwiftData/vertex.csv')
vertex['index']= vertex.index
edge = np.asarray(edge)
for i in range(len(SMRnode)):
    if(i==0):
        color = 'red'
    if(i==1):
        color = 'blue'
    if(i==2):
        color = 'green'
    if(i==3):
        color = 'yellow'
    if(i==4):
        color = 'cyan'
    if(i==5):
        color = 'magenta'
    if(i==6):
        color = 'Purple'
    if(i==7):
        color = 'grey'
    if(i==8):
        color = 'tan'
    if(i==9):
        color = 'SeaGreen'
    if(i==10):
        color = 'chocolate'
    if(i==11):
        color = 'salmon'
    if(i==12):
        color = 'YellowGreen'
    if(i==13):
        color = 'Lavender'
    if(i==14):
        color = 'Olive'
    if(i==15):
        color = 'Orange'
    if(i==16):
        color = 'Violet'
    if(i==17):
        color = 'PeachPuff'
        
        
    for j in range(len(SMRnode[i])):
        if(SMRnode[i][j][1]=='App'):
            vertexid = vertex.iloc[SMRnode[i][j][0]]['index']
            dot2.node(str(vertexid),str(SMRnode[i][j]) ,color = color,style='filled')
        if(SMRnode[i][j][1]=='File'):
            fileid = vertex.iloc[SMRnode[i][j][0]]['index']
            dot2.node(str(fileid),str(SMRnode[i][j]) ,color = color,style='filled')
for j in range(len(edge)):
    if(edge[j][2]==1):
        startid = vertex[vertex['app_exec_id']==str(edge[j][0])].index.values[0]
        endid = vertex[vertex['file_id']==str(edge[j][1])].index.values[0]
        dot2.edge(str(startid),str(endid))            
    else:
        startid = vertex[vertex['file_id']==str(edge[j][1])].index.values[0]
        endid = vertex[vertex['app_exec_id']==str(edge[j][0])].index.values[0]
        dot2.edge(str(startid),str(endid))
dot2.render('1013Output/kSnapColorGrap')


# In[149]:

dot1 = Digraph(comment='Summary Graph')

for i in range(len(SMRnode)):
    if(i==0):
        color = 'red'
    if(i==1):
        color = 'blue'
    if(i==2):
        color = 'green'
    if(i==3):
        color = 'yellow'
    if(i==4):
        color = 'cyan'
    if(i==5):
        color = 'magenta'
    if(i==6):
        color = 'Purple'
    if(i==7):
        color = 'grey'
    if(i==8):
        color = 'tan'
    if(i==9):
        color = 'SeaGreen'
    if(i==10):
        color = 'chocolate'
    if(i==11):
        color = 'salmon'
    if(i==12):
        color = 'YellowGreen'
    if(i==13):
        color = 'Lavender'
    if(i==14):
        color = 'Olive'
    if(i==15):
        color = 'Orange'
    if(i==16):
        color = 'Violet'
    if(i==17):
        color = 'PeachPuff'
          
    dot1.node(str(SMRnode[i][0]),str(SMRnode[i][0]),color = color,style='filled')
    for j in range(len(SMRnode)):
        if(i!=j):
            if(PArray[i][j]!=0):
                dot1.edge(str(SMRnode[j][0]),str(SMRnode[i][0]))

dot1.render('1013Output/kSnapSummary_Graph')


# In[ ]:



