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
VirtualMemory = np.full((36,XSpace),None)

endedList   = list() # Complementa la RAM
lockedList  = list()# Complementa la RAM
queueReady  = list()# Complementa la RAM
newList     = list() #Fuera de la RAM
DISK        = list()

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
#------------------------------------------------------- RAM
def checkSpace(memoryRequired):
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
    #print(x)
    #print(len(x))
    #print(memoryRequired)
    #time.sleep(2)
    if len(x) >= memoryRequired:
        #print("Permitido") 
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
    available = list()
    y = y.tolist() 
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

    queueReady.append(process)
    newList.remove(process)

def diskToRAM(process):
    global RAM
    global DISK
    global queueReady 
    raws , columns = getSpaces()
    counter = 0
    z = process.getSize()
    i = 0
    process.setNewListIndex()
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
    process.setState(1)

def cleanRAM(executableProcess):
    global RAM
    global endedList
    
    elements = np.where(RAM == executableProcess, None, RAM)
    RAM = elements
                
def getRAM():
    global RAM
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
                else :
                    line += "[" + str(e.getId()) + ","  +str(e.getState()) + "]"
            elif e == 0:
                line += "SO  "
            else:
                line += str(e) + "  "
        print(f"{line} \n")
        line = ""

def removePageFromRAM(page):
    global RAM
    for element in page:
        RAM[element[0]][element[1]] = None

def returnPagesToRAM(process, totalPages, pages):
    global RAM
    raws , columns = getSpaces()
    counter = 0
    i = 0
    for i in range(totalPages):
        r = raws[i]
        column = columns[i]
        p = len(pages[i])
        page = list()
        for x in range(p):
            c = column[x]
            page.append([r,c])
            RAM[r][c] = process
        process.setLastPage(page) 
         
        
def getRAM():
    global RAM
    tableData = list()
    line = ""
    i=0
    for x in RAM:
        if i < 10:
            line+=str(i) + "  "
        else:
            line+=str(i) + " "
        for e in x:
            if e != None and e != 0:
                if e.getState() ==4:
                    line += "\033[1;31;40m " + "[" + str(e.getId()) + ","  +str(e.getState())  +"]" +"\033[0m"
                elif e.getState() ==3:
                    line += "\033[0;37;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                elif e.getState() ==1:
                    line += "\033[0;35;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                else :
                    line += "[" + str(e.getId()) + ","  +str(e.getState()) + "]"
            elif e == 0:
                line += " SO   "
            else:
                line +=" " +str(e) + "  "
                
        i+=1
        tableData.append(line)
        line = "" 
    return tableData
#--------------------------------------------------------- DISK
def updateDisk():
    global DISK
    f= open("procesos.txt","w+")
    for task in DISK:
            taskId ="ID : " + str(task.getId()) + "\n"
            size = "Tamaño : "+str(task.getSize()) + "\n"
            f.write(taskId)
            f.write(size)
    f.close()
#--------------------------------------------------------- Virtual Mmemory

def checkSpaceVrM(memoryRequired):
    global VirtualMemory
    
    zz = np.where(VirtualMemory == None)
    x = zz[0]
    y = list(set(x))
    notAvailable = list()
    for e in y:
        for i in range(5):
            if VirtualMemory[e][i] != None:
                notAvailable.append(e)
                break
    
    for e in notAvailable:
        x  = np.delete(x, np.argwhere(x == e))
    """
    print(len(x))
    print(len(memoryRequired))
    print(x)
    print(zz)
    """
    
    if len(x) >= len(memoryRequired):
        return True
    else :
        return False

def getSpacesVrM():
    global VirtualMemory
    zz = np.where(VirtualMemory == None)
    x = zz[0] #Que filas hay disponibles
    x = list(set(x))
    x.sort()
    y = zz[1] #Que elementos en cada fila estan disponibles
    available = list()
    y = y.tolist() 
    coord = 0
    notAvailable = list()
    
    for r in x:
        Available = True
        for i in range(5):
            if VirtualMemory[r][i] != None: 
                Available =  False
                notAvailable.append(r)
                break
        if Available:
            available.append([])
            for i in range(5):
                if VirtualMemory[r][i] == None:
                    available[coord].append(i)
            coord += 1
 
    for e in notAvailable:
        x.remove(e)
    return x, available

def addPageToVrM(page, process):
    global VirtualMemory 
    raws , columns = getSpacesVrM()
    counter = 0
    z = len(page)
    i = 0 
    
    for r in raws :
        if counter == z:
            break
        column = columns[i]
        i += 1
        newPage = list()
        for c in column:
            newPage.append([r,c]) 
            VirtualMemory[r][c] = process
            counter += 1
            if counter == z:
                break  
    #print(newPage)
    #time.sleep(5)
    return newPage
    
def getVrM():
    global VirtualMemory
    tableData = list()
    line = ""
    i=0
    for x in VirtualMemory:
        if i < 10:
            line+=str(i) + "  "
        else:
            line+=str(i) + " "
            
        for e in x:
            if e != None and e != 0:
                if e.getState() ==4:
                    line += "\033[1;31;40m " + "[" + str(e.getId()) + ","  +str(e.getState())   +"]" +"\033[0m"
                elif e.getState() ==3:
                    line += "\033[0;37;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                elif e.getState() ==1:
                    line += "\033[0;35;40m " + "[" + str(e.getId()) + "," + str(e.getState())  + "]" +"\033[0m"
                else :
                    line += "[" + str(e.getId()) + ","  +str(e.getState()) + "]"
            else:
                line +=" " + str(e) + "  "
     
        i+=1
        tableData.append(line)
        line = ""
    return tableData

def removePageFromVirtualMemory(process):
    global VirtualMemory 
    for x in range(36) :
        for y in range(5):
            if  VirtualMemory[x][y] == process:
                VirtualMemory[x][y] = None 

#-----------------------------------------------------------------------------------
def motor(n):
    global RAM
    global newList
    global endedList 
    global lockedList
    global queueReady 
    global executableProcess
    global lastID
    tmp = sp.call('cls', shell=True)
    allList = newList  + lockedList + queueReady + DISK
    
    while len(allList) > 0 and not executableProcess:
        #Mientras la longitud de nuevos sea diferente de cero y RAM este "vacia"
        
        while len(newList ) != 0: 
            e = newList[0]
            if checkSpace(e.getSize()):
                addToRAM(e)
            else:
                break
        allList = newList  + lockedList + queueReady + DISK
        #3 - Ejecución e impresion
        if len(queueReady) > 0:
                while len(queueReady) > 0: 
                    executionState()
                    setStates()
                    
        if len(lockedList) > 0 or len(DISK) > 0:
            tmp = sp.call('cls',shell=True)
            while len(queueReady) == 0: 
                setStates()
                updateTimes()
                printTables()
                key = ''
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8')
                    key = key.lower()
                    
                    if keyController(key):
                        break
            
                time.sleep(1)
                tmp = sp.call('cls',shell=True)
        printTables()
    tmp = sp.call('cls',shell=True)
    printTables() 

def keyController(key):
    global lastID
    global DISK
    global executableProcess
    global newList
    global VirtualMemory
    
    if key == 'e':
        lockedList.append(executableProcess) 
        executableProcess = None
        setStates()
        time.sleep(1)
        return True
    
    elif key == 'w':
        executableProcess.setError(True)
        executableProcess.setErrorMessage('Error')
        return True
    
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
                getmemoriesData()
                while True:
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8')
                        key = key.lower()
                        if key == 'c':
                            break      
                              
    elif key == 's':
        if len(lockedList) > 0:
            task = lockedList.pop(0)
            task.setState(6)
            DISK.append(task)
            updateDisk()
            cleanRAM(task)
            while len(newList ) != 0: 
                e = newList[0]
                if not checkSpace(e.getSize()):
                    break
                else:
                    e.setState(1)
                    addToRAM(e)
    
    elif key == 'r':
        if len(DISK) > 0:
            task = DISK[0]
            if  checkSpace(task.getSize()):
                queueReady.append(task)
                DISK.remove(task)
                updateDisk()
                diskToRAM(task)
                task.setState(1)
    
    elif key == 'u':
        for e in queueReady:
            if len(e.getListIndex()) > 0:
                page = e.getLastPage()
                if checkSpaceVrM(page):
                    if not e.getProcessInVrM():
                        e.setNewVrMIndex()
                    e.setProcessInVrM(True)
                    removePageFromRAM(page)
                    newPage = addPageToVrM(page, e)
                    e.replacePage(newPage)
                    e.RAMtoVrM()
                    checkReady()
                #else:
                #    print("-----------------------------------------No hay memoria disponible")
                #    print(page)           
                #    print(VirtualMemory)
                #    time.sleep(5)   
            #else:
                #print("------------------------------------------------No hay paginas")
                #print(e.getId())
                #print(e.getListIndex())           
                #time.sleep(5)     
     
                                      
def executionState():
    global excecution
    global executableProcess
    global queueReady
    global quantum 
    
    completeOperationMatch = r"(\x2d)?\d(\x2a|\x2b|\x2d|\x5e|\x2f|\x25)\d"
    incrementTime = 1
    excecution = 1
    
    for i in range(len(queueReady)):
        e = queueReady[i]
        if  e.getProcessInVrM():
            pages = e.getVrM()
            requiredSpace = 0
            for p in pages:
                requiredSpace += len(p)
            if checkSpace(requiredSpace): 
                removePageFromVirtualMemory(e)
                returnPagesToRAM(e, len(pages), pages)
                executableProcess = queueReady.pop(i)
                executableProcess.setNewVrMIndex()
                break
        else:
            executableProcess = queueReady.pop(i)
            break
        
    executableProcess.setState(4)
    executableProcess.setProcessInVrM(False)
    quantumDone = False
    count = 0
 
    key = ''

    if not executableProcess.getFirstServe():
        executableProcess.setFirstServe(True) 
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
            if keyController(key):
                break
            
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
        removePageFromVirtualMemory(executableProcess)
        checkReady()
        
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
            e.setState(1)
            addToRAM(e)
        else:
            break
        
def updateTimes():
        
    global globalClock
    global lockedList
    global queueReady
    global executableProcess
    global DISK
    
    incrementTime = 1
    indexList = list()
    
    if len(queueReady) > 0:
        for e in queueReady:
            if not e.getFirstServe():
                e.addFirstServeClock()
            e.addWaitingT()
            
    if len(DISK) > 0:
        for e in DISK:
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
        
def printTables():
    global globalClock
    global endedList
    global lockedList
    global queueReady
    global RAM
    global executableProcess
    global newList
    global DISK

    print("\n")
    print(f"[*] Temporizador Global --->  {globalClock}")
    print("\n")
    print(f"\n PROCESOS NUEVOS : {len(newList)}")
    if len(DISK) > 0:
        getDisk()
    else:
        print("[-] No hay procesos suspendidos") 
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
    
    getmemoriesData()
    
    if executableProcess :
        getExcecutable()

def getmemoriesData():
    global newList
    print("\n Siguiente Proceso en entrar ")
    tableData = [['Proceso Nuevo', 'Memoria Principal','Memoria Principal', 'Memoria Virtual', 'Memoria Virtual']] 
    try:
        task = newList[0] 
        dataProcess1 = f"ID : {task.getId()}"
        dataProcess2 = f"Tamaño : {task.getSize()}"
    except:
        dataProcess1 = f""
        dataProcess2 = f""
    ram = getRAM()
    VrM = getVrM()
    i = 0
    while(i < 36):
        if i == 0:
            tableData.append([dataProcess1, 
                          ram[i],
                          ram[i+1],
                          VrM[i],
                          VrM[i+1]
                          ])
        elif i == 2:
            tableData.append([dataProcess2, 
                          ram[i],
                          ram[i+1],
                          VrM[i],
                          VrM[i+1]
                          ])
        else:
            tableData.append(["", 
                            ram[i],
                            ram[i+1],
                            VrM[i],
                            VrM[i+1]
                            ])
        i+=2
    table = AsciiTable(tableData)
    print(table.table)
    
def getDisk():
    global DISK
    print("\n TABLA DE SUSPENDIDOS ")
    tableData = [['ID',
                  "Espacio requerido"]]
    for task in DISK:
            tableData.append([task.getId(),
                            str(task.getSize()) 
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
                          str(pendingTask.getWaitingT()) + "'s"
                          ])
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
    global DISK
    
    for e in queueReady:
        e.setState(1)
    for e in newList:
        e.setState(2)
    for e in lockedList:
        e.setState(3)
    for e in endedList:
        e.setState(5)
    for e in DISK:
        e.setState(6)
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
    global DISK
    
    x = list()
    setStates()
    
    if executableProcess:
        x.append(executableProcess)
        
    
    
    allProcesses = queueReady + endedList + lockedList + x + newList +DISK
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
        if e.getState() ==1 :
            tableData.append(getReadyAttributes(e))
        elif e.getState() ==2:
            tableData.append(getNewTaskAttributes(e))
        elif e.getState() ==3:
            tableData.append(getLockedAttributes(e))
        elif e.getState() ==4:
            tableData.append(getExcecutableAttributes(e))
        elif e.getState() ==5:
            tableData.append(getEndedAttributes(e))
        elif e.getState() == 6:
            tableData.append(getSuspendedAttributes(e))
            

    table = AsciiTable(tableData)
    print(table.table)

def getSuspendedAttributes(task):
    tableData = list()
    tableData=([task.getId(),
                       'Suspendido',
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
    
            
        