import sys
from collections import deque
sys.path.insert(0,sys.argv[1])
from bmp import load_bmp_gray
SP=sys.argv[1]; W,H,g=load_bmp_gray(SP+'/plan.bmp')
X0,Y0,X1,Y1=92,96,1292,732
T=170; R=int(sys.argv[2]); MINRUN=int(sys.argv[3])

m=[bytearray(W) for _ in range(H)]
for y in range(Y0,Y1):
    row=m[y]; gy=g[y]
    for x in range(X0,X1):
        if gy[x]<T: row[x]=1

def dil_h(src,r):
    out=[bytearray(W) for _ in range(H)]
    for y in range(H):
        s=src[y]; o=out[y]; run=0
        for x in range(W):                     # forward
            run = r+1 if s[x] else (run-1 if run>0 else 0)
            if run: o[x]=1
        run=0
        for x in range(W-1,-1,-1):             # backward
            run = r+1 if s[x] else (run-1 if run>0 else 0)
            if run: o[x]=1
    return out
def dil_v(src,r):
    out=[bytearray(W) for _ in range(H)]
    for x in range(W):
        run=0
        for y in range(H):
            run = r+1 if src[y][x] else (run-1 if run>0 else 0)
            if run: out[y][x]=1
        run=0
        for y in range(H-1,-1,-1):
            run = r+1 if src[y][x] else (run-1 if run>0 else 0)
            if run: out[y][x]=1
    return out
def inv(s):
    return [bytearray(1-v for v in row) for row in s]
def dilate(s,r): return dil_v(dil_h(s,r),r)
def erode(s,r):  return inv(dilate(inv(s),r))

closed = erode(dilate(m,R),R)          # fill the gap between paired wall lines

# A wall is thick in BOTH directions. A dimension line is long but 1px tall,
# so requiring both runs >= MINRUN keeps walls and drops dimension lines.
vok=[bytearray(W) for _ in range(H)]
hok=[bytearray(W) for _ in range(H)]
for x in range(W):
    y=0
    while y<H:
        if closed[y][x]:
            s=y
            while y<H and closed[y][x]: y+=1
            if y-s>=MINRUN:
                for yy in range(s,y): vok[yy][x]=1
        else: y+=1
for y in range(H):
    row=closed[y]; x=0
    while x<W:
        if row[x]:
            s=x
            while x<W and row[x]: x+=1
            if x-s>=MINRUN:
                for xx in range(s,x): hok[y][xx]=1
        else: x+=1
thick=[bytearray(W) for _ in range(H)]
for y in range(H):
    for x in range(W):
        if vok[y][x] and hok[y][x]: thick[y][x]=1

# drop small blobs (text glyphs)
comp=[[0]*W for _ in range(H)]; cid=0; keep=set(); comps=[]
for sy in range(H):
    for sx in range(W):
        if thick[sy][sx] and not comp[sy][sx]:
            cid+=1; q=deque([(sx,sy)]); comp[sy][sx]=cid; px=[(sx,sy)]
            while q:
                x,y=q.popleft()
                for dy in(-1,0,1):
                    for dx in(-1,0,1):
                        nx,ny=x+dx,y+dy
                        if 0<=nx<W and 0<=ny<H and thick[ny][nx] and not comp[ny][nx]:
                            comp[ny][nx]=cid; q.append((nx,ny)); px.append((nx,ny))
            comps.append((len(px),cid,min(p[0] for p in px),min(p[1] for p in px),
                          max(p[0] for p in px),max(p[1] for p in px)))
comps.sort(reverse=True)
print("top components (px, bbox):")
for n_,c,a,b,d,e in comps[:14]:
    print("   px=%-7d bbox=(%d,%d)-(%d,%d) %dx%d"%(n_,a,b,d,e,d-a,e-b))
BIG=int(sys.argv[4]) if len(sys.argv)>4 else 1500
for n_,c,a,b,d,e in comps:
    if n_>=BIG: keep.add(c)
out=[bytearray(W) for _ in range(H)]
n=0
for y in range(H):
    for x in range(W):
        if thick[y][x] and comp[y][x] in keep: out[y][x]=1; n+=1
print("R=%d MINRUN=%d -> wall px=%d, blobs kept=%d"%(R,MINRUN,n,len(keep)))
# save visualisation
px=bytearray()
for y in range(Y0,Y1):
    for x in range(X0,X1):
        v = 0 if out[y][x] else (200 if m[y][x] else 255)
        px+=bytes([v,v,v])
open(SP+'/wallmask.ppm','wb').write(b'P6\n%d %d\n255\n'%(X1-X0,Y1-Y0)+px)
import pickle; pickle.dump((out,X0,Y0,X1,Y1),open(SP+'/mask.pkl','wb'))
