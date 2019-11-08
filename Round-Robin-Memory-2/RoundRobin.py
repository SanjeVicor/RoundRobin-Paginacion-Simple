#Librerias Externas
from xeger import Xeger
from terminaltables import AsciiTable

#modulos INTERNOS
import msvcrt
import subprocess as sp
import time
import re
import random
import numpy as np

#Librerias PERSONALES
from Process import Process
from calculator import makeOperation

#Variables GLOBALES


YSpace = 34
XSpace = 5
RAM = np.full((YSpace,XSpace),None)
Secundary = np.full((YSpace,XSpace),None)
endedList       = list() # Complementa la RAM
lockedList      = list()# Complementa la RAM
queueReady      = list()# Complementa la RAM
newList         = list() #Fuera de la RAM
suspendedList   = list()

globalClock = 0
executableProcess = None
excecution  = 0
lastID = 0
quantum = 0

"""
None = Vacio
0 = Sistema Operativo
#READY(1)    
#NEW(2)      
#LOCKED(3)   
#EXECUTION(4)
#ENDED(5)
#SUSPENDED(6)
"""

def main(n, q):
    global quantum
    global lastID
    quantum = q
    initSO()
    for id in range(n): #Crear procesos en lista de nuevos
        id += 1
        lastID = id
        addProcess(id)
    motor(n)

def initSO():
    global RAM
    YSpace = 2
    XSpace = 5
    SO  = np.full((YSpace,XSpace),0)
    RAM = np.append(SO,RAM).reshape((36,5))
        
def addProcess(id):
    global newList
    completeOperationMatch = r"(\x2d)?\d(\x2a|\x2b|\x2d|\x5e|\x2f|\x25)\d"
    x = Xeger(limit=5)
    operation = x.xeger(completeOperationMatch)
    TME = random.randint(7,18)
    size = random.randint(7,25)
    TASK = Process(id,operation,TME,0,size)
    TASK.setRemainingT(TME)
    newList.append(TASK)

def checkSpace(memoryRequired):
    #return booleano , cabe o no ?
    global RAM
    
    zz = np.where(RAM == None)
    x = zz[0]
    y = list(set(x))
    notAvailable = list()
    for e in y:
        for i in range(5):
            if RAM[e][i] != None:
                notAvailable.append(e)
                break
    
    for e in notAvailable:
        x  = np.delete(x, np.argwhere(x == e))
    """
    print(notAvailable)
    print(f"{len(x)} {memoryRequired} \n")
    print(x)
    print("\n")
    time.sleep(5)    
    """
    if len(x) >= memoryRequired:
        return True
    else :
        return False

def getSpaces():
    global RAM
    zz = np.where(RAM == None)
    x = zz[0] #Que filas hay disponibles
    x = list(set(x))
    x.sort()
    y = zz[1] #Que elementos en cada fila estan disponibles
    #print("tg")
    #print(y)
    #print("sdadsdsad")
    available = list()
    y = y.tolist() 
    #print(y)
    coord = 0
    notAvailable = list()
    for r in x:
        Available = True
        for i in range(5):
            if RAM[r][i] != None: 
                Available =  False
                notAvailable.append(r)
                break
        if Available:
            available.append([])
            for i in range(5):
                if RAM[r][i] == None:
                    available[coord].append(i)
            coord += 1
    #Limpiar x
    for e in notAvailable:
        x.remove(e)
    return x, available
            
def addToRAM(process):
    global RAM
    global newList
    global queueReady 
    raws , columns = getSpaces()#2 - Checar espacios en RAM 
    counter = 0
    z = process.getSize()
    i = 0
    
    for r in raws :
        if counter == process.getSize():
            break
        column = columns[i]
        i += 1
        page = list()
        for c in column:
            page.append([r,c])
            RAM[r][c] = process
            counter += 1
            if counter == process.getSize():
                break
        process.setListIndex(page)
    """
    print("\n")
    print(raws)
    print("\n")
    print(columns)
    print("\n")
    print(process.getListIndex())
    print("\n")
    print(process.getSize())
    print("\n")
    time.sleep(2)
    """
    queueReady.append(process)
    newList.remove(process)

def addPageToRAM(process):
    global RAM
    global suspendedList
    global queueReady 
    raws , columns = getSpaces()#2 - Checar espacios en RAM 
    counter = 0
    z = process.getLastPageSize()
    i = 0
    
    for r in raws :
        if counter == process.getLastPageSize():
            break
        column = columns[i]
        i += 1
        page = list()
        for c in column:
            page.append([r,c])
            RAM[r][c] = process
            counter += 1
            if counter == process.getLastPageSize():
                break
        process.setLasPage(page)
    process.setState(1)
    #queueReady.append(process)
    #suspendedList.remove(process)

def cleanRAM(executableProcess):
    global RAM
    global endedList
    
    elements = np.where(RAM == executableProcess, None, RAM)
    RAM = elements
                
def motor(n):
    global RAM
    global newList
    global endedList 
    global lockedList
    global queueReady 
    global executableProcess
    global lastID
    global suspendedList
    
    allList = newList  + lockedList + queueReady + suspendedList
    while len(allList) > 0 and not executableProcess:
        #Mientras la longitud de nuevos sea diferente de cero y RAM este "vacia"
        
        while len(newList ) != 0: 
            e = newList[0]
            if checkSpace(e.getSize()):
                addToRAM(e)
            else:
                break
        allList = newList  + lockedList + queueReady + suspendedList
        #3 - Ejecución e impresion
        if len(queueReady) > 0:
                while len(queueReady) > 0: 
                    executionState()
                    setStates()
                    
        if len(lockedList) > 0 or len(suspendedList) > 0:
            tmp = sp.call('cls',shell=True)
            while len(queueReady) == 0: 
                setStates()
                updateTimes()
                printTables()
                key = ''
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8')
                    key = key.lower()
                    if key == 'p':
                        print('Presiona la tecla "C" para continuar')
                        while True:
                            if msvcrt.kbhit():
                                key = msvcrt.getch().decode('utf-8')
                                key = key.lower()
                                if key == 'c':
                                    break
                    elif key == 'n':
                        lastID += 1
                        addProcess(lastID)
                        checkReady()
                    
                    elif key == "u":
                        pass
                        
                    elif key == 'b':
                        tmp = sp.call('cls', shell=True)
                        print('Presiona la tecla "C" para continuar')
                        getPCB()
                        while True:
                            if msvcrt.kbhit():
                                key = msvcrt.getch().decode('utf-8')
                                key = key.lower()
                                if key == 'c':
                                    break      
                        
                    elif key == 'm':
                        tmp = sp.call('cls', shell=True)
                        print('Presiona la tecla "C" para continuar')
                        printMemories()
                        #getRAM()
                        #print("\n")
                        #getSecundary()
                        while True:
                            if msvcrt.kbhit():
                                key = msvcrt.getch().decode('utf-8')
                                key = key.lower()
                                if key == 'c':
                                    break          
                    elif key == 's':
                        if len(lockedList) > 0:
                            addToSuspended()
                    elif key == 'u':
                        mainMemory = getMainMemory()
                        if len(mainMemory) > 0:
                            task = addToVirtualMemory()
                            for task in mainMemory:
                                if  checkSpaceSecundary(task.getLastPageSize()):
                                    removePageFromRAM(task)
                                    addToSecundary(task)
                                    task.setIsLastPageInVM(True)
                    elif key == 'r':
                        if len(suspendedList) > 0:
                            task = suspendedList[0]
                            if task.getIsLastPageInVM():
                                if  checkSpaceSecundary(task.getLastPageSize()):
                                    removePageFromVirtualMemory(task)
                                    addPageToRAM(task)
                                    queueReady.append(task)
                                    suspendedList.remove(task)
                                    task.setIsLastPageInVM(False)
                            else:
                                task.setState(1)
                                queueReady.append(task)
                                suspendedList.remove(task)
           
                time.sleep(1)
                tmp = sp.call('cls',shell=True)
        printTables()
    tmp = sp.call('cls',shell=True)
    printTables() 

def getRAM():
    global RAM
    tableData = list()
    line = ""
    for x in RAM:
        for e in x:
            if e != None and e != 0:
                if e.getState() ==4:
                    line += "\033[1;31;40m " + "[" + str(e.getId()) + ","  +str(e.getState())  +"]" +"\033[0m"
                elif e.getState() ==3:
                    line += "\033[0;37;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                elif e.getState() ==1:
                    line += "\033[0;35;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                elif e.getState() == 6:
                    line += "\033[0;33;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                else :
                    line += "[" + str(e.getId()) + ","  +str(e.getState()) + "]"
            elif e == 0:
                line += "SO  "
            else:
                line += str(e) + "  "
        #print(f"{line} \n")
        tableData.append(line)
        line = ""
    return tableData

def removePageFromRAM(process):
    global RAM
    positions = process.getLastPage()
    print(positions)
    for e in positions :
        RAM[e[0]][e[1]] = None 
        
def removePageFromVirtualMemory(process):
    global Secundary
    positions = process.getLastPage()
    #print(positions)
    #time.sleep(5)
    for e in positions :
        Secundary[e[0]][e[1]] = None 
        
def checkSpaceSecundary(memoryRequired):
    #return booleano , cabe o no ?
    global Secundary
    
    zz = np.where(Secundary == None)
    x = zz[0]
    y = list(set(x))
    notAvailable = list()
    for e in y:
        for i in range(5):
            if Secundary[e][i] != None:
                notAvailable.append(e)
                break
    
    for e in notAvailable:
        x  = np.delete(x, np.argwhere(x == e))
    """
    print(notAvailable)
    print(f"{len(x)} {memoryRequired} \n")
    print(x)
    print("\n")
    time.sleep(5)    
    """
    if len(x) >= memoryRequired:
        return True
    else :
        return False
"""
def addToSuspended():
    global suspendedList
    global lockedList
    if not checkSpaceSecundary(lockedList[0].getLastPageSize()):
        return False
    e = lockedList.pop(0)
    e.setState(6)
    suspendedList.append(e)
    return e
"""

def addToSuspended():
    global suspendedList
    global lockedList
    e = lockedList.pop(0)
    e.setState(6)
    suspendedList.append(e)

def addToVirtualMemory():
    mainMemory = getMainMemory()
    if not checkSpaceSecundary(mainMemory[0].getLastPageSize()):
        return False
    return mainMemory[0]

def addToSecundary(process):
    global Secundary 
    raws , columns = getSpacesSecundary()#2 - Checar espacios en Disco
    counter = 0
    z = process.getLastPageSize()
    i = 0
    
    for r in raws :
        if counter == process.getLastPageSize():
            break
        column = columns[i]
        i += 1
        page = list()
        for c in column:
            page.append([r,c])
            #page.append([0,0])
            Secundary[r][c] = process
            counter += 1
            if counter == process.getLastPageSize():
                break
        #print(page)
        #time.sleep(5)
        process.setLasPage(page)

def printMemories():
    global YSpace
    tableData = [['Memoria Principal',
                  'Memoria Secundaria']]
    ram = getRAM()
    secundary = getSecundary()
    
    for i in range(YSpace):
        tableData.append([ram[i],
                          secundary[i]])
        #print(ram[i])
        #print(secundary[i])
    
    table = AsciiTable(tableData)
    print(table.table)

def getSecundary():
    global Secundary
    tableData = list()
    line = ""
    for x in Secundary:
        for e in x:
            if e != None and e != 0:
                if e.getState() ==4:
                    line += "\033[1;31;40m " + "[" + str(e.getId()) + ","  +str(e.getState())  +"]" +"\033[0m"
                elif e.getState() ==3:
                    line += "\033[0;37;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                elif e.getState() ==1:
                    line += "\033[0;35;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                elif e.getState() == 6:
                    line += "\033[0;33;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                else :
                    line += "[" + str(e.getId()) + ","  +str(e.getState()) + "]"
            elif e == 0:
                line += "SO  "
            else:
                line += str(e) + "  "
        #print(f"{line} \n")
        tableData.append(line)
        line = ""
    return tableData

def getSpacesSecundary():
    global Secundary
    zz = np.where(Secundary == None)
    x = zz[0] #Que filas hay disponibles
    x = list(set(x))
    x.sort()
    y = zz[1] #Que elementos en cada fila estan disponibles
    #print("tg")
    #print(y)
    #print("sdadsdsad")
    available = list()
    y = y.tolist() 
    #print(y)
    coord = 0
    notAvailable = list()
    for r in x:
        Available = True
        for i in range(5):
            if Secundary[r][i] != None: 
                Available =  False
                notAvailable.append(r)
                break
        if Available:
            available.append([])
            for i in range(5):
                if Secundary[r][i] == None:
                    available[coord].append(i)
            coord += 1
    #Limpiar x
    for e in notAvailable:
        x.remove(e)
    return x, available

def getMainMemory():
    global lockedList
    global queueReady
    global suspendedList
    
    mainMemory = queueReady + suspendedList + lockedList
    return mainMemory

#-----------------------------------------------------------------------------------
def executionState():
    
    global excecution
    global executableProcess
    global queueReady
    global lastID
    global quantum
    
    completeOperationMatch = r"(\x2d)?\d(\x2a|\x2b|\x2d|\x5e|\x2f|\x25)\d"
    incrementTime = 1
    excecution = 1
    executableProcess = queueReady.pop(0)
    if executableProcess.getIsLastPageInVM():
        removePageFromVirtualMemory(executableProcess)
        addPageToRAM(executableProcess)
        executableProcess.setIsLastPageInVM(False)
    
    executableProcess.setState(4)
    quantumDone = False
    count = 0
    #executableProcess.setResult(0)
    key = ''

    if not executableProcess.getFirstServe():
        executableProcess.setFirstServe(True)
        #firstServeT =  executableProcess.getFirstServeClock() - executableProcess.getAT()
        firstServeT = globalClock - executableProcess.getArriveT()
        executableProcess.setFirstServeT( firstServeT )

    while executableProcess.getRemainingT() > 0:
        updateTimes()
        printTables()
        key = ''
        count += 1
        
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8')
            key = key.lower()
            
            if key == 'e':
                lockedList.append(executableProcess) 
                executableProcess = None
                setStates()
                time.sleep(1)
                break
            
            elif key == 'w':
                executableProcess.setError(True)
                executableProcess.setErrorMessage('Error')
                break
            
            elif key == 'p':
                print('Presiona la tecla "C" para continuar')
                while True:
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8')
                        key = key.lower()
                        if key == 'c':
                            break
       
            elif key == 'n':
                lastID += 1
                addProcess(lastID)
                checkReady()
            elif key == 'b':
                tmp = sp.call('cls', shell=True)
                print('Presiona la tecla "C" para continuar')
                getPCB()
                while True:
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8')
                        key = key.lower()
                        if key == 'c':
                            break      
            elif key == 'm':
                        tmp = sp.call('cls', shell=True)
                        print('Presiona la tecla "C" para continuar')
                        printMemories()
                        #getRAM()
                        #print("\n")
                        #getSecundary()
                        while True:
                            if msvcrt.kbhit():
                                key = msvcrt.getch().decode('utf-8')
                                key = key.lower()
                                if key == 'c':
                                    break            
            elif key == 's':
                if len(lockedList) > 0:
                    addToSuspended()
            elif key == 'u':
                mainMemory = getMainMemory()
                if len(mainMemory) > 0:
                    task = addToVirtualMemory()
                    for task in mainMemory:
                        if  checkSpaceSecundary(task.getLastPageSize()):
                            removePageFromRAM(task)
                            addToSecundary(task)
                            task.setIsLastPageInVM(True)
            elif key == 'r':
                if len(suspendedList) > 0:
                    task = suspendedList[0]
                    if task.getIsLastPageInVM():
                        if  checkSpaceSecundary(task.getLastPageSize()):
                            removePageFromVirtualMemory(task)
                            addPageToRAM(task)
                            queueReady.append(task)
                            suspendedList.remove(task)
                            task.setIsLastPageInVM(False)
                    else:
                        task.setState(1)
                        queueReady.append(task)
                        suspendedList.remove(task)
            
            """
            elif key == "u":
                if len(lockedList) > 0:
                    task = addToSuspended() #SOLO CAMBIA ESTA FUNCION
                    if task != False:
                        removePageFromRAM(task)
                        addToSecundary(task)
            """ 
        if (count == quantum) and (executableProcess.getRemainingT() > 0):
            quantumDone = True
            time.sleep(1)
            break
        time.sleep(1)
        tmp = sp.call('cls', shell=True)
    tmp = sp.call('cls', shell=True)
    
    if quantumDone:
        queueReady.append(executableProcess)
        executableProcess = None
        setStates()
        
        
    if key != 'e' and not quantumDone:
            

        if not executableProcess.getError():
            result = solveOperation(executableProcess)
            executableProcess.setResult(result)

        executableProcess.setEndingT(globalClock)
        executableProcess.setReturnT(executableProcess.getEndingT() - executableProcess.getArriveT())   
        endedList.append(executableProcess)
        cleanRAM(executableProcess)
        checkReady() 
        #print(f"Se ha limpiado : {executableProcess}")
        #print(RAM)
        #time.sleep(5)
    executableProcess = None
    excecution = 0
                
def solveOperation(process):
    
    operationList = []
    operationList = re.split(r"(\x2a|\x2b|\x2d|\x2f|\x5e|\x25)", process.getOperation())

    for word in operationList:
        if word == "":
            operationList.remove(word)

    result = makeOperation(operationList)
    return result
        
def addToQueueReadyLockedProcess(task):
    global lockedList
    global queueReady
    index = lockedList.index(task)
    #x = lockedList.pop(index)
    x = lockedList[index]
    x.setLockedT(0)
    queueReady.append(x)
    return index       
        
def checkReady():
    global queueReady
    global newList
    global lockedList
    global executableProcess
    a = 0
    if executableProcess != None:
        b = list()
        b.append(executableProcess)
        a = queueReady + lockedList + b
    else:
        a = queueReady + lockedList 
    while len(newList ) != 0: 
        e = newList[0]
        if checkSpace(e.getSize()):
            addToRAM(e)
        else:
            break
        
def updateTimes():
        
    global globalClock
    global lockedList
    global queueReady
    global executableProcess
    incrementTime = 1
    indexList = list()
    
    if len(queueReady) > 0:
        for e in queueReady:
            if not e.getFirstServe():
                e.addFirstServeClock()
            e.addWaitingT()

    if len(lockedList) > 0:
        for e in lockedList:
            e.setLockedT(e.getLockedT() +   incrementTime)
            e.addWaitingT()
            if e.getLockedT() % 10 == 0:
                e.setLockedT(0)
                indexList.append(addToQueueReadyLockedProcess(e))
    
    if indexList:
        for e in indexList:
            cleanLockedList(e)
            setStates()
        
    
                       
    if executableProcess:
        executableProcess.addServiceT()
        executableProcess.decrementRemaining()
        
    globalClock += incrementTime

def printRAM():
    getRAM()
        
def printTables():
    global globalClock
    global endedList
    global lockedList
    global queueReady
    global RAM
    global executableProcess
    global newList
    global suspendedList

    print("\n")
    print(f"[*] Temporizador Global --->  {globalClock}")
    print("\n")
    print(f"\n PROCESOS NUEVOS : {len(newList)}")
    if len(suspendedList) > 0:
        getSuspended()
    else:
        print("[-] No hay procesos suspendidos")
    print("\n")
    if len(lockedList) > 0:
        getLocked()
    else:
        print("[-] No hay procesos bloqueados")
    print("\n")
    if len(queueReady) > 0:
        getReady()
    else:
        print("[-] No hay procesos en memoria")
    print("\n")
    if len(endedList) > 0:
        getEnded()
    else:
        print("[-] No hay procesos terminados")
    if executableProcess :
        getExcecutable()

def getSuspended():
    global suspendedList
    print("\n TABLA DE SUSPENDIDOS ")
    tableData = [['ID',
                  "Tamaño de ultima pagina"]]
    for task in suspendedList:
        tableData.append([task.getId(),
                          str(task.getLastPageSize()) 
                          ])
    table = AsciiTable(tableData)
    print(table.table)
        
def getEnded():
    global endedList
    print("\n TABLA DE TERMINADOS ")
    tableData = [['ID',
                  'Op',
                  'R',
                  'H_Fin',
                  'H_lleg',
                  'T M E',
                  'T_Rest',
                  'T_Resp',
                  'T_Esp',
                  'T_Serv',
                  "T_Ret",
                  "Size",
                  "Pages"]]
    for task in endedList:
        if not task.getError():
            tableData.append([task.getId(),
                                task.getOperation(),
                                task.getResult(),
                                str(task.getEndingT()) + "'s",
                                str(task.getArriveT()) + "'s",
                                str(task.getTME()) + "'s",
                                str(task.getRemainingT()) + "'s",
                                str(task.getFirstServeT()) + "'s",
                                str(task.getWaitingT()) + "'s",
                                str(task.getServiceT()) + "'s",
                                str(task.getReturnT()) + "'s",
                                str(task.getSize()) ,
                                str(len(task.getListIndex())) 
                                ])
        else:
            tableData.append([task.getId(),
                                task.getOperation(),
                                task.getErrorMessage(),
                                str(task.getEndingT()) + "'s",
                                str(task.getArriveT()) + "'s",
                                str(task.getTME()) + "'s",
                                str(task.getRemainingT()) + "'s",
                                str(task.getFirstServeT()) + "'s",
                                str(task.getWaitingT()) + "'s",
                                str(task.getServiceT()) + "'s",
                                str(task.getReturnT()) + "'s",
                                str(task.getSize()) ,
                                str(len(task.getListIndex())) 
                                ])
    table = AsciiTable(tableData)
    print(table.table)

def getLocked():
    global lockedList
    print("\n TABLA DE BLOQUEADOS ")
    tableData = [['ID', 'Tiempo transcurrido en bloqueado']]
    for task in lockedList:
        tableData.append([task.getId(), str(task.getLockedT()) + "'s"])
    table = AsciiTable(tableData)
    print(table.table)

def getExcecutable():
    global executableProcess
    print("\nTABLA DE EJECUCION ")
    tableData = [['ID',
                  'Operación',
                  'Hora de llegada',
                  'Tiempo de respuesta',
                  'Tiempo Max. Esperado',
                  'Tiempo Restante',
                  'Tiempo de Servicio']]

    tableData.append([executableProcess.getId(),
                      executableProcess.getOperation(),
                      str(executableProcess.getArriveT()) + "'s",
                      str(executableProcess.getFirstServeT()) + "'s",                      
                      str(executableProcess.getTME()) + "'s",
                      str(executableProcess.getRemainingT()) + "'s",
                      str(executableProcess.getServiceT()) + "'s"
                      ])

    table = AsciiTable(tableData)
    print(table.table)
        
def getReady():
    global queueReady
    print("\nTABLA DE LISTOS ")
    tableData = [['ID', 'Tiempo Maximo Esperado', 'Tiempo Restante', 'Tiempo de Espera']]
    for pendingTask in queueReady:
        tableData.append([pendingTask.getId(),
                          str(pendingTask.getTME()) + "'s",
                          str(pendingTask.getRemainingT()) + "'s",
                          str(pendingTask.getWaitingT()) + "'s"])
    table = AsciiTable(tableData)
    print(table.table)
 
def cleanLockedList(e):
    global lockedList
    global queueReady
    x = lockedList.pop(e) 
        
def setStates():
    global queueReady
    global endedList
    global lockedList
    global executableProcess
    global newList
    for e in queueReady:
        e.setState(1)
    for e in newList:
        e.setState(2)
    for e in lockedList:
        e.setState(3)
    for e in endedList:
        e.setState(5)
    try:
        if executableProcess:
            executableProcess.setState(4)   
    except:
        pass
                
def getPCB():
    global queueReady
    global endedList
    global lockedList
    global executableProcess
    global newList
    global suspendedList
    
    x = list()
    setStates()
    
    if executableProcess:
        x.append(executableProcess)
        
    
    
    allProcesses = queueReady + endedList + lockedList + x + newList + suspendedList
    allProcesses.sort(key=lambda x: x.id, reverse=False)
    print("\n TABLA PCB ")
    tableData = [['ID',
                  'Estado',
                  'Op',
                  'R',
                  "T_Rest_Bloq",
                  'H_Fin',
                  'H_lleg',
                  'T M E',
                  'T Rest',
                  'T Resp',
                  'T_Esp',
                  'T_Serv',
                  "T_Ret",
                  "Size"]]
    
    for e in allProcesses:
        if e.getState() ==1:
            tableData.append(getReadyAttributes(e))
        elif e.getState() ==2:
            tableData.append(getNewTaskAttributes(e))
        elif e.getState() ==3:
            tableData.append(getLockedAttributes(e))
        elif e.getState() ==4:
            tableData.append(getExcecutableAttributes(e))
        elif e.getState() ==5:
            tableData.append(getEndedAttributes(e))
        elif e.getState() ==6:
            tableData.append(getSuspendedAttributes(e))

    table = AsciiTable(tableData)
    print(table.table)

def getSuspendedAttributes(task):
    tableData = list()
    tableData=([task.getId(),
                       'Suspendido',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        "-",
                        str(task.getSize()) 
                        ])
    return tableData

def getReadyAttributes(task):
    tableData = list()
    if task.getFirstServe():
        tableData=([task.getId(),
                           'Listo',
                            task.getOperation(),
                            '-',
                            '-',
                            '-',
                            str(task.getArriveT()) + "'s",
                            str(task.getTME()) + "'s",
                            str(task.getRemainingT()) + "'s",
                            str(task.getFirstServeT()) + "'s",
                            str(task.getWaitingT()) + "'s",
                            str(task.getServiceT()) + "'s",
                            "-",
                            str(task.getSize()) 
                            ])
    else:
        tableData=([task.getId(),
                           'Listo',
                            task.getOperation(),
                            '-',
                            '-',
                            '-',
                            str(task.getArriveT()) + "'s",
                            str(task.getTME()) + "'s",
                            str(task.getRemainingT()) + "'s",
                            "-",
                            str(task.getWaitingT()) + "'s",
                            "-",
                            "-",
                            str(task.getSize()) 
                            ])
    return tableData

def getNewTaskAttributes(task):#Nuevos
    tableData = list()
    tableData=([task.getId(),
                       'Nuevo',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        '-',
                        "-",
                        str(task.getSize()) 
                        ])
    return tableData

def getEndedAttributes(task):
    tableData = list()
    if not task.getError():
        tableData=([task.getId(),
                            'Terminado',
                            task.getOperation(),
                            task.getResult(),
                            '-',
                            str(task.getEndingT()) + "'s",
                            str(task.getArriveT()) + "'s",
                            str(task.getTME()) + "'s",
                            str(task.getRemainingT()) + "'s",
                            str(task.getFirstServeT()) + "'s",
                            str(task.getWaitingT()) + "'s",
                            str(task.getServiceT()) + "'s",
                            str(task.getReturnT()) + "'s",
                            str(task.getSize()) 
                            ])
    else:
        tableData=([task.getId(),
                            'Terminado con error',
                            task.getOperation(),
                            task.getErrorMessage(),
                            '-',
                            str(task.getEndingT()) + "'s",
                            str(task.getArriveT()) + "'s",
                            str(task.getTME()) + "'s",
                            str(task.getRemainingT()) + "'s",
                            str(task.getFirstServeT()) + "'s",
                            str(task.getWaitingT()) + "'s",
                            str(task.getServiceT()) + "'s",
                            str(task.getReturnT()) + "'s",
                            str(task.getSize()) 
                            ])

    return tableData

def getLockedAttributes(task):
    tableData = list()
    tableData=([task.getId(),
                       'Bloqueado',
                        task.getOperation(),
                        '-',
                        str(10 - task.getLockedT()) + "'s",
                        '-',
                        str(task.getArriveT()) + "'s",
                        str(task.getTME()) + "'s",
                        str(task.getRemainingT()) + "'s",
                        str(task.getFirstServeT()) + "'s",
                        str(task.getWaitingT()) + "'s",
                        str(task.getServiceT()) + "'s",
                        "-",
                            str(task.getSize()) 
                        ])
    return tableData

def getExcecutableAttributes(task):
    tableData = list()
    tableData=([task.getId(),
                       'Ejecucion',
                        task.getOperation(),
                        '-',
                        '-',
                        '-',
                        str(task.getArriveT()) + "'s",
                        str(task.getTME()) + "'s",
                        str(task.getRemainingT()) + "'s",
                        str(task.getFirstServeT()) + "'s",
                        str(task.getWaitingT()) + "'s",
                        str(task.getServiceT()) + "'s",
                        "-",
                            str(task.getSize()) 
                        ])
    return tableData
    
            
        