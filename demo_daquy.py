import numpy as np
import skfuzzy as fz
import matplotlib.pyplot as plt

X = np.arange(0.01, 15.001, 0.1)
Ds = fz.trimf(X, [0, 0, 3])
Dm= fz.trimf(X, [0, 3, 6])
Dl = fz.trimf(X, [3, 6, 6])

### Định nghĩa tập mờ
Y = np.arange(2.5, 12.1, 0.1)
Gs = fz.trimf( Y,[0,0,50] )
Gm = fz.trimf( Y,[0,50,100] )
Gl = fz.trimf( Y,[50,100,100] )

### Vẽ đồ thị 3 hàm thuộc tương ứng
plt.title( "CÁC TẬP MỜ VỀ LƯỢNG DẦU MỠ" )
plt.plot( Y, Gs, label = "Dầu mở ít" )
plt.plot( Y, Gm, label = "Dầu mở vừa phải" )
plt.plot( Y, Gl, label = "Dầu mở nhiều" )
plt.xlabel( "Khộng gian nền $Y \in [1,100]$" )
plt.legend( loc="best" )
plt.show()

Z = np.array( [0,4,18,32,46,60] )
Tf = fz.trapmf( Z,[0,0,4,18] )
Ts = fz.trimf( Z,[4,18,32] )
Tm = fz.trimf( Z,[18,32,46] )
Tl = fz.trimf( Z,[32,46,60] )
Tv = fz.trimf( Z,[46,60,60] )

plt.title( "CÁC TẬP MỜ VỀ THỜI GIAN GIẶT" )
plt.plot( Z, Tf, label = "Rất nhanh" )
plt.plot( Z, Ts, label = "Nhanh" )
plt.plot( Z, Tm, label = "trung bình" )
plt.plot( Z, Tl, label = "Lâu" )
plt.plot( Z, Tv, label = "Rất lâu" )
plt.xlabel( "Khộng gian nền $Z \in [0,60]$" )
plt.legend( loc="best" )
plt.show()

x0, y0 = 10, 40

xs = fz.interp_membership( X,Ds,x0 )
xm = fz.interp_membership( X,Dm,x0 )
xl = fz.interp_membership( X,Dl,x0 )

ys = fz.interp_membership(Y,Gs,y0)
ym = fz.interp_membership(Y,Gm,y0)
yl = fz.interp_membership(Y,Gl,y0)

w1 = min( xl,yl )
w2 = min( xm,yl )
w3 = min( xs,yl )
w4 = min( xl,ym )
w5 = min( xm,ym )
w6 = min( xs,ym )
w7 = min( xl,ys )
w8 = min( xm,ys )
w9 = min( xs,ys )

T = w1*Tv + (w2+w3+w4)*Tl + (w5+w6+w7)*Tm + w8*Ts + w9*Tf

### Tử số là tích của Z với chuyển vị của T
t0 = Z.dot(T.T)/T.sum()

print( "Với độ bẩn %.f, lượng dầu mở %.f, thì thời gian giặt là %.f phút" % (x0,y0,t0) )
