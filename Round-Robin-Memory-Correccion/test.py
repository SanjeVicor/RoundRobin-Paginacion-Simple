
import numpy as np

YSpace = 2
XSpace = 5
SO = np.full((YSpace,XSpace),0)
YSpace = 34
XSpace = 5
RAM = np.full((YSpace,XSpace),None)

RAM = np.append(SO,RAM).reshape((36,5))
RAM[2][1] = 5
print(RAM)

#Cuales estan vacias
#Usar solo x, y es inservible
zz = np.where(RAM == None)
x = zz[0]
y = zz[1]
#x = np.reshape(x,(34,5))
#y = np.reshape(y,(34,5))
print("\n")
print(x)
#print(y)
print(len(x))

available = list()
i = -1
for e in y:
    if e == 0:
        available.append([])
        i +=1 
    available[i].append(e)

print(available)
print(len(available))

x = list(set(x))
print("\n")
print(x)

print(RAM)