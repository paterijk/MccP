import copy, math
class algMccP(object):
    def __init__(self, objects, relation, min, max, cut, bipolar):
        
        self.objects = objects
        self.N = len(objects)
        self.relation = relation
        self.min = min
        self.max = max
        self.cut = cut
        self.bipolar = bipolar
        
    def Run(self):
        
        cores = self.FindCores()
        clusters = self.ExpandCores(cores)
        
        results = {}
        for i in range(len(clusters)):
            for o in clusters[i]:
                results[o] = 'cluster_%d'%(i+1)
        
        return results
    
    def FindCores(self):
        
        max_cliques = self.EnumBK_K()
        
        perf_max_cliques = []
        for mc in max_cliques:
            perf = self.Fitness_Core(mc)
            perf_max_cliques.append([perf,mc])
        perf_max_cliques.sort(reverse = True)
        
        cores = []
        while perf_max_cliques:
            perf = perf_max_cliques[0][0]
            mc = perf_max_cliques[0][1]
            cores.append(mc)
            
            new_perf_max_cliques = []
            for pmc in perf_max_cliques[1:]:
                overlapping = False
                for o in mc:
                    if o in pmc[1]:
                        overlapping = True
                        break
                if not overlapping:
                    new_perf_max_cliques.append(pmc)
            
            perf_max_cliques = new_perf_max_cliques
            
        return cores
    
    def EnumBK_K(self):
        
        results = []
        self.IK_G([],set(self.objects),set(), results)
        
        return results

    def IK_G(self,R,P,X,MC):
        
        if len(P) == 0 and len(X) == 0:
            MC.append(R)
        else:
            if len(P) > 0:
                tempP = copy.deepcopy(P)
                OIN_v = set()
                for u in P:
                    OIN_u = self.OIN(u)
                    if len(OIN_u) > len(OIN_v):
                        OIN_v = OIN_u
                for u in P:
                    if not(u in OIN_v):
                        tempP.remove(u)
                        R1 = copy.deepcopy(R)
                        R1.append(u)
                        P1 = copy.deepcopy(tempP)
                        OIN_u = self.OIN(u)
                        P1 = tempP.intersection(OIN_u)
                        X1 = X.intersection(OIN_u)
                        self.IK_G(R1,P1,X1,MC)
                        X.add(u)
    
    def ExpandCores(self, cores):
        
        clusters = copy.deepcopy(cores)
        objects = copy.deepcopy(self.objects)
        for core in cores:
            for o in core:
                objects.remove(o)
        for o in objects:
            index = 0
            max_mm = -self.N - 1
            for i in range(len(cores)):
                mm = self.MIM(o,cores[i])
                if mm > max_mm:
                    max_mm = mm
                    index = i
            if max_mm > 0:
                clusters[index].append(o)
            else:
                clusters.append([o])
        
        return clusters
    
    #--------------- Additional Procedures -----------#
    def GetCrispRel(self, o, p):
        
        med = (self.min + self.max) / 2
        
        if self.cut == med:
            if self.relation[o][p] > self.cut:
                return +1
            elif self.relation[o][p] < self.cut:
                return -1
            else:
                return 0
        else:
            if not self.bipolar:
                if self.relation[o][p] >= self.cut:
                    return +1
                else:
                    return -1
            else:
                if self.relation[o][p] >= self.cut:
                    return +1
                if self.relation[o][p] <= med - (self.cut - med):
                    return -1
                else:
                    return 0
        
    def OIN(self, x):
        
        result = set()
        for o in self.objects:
            if o != x:
                if self.GetCrispRel(x,o) == 1 and self.GetCrispRel(o,x) == 1:
                    result.add(o)
                    
        return result
    
    def MIM(self, o, Y):
        
        mim = 0.0
        for p in Y:
            if o != p:
                if self.GetCrispRel(o,p) == 1 and self.GetCrispRel(p,o) == 1:
                    mim += 1.0
                elif self.GetCrispRel(o,p) == -1 or self.GetCrispRel(p,o) == -1:
                    mim -= 1.0
                    
        return mim
    
    def Fitness_Core(self, Y, PI = None):
        
        performance = 0.0
        
        if PI == None:
            PI = {}
            for o in self.objects:
                PI[o] = self.MIM(o, Y)
                
        for o in self.objects:
            if o in Y:
                performance += PI[o] / float(self.N)
            else:
                performance -= PI[o] / float(self.N)
        performance = (performance / (self.N) + 1.0) / 2.0
        
        return performance
    
    def Fitness_Object(self, y, Y, PI = None):
        
        performance = 0.0
        
        if PI == None:
            PI = {}
            for o in self.objects:
                PI[o] = self.MIM(o, Y)
                
        for o in self.objects:
            if o != y:
                if o in Y:
                    if self.GetCrispRel(o,y) == 1 and self.GetCrispRel(y,o) == 1:
                        performance += 1.0
                    elif self.GetCrispRel(o,y) == -1 or self.GetCrispRel(y,o) == -1:
                        performance -= 1.0
                else:
                    if self.GetCrispRel(o,y) == 1 and self.GetCrispRel(y,o) == 1:
                        performance -= 1.0
                    elif self.GetCrispRel(o,y) == -1 or self.GetCrispRel(y,o) == -1:
                        performance += 1.0
            
        performance = (performance / ((self.N) * self.N) + 1) / 2      
          
        return performance
    
    def Fitness_Partition(self, C):
        
        dist = 0.0
        
        for i in range(len(C)):
            Y = C[i]
            min = 0
            for k in range(len(Y)-1):
                for l in range(len(Y))[k+1:]:
                    if self.GetCrispRel(Y[k],Y[l]) == 1 and self.GetCrispRel(Y[l],Y[k]) == 1:
                        min += 1.0
                    elif self.GetCrispRel(Y[k],Y[l]) == -1 or self.GetCrispRel(Y[l],Y[k]) == -1:
                        min += 0.0
                    else:
                        min += 0.5
            dist += min
            for j in range(len(C))[i+1:]:
                Z = C[j]
                min = 0
                for k in range(len(Y)):
                    for l in range(len(Z)):
                        if self.GetCrispRel(Y[k],Z[l]) == 1 and self.GetCrispRel(Z[l],Y[k]) == 1:
                            min += 0.0
                        elif self.GetCrispRel(Y[k],Z[l]) == -1 or self.GetCrispRel(Z[l],Y[k]) == -1:
                            min += 1.0
                        else:
                            min += 0.5
                dist+=min
        dist /= (self.N * (self.N - 1)/2)
        
        return dist
