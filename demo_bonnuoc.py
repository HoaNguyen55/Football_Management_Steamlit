import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

def MuCf(x):
    if 0 <= x and x <= 1:
        return 0
    elif 1 < x and x <= 2:
        return x - 1

def MuCm(x):
    if 0 <= x and x <= 1:
        return x
    elif 1 < x and x <= 2:
        return 2 - x

def MuCe(x):
    if 0 <= x and x <= 1:
        return 1 - x
    elif 1 < x and x <= 2:
        return 0

C = np.linspace( 0,2 )
Cf = [MuCf(x) for x in C]
Cm = [MuCm(x) for x in C]
Ce = [MuCe(x) for x in C]

plt.plot( C, Cf )
plt.plot( C, Cm )
plt.plot( C, Ce )
plt.show()

def MuTf(y):
    if 0 <= y and y <= 1:
        return y
    elif 1 <= y and y <= 2:
        return 1

def MuTe(y):
    if 0 <= y and y <= 1:
        return 1 - y
    elif 1 <= y and y <= 2:
        return 0

T = np.linspace( 0,2 )
Tf = [MuTf(y) for y in T]
Te = [MuTe(y) for y in T]

plt.plot( T, Cf )
plt.plot( T, Ce )
plt.show()

def MuL(t):
    if 0 <= t and t <= 20:
        return 0
    elif 20 <= t and t <= 30:
        return (t - 20)/10

def MuM(t):
    if 0 <= t and t <= 10:
        return t/10
    elif 10 <= t and t <= 20:
        return 1
    elif 20 <= t and t <= 30:
        return (30 - t)/10

def MuS(t):
    if 0 <= t and t <= 10:
        return 1 - t/10.
    elif 10 <= t and t <= 30:
        return 0

Tg = np.linspace( 0,30 )
L = [MuL(t) for t in Tg]
M = [MuM(t) for t in Tg]
S = [MuS(t) for t in Tg]

x0, y0 = 1.2, 0.5
w1 = min( MuTf(y0),MuCf(x0))
w2 = min( MuTf(y0),MuCm(x0))
w3 = min( MuTf(y0),MuCe(x0))
w4 = min( MuTe(y0),MuCf(x0))
w5 = min( MuTe(y0),MuCm(x0))
w6 = min( MuTe(y0),MuCe(x0))

def MuT(t):
    return w1*MuS(t) + w2*MuS(t) + w3*MuS(t) + w4*MuL(t) + w5*MuM(t) + w6*MuS(t)

def Tmp(t):
    return t*MuT(t)

tu,_  = quad( Tmp,0,30 )
mau,_ = quad( MuT,0,30 )
t0 = tu/mau

print("Bồn có %.1f m3 và bể có %.1f m3, thời gian bơm: %.2f phút" % (y0,x0,t0))
