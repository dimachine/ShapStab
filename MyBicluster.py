# -*- coding: utf-8 -*-
from collections import defaultdict

class Context:
    def __init__(self, file_name):
            self.filename=file_name
            cfile=open(file_name)
            self.attr_names=cfile.readline().rstrip().split('\t')
            #rstrip() - удаление пробелов в конце строки
            # split - указание разделителя
            self.objects=[]
            cfile.readline()
            n=0
            for line in cfile:
                sobj=line.rstrip().split('\t')
                obj=[]
                n+=1
                for i in range(len(sobj)):
                    obj.append(int(sobj[i]))
                self.objects.append(obj)
                if n%100==0: print ('Loading ', n)
            cfile.close()
            self.nAttr=len(self.attr_names)
            self.nObj=len(self.objects)

    def objPrime(self, oSet):
        #вычисление оператора штрих от множества объектов
        if oSet==[]:
            return list(range(self.nAttr))
        aSet=[attr for attr in range(len(self.objects[oSet[0]])) if self.objects[oSet[0]][attr]==1]
        aSetC=aSet[:]
        for obj in oSet:
            for attr in aSet:
                if self.objects[obj][attr]==0 and attr in aSetC:
                    aSetC.remove(attr)
                 
        return list(aSetC)
    
    def attrPrime(self,aSet):
        #вычисление оператора штрих от множества признаков
        if aSet==[]:
            return list(range(self.nObj))
        oSet=[obj for obj in range(len(self.objects)) if self.objects[obj][aSet[0]]==1]
        oSetC=oSet[:]
        #print oSet, aSet
        for attr in aSet:
            for obj in oSet:
                #print obj,attr
                if self.objects[obj][attr]==0 and obj in oSetC:
                    oSetC.remove(obj)
        return list(oSetC)

    def oClosure(self,oSet):
        #вычисление объектного замыкания
        
        return self.attrPrime(self.objPrime(oSet))
    
    def aClosure(self,aSet):
        #вычисление признакового замыкания
        return self.objPrime(self.attrPrime(aSet))


def MyBiclusters(context):
    #вычисление всего множества бикластеров
    print("MyBicluster has been started")
    G=[g for g in range(context.nObj)]
    M=[m for m in range(context.nAttr)]
    oConcepts=[]
    aConcepts=[]
    biclSet=[]
    for g in G:
        b=(context.oClosure([g]),context.objPrime([g]))
        #print b
        #print b not in biclSet
        if b not in oConcepts:
            oConcepts.append(b)
    for a in M:
        b=(context.attrPrime([a]),context.aClosure([a]))
        #print b
        #print b not in biclSet
        if b not in aConcepts:
            aConcepts.append(b)
    
    for oc in oConcepts:
        for ac in aConcepts:
            #print oc
            #print ac
            #print isLess(oc[0],ac[0])
            if isLess(oc[0],ac[0]):
                #ошибка if (oc[0],ac[0]) not in biclSet:
                if (ac[0],oc[1]) not in biclSet:
                    biclSet.append((ac[0],oc[1]))
    print("MyBicluster has finished its job")                
    return biclSet

def denseBiclusters(biclset, context, threshold=0.5):
    #вычисление только плотных бикластеров
    return [bicl for bicl in biclset if calcDensity(context,bicl)>=threshold]

def denseBiclustersD(biclset, context, threshold=0.5):
    #вычисление только плотных бикластеров
    bD=[(calcDensity(context,bicl),bicl)  for bicl in biclset if calcDensity(context,bicl)>=threshold]
    bD.sort()
    bD.reverse()
    return bD
    
def greedyBiclusters(biclset, context, cover=0.5):
    #вычисление бикластеров с помощью жадной стратегии поиска
    #по покрытию отношения I
    I=[(o,a) for o in range(context.nObj) for a in range(context.nAttr) if context.objects[o][a]==1]
    sizeI=len(I)*1.0
    print('I',I)
    print('sizeI', sizeI)
    bD=[(calcDensity(context,bicl),bicl) for bicl in biclset]
    bD.sort()
    bD.reverse()

    cnt=0

    for bc in bD:
        for o in bc[1][0]:
            for a in bc[1][1]:
                if ((o,a) in I and context.objects[o][a]==1):
                    I.remove((o,a))
        cnt+=1
        print('len(I)',len(I))
        if len(I)/sizeI<=1-cover:
            print(len(I)/sizeI)
            break
    return bD[0:cnt+1]

    
    

 
    
def calcDensity(context, bicl):
    #вычисление плотности бикластера
    ro=0.0
    for o in bicl[0]:
        for i in bicl[1]:
            if context.objects[o][i]==1:
                ro+=1
    ro=ro/(len(bicl[0])*len(bicl[1]))
    
    return ro
                
        

def GaloisHierarchy(context):
    print("GaloisHierarchy has been started")
    #вычисление объектной и признаковой иерархии Галуа
    G=[g for g in range(context.nObj)]
    M=[m for m in range(context.nAttr)]
    oConcepts=[]
    aConcepts=[]
    biclSet=[]
    for g in G:
        b=(context.oClosure([g]),context.objPrime([g]))
        #print biclSet
        #print b
        #print b not in biclSet
        if b not in aConcepts and b not in oConcepts:
            oConcepts.append(b)
            
    for a in M:
        b=(context.attrPrime([a]),context.aClosure([a]))
        #print biclSet
        #print b
        #print b not in biclSet
        if b not in aConcepts and b not in oConcepts:
            aConcepts.append(b)

    
    conceptSet=[]
    conceptSet.extend(oConcepts)
    #conceptSet.extend([c for c in aConcepts if c not in oConcepts])
    conceptSet.extend(aConcepts)
    #print conceptSet

    print("GaloisHierarchy has finished its job")

    return conceptSet
    
    
            
        
def coverRelation(biclSet):
    #вычисление отношения покрытия
    #по вложению первой компоненты
  coverRel= [[] for b in biclSet]
  for i in xrange(len(biclSet)):
           for j in xrange(len(biclSet)):
               if i!=j and isLess(biclSet[j][0],biclSet[i][0]):
                   #print (biclSet[j][0],biclSet[i][0])
                   coverRel[j].append(i)
                   #print coverRel
                   for k in xrange(len(biclSet)):
                       if (isLess(biclSet[k][0],biclSet[i][0]) and
                           isLess(biclSet[j][0],biclSet[k][0]) and k!=i and k!=j ):
                           #print 'before',coverRel
                           coverRel[j].remove(i)
                           #print 'after', coverRel
                           break
  return coverRel

def coverBiRelation(biclSet):
    #вычисление отношения покрытия по вложению второй компоненты
  coverRel= [[] for b in biclSet]
  for i in xrange(len(biclSet)):
           for j in xrange(len(biclSet)):
               if i!=j and isLess(biclSet[j][0],biclSet[i][0]) and isLess(biclSet[j][1],biclSet[i][1]):
                   #print (biclSet[j][0],biclSet[i][0])
                   coverRel[j].append(i)
                   #print coverRel
                   for k in xrange(len(biclSet)):
                       if (isLess(biclSet[k][0],biclSet[i][0]) and isLess(biclSet[k][1],biclSet[i][1]) and
                           isLess(biclSet[j][0],biclSet[k][0]) and isLess(biclSet[j][1],biclSet[k][1]) and k!=i and k!=j ):
                           #print 'before',coverRel
                           coverRel[j].remove(i)
                           #print 'after', coverRel
                           break
  return coverRel  


def CRtoGraphViz(filename,CR,conceptSet,context,ro='no'):
    #записть отношения покрытия в dot файл
    f=open(filename,'w')
    f.write('digraph lattice\n')
    f.write('{\n')
    f.write('   // top to bottom\n')
    f.write('rankdir=TB;\n')
    f.write('concentrate=true;\n')
    f.write('edge [dir=back, arrowsize=0.75, color=black];\n')

    f.write('// top and bottom concepts\n')
    #f.write('node [shape=box, peripheries=2, style=filled];\n')
    #f.write(str(len(CR))+' 1\n')

    f.write('// inner concepts\n')
    f.write('node [shape=box, peripheries=1, color=black, style=solid];\n')

    f.write('// all concepts\n')
    print('context',context)
    print(ro,conceptSet)
    for c in range(len(conceptSet)-1,-1,-1):
        Ext=str([e+1 for e in conceptSet[c][0]]).replace('[','{').replace(']','}')
        
        Int=str([context.attr_names[attr] for attr in conceptSet[c][1]]).replace('[','{').replace(']','}').replace('"','')

        if ro=='no':
            f.write(str(c+1)+' [label="('+Ext+', '+Int+')"];\n')
        elif ro=='yes':
            f.write(str(c+1)+' [label="('+Ext+', '+Int+') ro=' + str(conceptSet[c][2])+'"];\n')
    

    f.write('// links between the concepts\n')
    for c in range(len(CR)):
        for p in CR[c]:
            f.write(str(p+1)+' -> '+str(c+1)+';\n')

    f.write('}\n')
    f.close()
 


    
def NextClosure(context):
    print("NextClosure has been started")
    #алгоритма Гантера для построения всех формальных понятий
    #
    L=[]
    A=[]
    G=[g for g in range(context.nObj)]
    M=[m for m in range(context.nAttr)]
    Mprime=context.attrPrime(M)
    if len(Mprime)==0:
        L.append((Mprime,M))
    g=max(G)
    cnt=0
    while A!=G:
        #print(type(A),A)
        A.append(g)
        #print '[...]',[h for h in A if g<h]
        A=substract(A,[h for h in A if g<h])
        
        clA=context.oClosure(A)
        H=[h for h in substract(clA,A) if h<g]
        if H==[]:
            cnt+=1
            L.append((clA,context.objPrime(A)))
            #print 'g=',g+1,'A=',[g+1 for g in A], 'A\'\'=',[g+1 for g in clA],'-->', [g+1 for g in L[-1][0]], [context.attr_names[attr] for attr in L[-1][1]]
            #print L
            if cnt%10==0 :print("I have just calculate concept number",cnt)
            H1=[h for h in substract(G,clA)]
            if H1!=[]: g=max(H1)
            A=list(clA[:])
            #print(type(clA[:]))
                       
        else:
            g=max([h for h in substract(G,A) if h<g])
    print("NextClosure has finished its job")
    return L
        
        

def substract(A,B):
    #вычитание множеств
    ret=list(A[:])
    #print(type(ret))
    for b in B:
        if b in A:
            ret.remove(b)
            
    return ret

def intersect(A,B):
    #пересечение множеств
    ret=[]
    for b in B:
        if b in A:
            ret.append(b)
            
    return ret

def isEqual(A,B):
    #провекра на равенство множеств
    for a in A:
        if a not in B:
            return False
    for b in B:
        if b not in A:
            return False
            
    return True

def isLess(A,B):
    #проверка на вложение
    for a in A:
        if a not in B:
            return False
            
    return True

def union(A,B):
    #объединение множеств
    union=[]
    union.extend(A)
    union.extend(B)
    union=list(set(union))
    return union

def isLessG(A,B):
    #"меньше чем" по Гантеру
    
    simS=substract(union(A,B),intersect(A,B))
    if simS!=[]:
        return min(simS) in B
    return False

def coverGraph(context,L):
    #граф покрытия
    E=[]
    cnt=0
    #print L
    for k in range(len(L)):
        lst=[]
        H=L[k][:]
        #print L
        for x in substract(range(context.nObj),H[0]):
            #print (intersect(context.objPrime([x]),H[1]))
            lst.append((intersect(context.objPrime([x]),H[1]), x))
       
        while lst!=[]:
            h=lst.pop(0)
            Ext=H[0][:]
            #print 'Ext=',Ext
            maximal=True
            lstC=lst[:]
            for e in lst:
                #print 'h.extent=',h[0],'e.extent',e[0]
                if isEqual(h[0],e[0]):
                    #print 'h.extent=',h[0],'e.extent',e[0]
                    Ext.append(e[1])
                    #print 'Ext=',Ext
                    #print L
                    lstC.remove(e)
                elif isLess(e[0],h[0]):
                    lstC.remove(e)
                elif isLess(h[0],e[0]):
                    maximal=False
                    break
            lst=lstC[:]
            if maximal==True:
                Ext.append(h[1])
                #print 'Ext=',Ext
                #print 'k=',k
                first=k+1
                last=len(L)-1
                C=L[0][:]
                while not isEqual(Ext,C[0]):
                    #print 'Ext=',Ext,"!=",'C.extent',C[0]
                    cur=(first+last)//2
                    #print('cur=',cur)
                    C=L[cur][:]
                    if isLessG(C[0],Ext):
                        #print 'isLess'
                        first=cur+1
                    else:
                        last=cur
                    
                E.append((L.index(C),L.index(H)))
                cnt+=1
                if cnt%100==0: print("I have just added edge number",cnt)
    return L,E
            
def CGtoGraphViz(filename,CG,context):
    #запись графа покрытия в dot файл
    f=open(filename,'w')
    f.write('digraph lattice\n')
    f.write('{\n')
    f.write('   // top to bottom\n')
    f.write('rankdir=TB;\n')
    f.write('concentrate=true;\n')
    f.write('edge [dir=back, arrowsize=0.75, color=black];\n')

    f.write('// top and bottom concepts\n')
    f.write('node [shape=box, peripheries=2, style=filled];\n')
    f.write(str(len(CG[0]))+' 1\n')

    f.write('// inner concepts\n')
    f.write('node [shape=box, peripheries=1, color=black, style=solid];\n')

    f.write('// all concepts\n')
    for c in range(len(CG[0])-1,-1,-1):
        Ext=str([e+1 for e in CG[0][c][0]]).replace('[','{').replace(']','}')
        
        Int=str([context.attr_names[attr] for attr in CG[0][c][1]]).replace('[','{').replace(']','}').replace('"','')
        
        f.write(str(c+1)+' [label="('+Ext+', '+Int+')"];\n')
    

    f.write('// links between the concepts\n')
    for pair in range(len(CG[1])-1,-1,-1):
        f.write(str(CG[1][pair][0]+1)+' -> '+str(CG[1][pair][1]+1)+';\n')

    f.write('}\n')
    f.close()

def calculateStability(context,coverGraph):
    #вычисление устойчивости
    L=coverGraph[0]
    E=coverGraph[1]
    count={}
    subsets={}
    stability={}
    for i in range(len(L)):
        #print 'concept=',L[i]
        count[i]=numberNeighbours(i,E)
        subsets[i]=2**len(L[i][0])
    concepts=L[:]
    #print count
    #print subsets
    #print stability
    while concepts!=[]:
        #print count
        for c in concepts:
            if count[L.index(c)]==0:
                
                concept=L.index(c)
                #print concept
                break
        stability[concept]=subsets[concept] / (2.0**len(L[concept][0]))
        #print 'concepts=',concepts, ' removed concept=',L[concept]
        concepts.remove(L[concept])
        for c in concepts:
            #print c,'isLess', L[concept],'???'
            if isLess(L[concept][0],c[0]):
                #print 'yes!'
                subsets[L.index(c)] = subsets[L.index(c)]-subsets[concept]
            #print 'neigbours',getNeighbours(L.index(c),E)
            if concept in getNeighbours(L.index(c),E):
                count[L.index(c)] = count[L.index(c)]-1
    #print count
    #print subsets
    #print stability
    return stability


def calculateStabilityAttr(context,coverGraph):
    #вычисление устойчивости
    L=coverGraph[0]
    E=coverGraph[1]
    count={}
    subsets={}
    stability={}
    attrSubsets={}
    contribVector={}
    
    for i in range(len(L)):
        #print 'concept=',L[i]
        count[i]=numberNeighboursDual(i,E)
        subsets[i]=2**len(L[i][1])
        attrSubsets[i]=[2**(len(L[i][1])-1) if x in L[i][1] else 0 for x in range(context.nAttr)]
        print ("attrSubsets for ", L[i], attrSubsets[i])
    concepts=L[:]
    #print count
    #print subsets
    #print stability
    while concepts!=[]:
        #print count
        for c in concepts:
            if count[L.index(c)]==0:
                
                concept=L.index(c)
                #print concept
                break
        stability[concept]=subsets[concept] / (2.0**len(L[concept][1]))

        contribVector[concept]=[attrSubsets[concept][i]/(2.0**(len(L[concept][1])-1)) for i in range(context.nAttr)]

        print(concept, contribVector[concept])

         
        #print 'concepts=',concepts, ' removed concept=',L[concept]
        concepts.remove(L[concept])
        for c in concepts:
            #print c,'isLess', L[concept],'???'
            if isLess(c[0],L[concept][0]):
                #print 'yes!'
                subsets[L.index(c)] = subsets[L.index(c)]-subsets[concept]
                #attrSubsets[L.index(c)]=[attrSubsets[L.index(c)][x]-attrSubsets[concept][x] if x in L[L.index(c)][1] else attrSubsets[L.index(c)][x] for x in range(context.nAttr)]
                attrSubsets[L.index(c)]=[attrSubsets[L.index(c)][x]-attrSubsets[concept][x] for x in range(context.nAttr)]
                #print ("attrSubsets for ", c, attrSubsets[L.index(c)])
            #print 'neigbours',getNeighbours(L.index(c),E)
            if concept in getNeighboursDual(L.index(c),E):
                count[L.index(c)] = count[L.index(c)]-1
    #print count
    #print subsets
    #print stability
    return stability, contribVector


def calculateStabilityDelta(context,coverGraph):
    #вычисление устойчивости
    L=coverGraph[0]
    E=coverGraph[1]
    count={}
    subsets={}
    stability={}
    attrSubsets={}
    contribVector={}
    
    for i in range(len(L)):
        #print 'concept=',L[i]
        count[i]=numberNeighboursDual(i,E)
        subsets[i]=2**len(L[i][1])
        attrSubsets[i]=[2**(len(L[i][1])-1) if x in L[i][1] else subsets[i] for x in range(context.nAttr)]
        print ("attrSubsets for ", L[i], attrSubsets[i])
    concepts=L[:]
    #print count
    #print subsets
    #print stability
    while concepts!=[]:
        #print count
        for c in concepts:
            if count[L.index(c)]==0:
                
                concept=L.index(c)
                #print concept
                break
        stability[concept]=subsets[concept] / (2.0**len(L[concept][1]))

        contribVector[concept]=[(subsets[concept] - 2*attrSubsets[concept][i])/(2.0**(len(L[concept][1])-1))  if i in L[concept][1] else 0 for i in range(context.nAttr)]

        print(concept, contribVector[concept])

         
        #print 'concepts=',concepts, ' removed concept=',L[concept]
        concepts.remove(L[concept])
        for c in concepts:
            #print c,'isLess', L[concept],'???'
            if isLess(c[0],L[concept][0]):
                #print 'yes!'
                subsets[L.index(c)] = subsets[L.index(c)]-subsets[concept]
                #attrSubsets[L.index(c)]=[attrSubsets[L.index(c)][x]-attrSubsets[concept][x] if x in L[L.index(c)][1] else attrSubsets[L.index(c)][x] for x in range(context.nAttr)]
                attrSubsets[L.index(c)]=[attrSubsets[L.index(c)][x]-attrSubsets[concept][x] for x in range(context.nAttr)]
                #print ("attrSubsets for ", c, attrSubsets[L.index(c)])
            #print 'neigbours',getNeighbours(L.index(c),E)
            if concept in getNeighboursDual(L.index(c),E):
                count[L.index(c)] = count[L.index(c)]-1
    #print count
    #print subsets
    #print stability
    return stability, contribVector    

def calculateMoebius(context,coverGraph):
    #вычисление устойчивости
    L=coverGraph[0]
    E=coverGraph[1]
    count={}
    subsets={}
    stability={}
    attrSubsets={}
    contribVector={}
    
    for i in range(len(L)):
        #print 'concept=',L[i]
        count[i]=numberNeighboursDual(i,E)
        subsets[i]=2**len(L[i][1])
        attrSubsets[i]=[2**(len(L[i][1])-1) if x in L[i][1] else subsets[i] for x in range(context.nAttr)]
        print ("attrSubsets for ", L[i], attrSubsets[i])
    concepts=L[:]
    #print count
    #print subsets
    #print stability
    while concepts!=[]:
        #print count
        for c in concepts:
            if count[L.index(c)]==0:
                
                concept=L.index(c)
                #print concept
                break
        stability[concept]=subsets[concept] / (2.0**len(L[concept][1]))

        contribVector[concept]=[(subsets[concept] - 2*attrSubsets[concept][i])/(2.0**(len(L[concept][1])-1))  if i in L[concept][1] else 0 for i in range(context.nAttr)]

        print(concept, contribVector[concept])

         
        #print 'concepts=',concepts, ' removed concept=',L[concept]
        concepts.remove(L[concept])
        for c in concepts:
            #print c,'isLess', L[concept],'???'
            if isLess(c[0],L[concept][0]):
                #print 'yes!'
                subsets[L.index(c)] = subsets[L.index(c)]-subsets[concept]
                #attrSubsets[L.index(c)]=[attrSubsets[L.index(c)][x]-attrSubsets[concept][x] if x in L[L.index(c)][1] else attrSubsets[L.index(c)][x] for x in range(context.nAttr)]
                attrSubsets[L.index(c)]=[attrSubsets[L.index(c)][x]-attrSubsets[concept][x] for x in range(context.nAttr)]
                #print ("attrSubsets for ", c, attrSubsets[L.index(c)])
            #print 'neigbours',getNeighbours(L.index(c),E)
            if concept in getNeighboursDual(L.index(c),E):
                count[L.index(c)] = count[L.index(c)]-1
    #print count
    #print subsets
    #print stability
    return stability, contribVector  




def writeStability2File(context,coverGraph,filename):
    #запись резульатов вычисления с индексом устойчивости в файл
    st=calculateStability(context,coverGraph)
    result = map(None, st.values(),st.keys( ))
    result.sort()
    result.reverse()
    
    f=open(filename,'w')
    for s,k in result:
        Ext=str([e+1 for e in coverGraph[0][k][0]]).replace('[','{').replace(']','}')
        Int=str([context.attr_names[attr] for attr in coverGraph[0][k][1]]).replace('[','{').replace(']','}').replace('"','')
        f.write('('+Ext+', '+Int+') '+str(st[k])+'\n')
    f.close()

def writeExt2File(context,coverGraph,filename):
    #запись результатов вычисления самых крупных понятия в файл
    exts=[(len(c[0]),c) for c in coverGraph[0]]
    exts.sort()
    exts.reverse()
    
    f=open(filename,'w')
    for n,c in exts:
        Ext=str([e+1 for e in c[0]]).replace('[','{').replace(']','}')
        Int=str([context.attr_names[attr] for attr in c[1]]).replace('[','{').replace(']','}').replace('"','')
        f.write('('+Ext+', '+Int+') '+str(n)+'\n')
    f.close()


def saveBicl2Mat(context, biclustersD,filename):
    #запись результатов вычисления плотных бикластеров в файл
        
    f=open(filename,'w')
    f.write('res={')
    for b in biclustersD:
        Ext=str([int(e)+1 for e in b[1][0]])
        Int=str([int(context.attr_names[attr]) for attr in b[1][1]])
        f.write(Ext+', '+Int+', '+str(b[0])+';')
    f.write('}')
    f.close()

def saveBicl2File(context, biclustersD,filename):
    #запись результатов вычисления плотных бикластеров в файл
        
    f=open(filename,'w')
    for b in biclustersD:
        Ext=str([int(e)+1 for e in b[1][0]]).replace('[','{').replace(']','}')
        Int=str([context.attr_names[attr] for attr in b[1][1]]).replace('[','{').replace(']','}').replace('"','')
        f.write('('+Ext+', '+Int+') '+str(b[0])+'\n')
    f.close()


def minHyp(posContext, negContext, L, coverGraph):
    hyps=[]
    global d 
    global h
    d = defaultdict(list)
    h = []
    for k, v in coverGraph:
        d[k].append(v)
    currPair=coverGraph[-1]
    candHyp=L[currPair[0]][1]

    if nextCandHyp(candHyp, posContext, negContext, L, coverGraph):
        if currPair[0] not in h:
            hyps.append(candHyp)
            h.append(currPair[0])
    else:
        if currPair[0] in d:
            hyps.extend(nextCandHyps(d[currPair[0]], posContext, negContext, L, coverGraph))


        # while currPair[0] in d: 
        #     for i in d[currPair[0]]:
        #         candHyp=L[i][1]
        #         if nextCandHyp(candHyp, posContext, negContext, L, coverGraph):
        #             hyps.append(candHyp)

    
    return hyps


def nextCandHyps(candHyps, posContext, negContext, L, coverGraph):
    hyps=[]
    for i in candHyps:
        candHyp=L[i][1]
        if nextCandHyp(candHyp, posContext, negContext, L, coverGraph):
            if i not in h:
                hyps.append(candHyp)
                h.append(i)
        else:
            if i in d:
                hyps.extend(nextCandHyps(d[i], posContext, negContext, L, coverGraph))

    return hyps

def reduceNonMinHyp(Hyps):
    Hyps=Hyps[:]
    rHyps=[]
    hfalse=False
    for h in Hyps:
        for f in  Hyps:
            if  isLess(f,h) and f!=h:
                #print("h=",h,"f=",f)
                hfalse=True
                break
        if not hfalse:
            rHyps.append(h)
            hfalse=False
        hfalse=False
    return rHyps



def nextCandHyp(candHyp, posContext, negContext, L, coverGraph):
    #print("candHyp",candHyp)
    #print("candHyp",int2names(posContext,candHyp))
    for g in range(negContext.nObj):
        negExInt=obj2Int(negContext,g)
        #print(int2names(negContext,negExInt))
        if isLess(candHyp,negExInt):
            #print("Negative example:", g)
            return False
    return True




def obj2Int(context,g):
    ret=[]
    for i in range(context.nAttr):
        if context.objects[g][i]==1:
            ret.append(i)
    return ret

def list2Int(lst):
    ret=[]
    for i in range(len(lst)):
        if lst[i]==1:
            ret.append(i)
    return ret



def int2names(context,intent):
    return    [context.attr_names[i] for i in intent]

def numberNeighbours(i,E):
    #вычислить число соседей
    n=0
    for e in E:
        if e[0]==i: n+=1
    return n

def numberNeighboursDual(i,E):
    #вычислить число соседей
    n=0
    for e in E:
        if e[1]==i: n+=1
    return n    

def getNeighbours(i,E):
    #построить список соседей
    n=[]
    for e in E:
        if e[0]==i: n.append(e[1])
    return n

def getNeighboursDual(i,E):
    #построить список соседей
    n=[]
    for e in E:
        if e[1]==i: n.append(e[0])
    return n    


def JSMClassifyer(ex,pHyps,nHyps):
    pos=False
    neg=False
    for p in pHyps:
        if isLess(p,ex):
            #print("pos",p)
            pos=True
    for n in nHyps:
        if isLess(n,ex):
            neg=True
            #print("neg",n)
    if pos:
        if neg:
            return 0
        else:
            return 1
    else:
        if neg:
            return -1
        else:
            return 0



class nnContext:
    def __init__(self, n=3, i=0):
            self.attr_names=[str(m+1) for m in range(n)]
            self.objects=[]
            bit=bin(i)[:1:-1]
            d=n**2-len(bit)
            if d>0:
                bit=bit+"0"*d           
            pos=0
            obj=[]            
            for s in bit:
                obj.append(int(s))
                pos=pos+1
                if pos % n == 0:
                    self.objects.append(obj)
                    obj=[]
            self.nAttr=len(self.attr_names)
            self.nObj=len(self.objects)

    def objPrime(self, oSet):
        #вычисление оператора штрих от множества объектов
        if oSet==[]:
            return list(range(self.nAttr))
        aSet=[attr for attr in range(len(self.objects[oSet[0]])) if self.objects[oSet[0]][attr]==1]
        aSetC=aSet[:]
        for obj in oSet:
            for attr in aSet:
                if self.objects[obj][attr]==0 and attr in aSetC:
                    aSetC.remove(attr)
                 
        return list(aSetC)
    
    def attrPrime(self,aSet):
        #вычисление оператора штрих от множества признаков
        if aSet==[]:
            return list(range(self.nObj))
        oSet=[obj for obj in range(len(self.objects)) if self.objects[obj][aSet[0]]==1]
        oSetC=oSet[:]
        #print oSet, aSet
        for attr in aSet:
            for obj in oSet:
                #print obj,attr
                if self.objects[obj][attr]==0 and obj in oSetC:
                    oSetC.remove(obj)
        return list(oSetC)

    def oClosure(self,oSet):
        #вычисление объектного замыкания
        
        return self.attrPrime(self.objPrime(oSet))
    
    def aClosure(self,aSet):
        #вычисление признакового замыкания
        return self.objPrime(self.attrPrime(aSet))






def all2GraphViz(filename):
    #все бикластеры, плотные бикластеры, иерархии Галуа, бикластеры жадного алгоритма
    #и решетка понятий выводятся в dot файлы
    c=Context(filename)
    print('context1',c)
    B=MyBiclusters(c)
    H=GaloisHierarchy(c)
    CR1=coverBiRelation(B)
    CR2=coverRelation(H)
    dB=denseBiclusters(B,  c, threshold=0.9)
    gB=greedyBiclusters(B, c, cover=1)            
    CR3=coverBiRelation(dB)
    gBs=[b[1] for b in gB]
    gBtriple=[(b[1][0],b[1][1],b[0]) for b in gB]
    print(gBtriple)
    CR4=coverBiRelation(gBs)
    print('context',c)

    CRtoGraphViz('biclusters_'+filename[:-4]+'.dot',CR1,B,c)
    CRtoGraphViz('dense_biclusters_'+filename[:-4]+'.dot',CR3,dB,c)
    CRtoGraphViz('GaloisHierarchy_'+filename[:-4]+'.dot',CR2,H,c)
    CRtoGraphViz('greedy_bicluster_'+filename[:-4]+'.dot',CR4,gBtriple,c,ro='yes')
    L=NextClosure(c)
    Gr=coverGraph(c,L)
    CGtoGraphViz('ConceptLattice_'+filename[:-4]+'.dot',Gr,c)
    


#all2GraphViz('BinaryVotingAtt.txt')
#c=Context('BinaryVotingAtt.txt')
#B=MyBiclusters(c)
#DB=denseBiclustersD(B, c, threshold=0)
#saveBicl2Mat(c, DB,'test.txt')
#H=GaloisHierarchy(c)
#CR1=coverRelation(B)
#CR2=coverRelation(H)
#CRtoGraphViz('BinaryVotingAtt.dot',CR2,H,c)
#L=NextClosure(c)
#Gr=coverGraph(c,L)
#CGtoGraphViz('BinaryVotingAtt.dot',Gr,c)
#writeStability2File(c,Gr,'2_i-stability.txt')
#writeExt2File(c,Gr,'2_ext.txt')

