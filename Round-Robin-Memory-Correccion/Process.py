
import time
class Process:
    def __init__(self,id,operation,TME,other=0,size=1,status=1):
        self.id             = id
        self.operation      = operation
        self.result         = '-'
        self.TME            = TME
        self.remainingT     = other
        self.lockedT        = other
        self.arriveT        = other
        self.endingT        = other
        self.firstServeT    = other
        self.waitingT       = other
        self.serviceT       = other
        self.returnT        = other
        self.FSClk          = other
        self.error          = False
        self.firstServe     = False
        self.size           = size
        self.state          = status
        self.status         = status
        self.RAMlist        = list()
        self.VrMlist        = list()
        self.isProcessInVrM = False
    
    def replacePage(self, page):
        self.RAMlist[-1] = page
        
    def setProcessInVrM(self, itIs):
        self.isProcessInVrM = itIs
        
    def getProcessInVrM(self):
        return self.isProcessInVrM
    
    def setNewVrMIndex(self): 
        self.VrMlist = []
        
    def getLastPage(self):
        #print(self.RAMlist)
        #time.sleep(5)
        return self.RAMlist[-1]
    
    def setLastPage(self,p):
        self.RAMlist.append(p)
        self.RAMlist.sort(reverse=True, key=lambda x:len(x) )
        #print(self.RAMlist)
        #time.sleep(1)
        
    def RAMtoVrM(self):
        page = self.RAMlist.pop(-1)
        self.VrMlist.append(page)
    
    def getVrM(self):
        return self.VrMlist
    
    def N_pagesInVrM(self):
        return len(self.VrMlist)
    
    def N_pagesInRAM(self):
        return len(self.RAMlist)
        
    def setNewListIndex(self):
        self.RAMlist = []
        
    def setListIndex(self, position):
        self.RAMlist.append(position)
    
    def getListIndex(self):
        return self.RAMlist
    
    def getId(self):
        return self.id
    
    def getSize(self):
        return self.size
    
    def getOperation(self):
        return self.operation
    
    def getTME(self):
        return self.TME
    
    def setResult(self, result):
        self.result = result
    
    def getResult(self):
        return self.result
    
    def setErrorMessage(self, message):
        self.errorMessage = message
    
    def getErrorMessage(self):
        return self.errorMessage
    
    def getStatus(self):
        return self.status

    def setStatus(self,status):
        self.status = status

    def setError(self, error):
        self.error = error
    
    def getError(self):
        return self.error 
    
    def setFirstServe(self, FS): #Flag
        self.firstServe = FS
    
    def getFirstServe(self):
        return self.firstServe

    def setState(self,st):
        self.state = st
    
    def getState(self):
        return self.state
    
# -------------- TIMES ----------------------

    def getRemainingT(self):
        return self.remainingT
    
    def setRemainingT(self, RT):
        self.remainingT = RT
    
    def decrementRemaining(self):
        self.remainingT -= 1
    
    def getLockedT(self):
        return self.lockedT
    
    def setLockedT(self,lt):
        self.lockedT = lt
        
    def getArriveT(self):
        return self.arriveT
    
    def setArriveT(self,at):
        self.arriveT = at
    
    def getEndingT(self):
        return self.endingT
    
    def setEndingT(self,et):
        self.endingT = et
    
    def getFirstServeT(self):
        return self.firstServeT
    
    def setFirstServeT(self,fst):
        self.firstServeT = fst
    
    def getWaitingT(self):
        return self.waitingT
    
    def setWaitingT(self,wt):
        self.waitingT = wt
    
    def addWaitingT(self):
        self.waitingT += 1
    
    def getServiceT(self):
        return self.serviceT
    
    def setServiceT(self,st):
        self.serviceT = st
    
    def addServiceT(self):
        self.serviceT += 1
    
    def getReturnT(self):
        return self.returnT
    
    def setReturnT(self,rt):
        self.returnT = rt
    
    def addFirstServeClock(self):
        self.FSClk += 1
    
    def getFirstServeClock(self):
        return self.FSClk