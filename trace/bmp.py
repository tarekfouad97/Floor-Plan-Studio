import struct

def load_bmp_gray(path):
    with open(path,'rb') as f: data=f.read()
    assert data[:2]==b'BM'
    off = struct.unpack_from('<I', data, 10)[0]
    hdr = struct.unpack_from('<I', data, 14)[0]
    w,h = struct.unpack_from('<ii', data, 18)
    bpp = struct.unpack_from('<H', data, 28)[0]
    comp = struct.unpack_from('<I', data, 30)[0]
    flip = h>0
    h=abs(h)
    nb = bpp//8
    rowsize = ((bpp*w+31)//32)*4
    g=[]
    for r in range(h):
        sr = (h-1-r) if flip else r
        base = off + sr*rowsize
        row=bytearray(w)
        for c in range(w):
            p = base + c*nb
            b,gg,rr = data[p],data[p+1],data[p+2]
            row[c] = (rr*299+gg*587+b*114)//1000
        g.append(row)
    return w,h,g

if __name__=='__main__':
    import sys
    w,h,g = load_bmp_gray(sys.argv[1])
    print('size',w,h)
