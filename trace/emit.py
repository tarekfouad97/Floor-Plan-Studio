import sys,pickle,json
SP=sys.argv[1]
wall,X0,Y0,X1,Y1=pickle.load(open(SP+'/mask.pkl','rb'))
# Scale calibrated per axis against the sketch's own dimension labels
# (median over every labelled room). The sketch is drawn slightly
# anisotropically; this keeps the traced shape while matching the labels.
PX=0.694; PY=0.780; OX=101.0; OY=112.0
cx=lambda p: round((p-OX)/PX,1)
cy=lambda p: round((p-OY)/PY,1)

# --- wall raster -> rectangles (row runs merged vertically) ----------
runs=[]
for y in range(Y0,Y1):
    x=X0
    while x<X1:
        if wall[y][x]:
            s=x
            while x<X1 and wall[y][x]: x+=1
            runs.append((y,s,x))
        else: x+=1
by={} 
for y,a,b in runs: by.setdefault(y,[]).append((a,b))
rects=[]; openr={}
for y in sorted(by):
    cur=set(by[y])
    for k in list(openr):
        if k not in cur:
            a,b=k; y0=openr.pop(k); rects.append((a,y0,b-a,y-y0))
    for k in cur:
        if k not in openr: openr[k]=y
for k,y0 in openr.items():
    a,b=k; rects.append((a,y0,b-a,Y1-y0))
rects=[r for r in rects if r[2]>0 and r[3]>0]

# ---- straighten: cluster near-identical edge coordinates and snap ----
def cluster(vals,tol=4):
    vs=sorted(set(vals)); groups=[]; cur=[vs[0]]
    for v in vs[1:]:
        if v-cur[-1]<=tol: cur.append(v)
        else: groups.append(cur); cur=[v]
    groups.append(cur)
    m={}
    for gp in groups:
        rep=gp[len(gp)//2]
        for v in gp: m[v]=rep
    return m
xm=cluster([r[0] for r in rects]+[r[0]+r[2] for r in rects])
ym=cluster([r[1] for r in rects]+[r[1]+r[3] for r in rects])
snapped=set()
for a,b,w,h in rects:
    x0,x1,y0,y1 = xm[a],xm[a+w],ym[b],ym[b+h]
    # never let snapping collapse a rectangle - fall back to its own edges
    if x1-x0 < 2: x0,x1 = a, a+w
    if y1-y0 < 2: y0,y1 = b, b+h
    snapped.add((x0,y0,x1-x0,y1-y0))
rects=sorted(snapped)
print("wall rectangles: %d (straightened, %d edge clusters x / %d y)"%(
      len(rects),len(set(xm.values())),len(set(ym.values()))))

WALLS=[[cx(a),cy(b),round(w/PX,1),round(h/PY,1)] for a,b,w,h in rects]

# --- rooms: rectangles read off the extracted wall bands -------------
# every coordinate below is a wall-band edge measured off the photo.
# the master bedroom is L-shaped: the balcony is carved out of its corner.
R=[("rec","Reception",  [(121,125,372,403)],           "3.60 x 3.73"),
   ("bed1","Bedroom 1", [(383,125,632,403)],           "3.60 x 3.48"),
   ("bed2","Bedroom 2", [(671,125,905,403)],           "3.50 x 3.48"),
   ("mbed","Master Bed",[(940,125,1180,277),(940,277,1248,534)], "3.60 x 5.10"),
   ("balc","Balcony",   [(1191,125,1255,277)],         "1.10 x 2.00"),
   ("hall","Corridor",  [(306,429,905,491)],           "1.00 wide"),
   ("bath","Bathroom",  [(193,429,295,596)],           "1.42 x 2.20"),
   ("stor","Store",     [(306,502,451,596)],           "2.06 x 1.32"),
   ("wc","Toilet",      [(461,502,563,696)],           "1.60 x 2.32"),
   ("kit","Kitchen",    [(587,502,821,696)],           "3.35 x 2.32"),
   ("lob","Entrance",   [(842,545,905,696)],           "-")]
ROOMS=[]
for rid,nm,rr,lbl in R:
    parts=[[cx(a),cy(b),round((c-a)/PX,1),round((d-b)/PY,1)] for a,b,c,d in rr]
    area=sum(p[2]*p[3] for p in parts)/10000.0
    ROOMS.append(dict(id=rid,name=nm,rects=parts,outdoor=(rid=="balc"),label=lbl))
    dims=" + ".join("%.2fx%.2f"%(p[2]/100,p[3]/100) for p in parts)
    print("  %-11s %-24s %5.1f m2   sketch says %s"%(nm,dims,area,lbl))
ext=dict(x=cx(X0),y=cy(Y0),w=round((X1-X0)/PX,1),h=round((Y1-Y0)/PY,1))
json.dump(dict(walls=WALLS,rooms=ROOMS,extent=ext),open(SP+'/plan.json','w'))
print("\ntotal extent: %.2f x %.2f m"%(ext['w']/100,ext['h']/100))
print("wrote plan.json (%d wall rects)"%len(WALLS))
