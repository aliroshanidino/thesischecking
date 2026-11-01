# Bit-accurate Python model of rtl/mark2_homeostatic.vhd (Q7.19, 26-bit), for audit only.
# Usage: python3 tools/rtl_model.py   (reproduces audit items A1 and B8 in 09-consistency-audit.md)
W=26; ONE=1<<19
def wrap(x):
    x&=(1<<W)-1
    return x-(1<<W) if x>>(W-1) else x
C,D,UR,TR,FB=0,49152,-106496,576717,-52429
G,VMAX,VMIN,UMAX,UMIN,TMAX,C25=65536,2097152,-262144,2097152,-2097152,4194304,131072
def sim(I,n=10000,sign_fix=False,fault=None):
    v,u,th=0,UR,TR; spikes=[]; us=[]
    for t in range(n):
        if v<0: pwl=0
        elif v<131072: pwl=v>>1
        elif v<327680: pwl=(v<<1)-196608
        elif v<589824: pwl=(v<<2)-851968
        else: pwl=(v<<3)-3211264
        pwl=wrap(pwl)
        dv=wrap((pwl+I)-((v>>3)+(v>>6)+u+C25)); vn=wrap(v+(dv>>6))
        vc=min(max(vn,VMIN),VMAX)
        bv=(v>>2)-(v>>4)+(v>>6)
        diff=wrap(bv-UR-u) if not sign_fix else wrap(bv+UR-u)
        du=(diff>>6)+(diff>>8); un=wrap(u+(du>>6))
        err=th-TR; thr=th-(err>>6); brake=(err<<3) if err>0 else 0
        fb_en = vn<FB and th>TR and u>UR
        upre=((un+UR)>>1) if fb_en else un
        uc=min(max(upre,UMIN),UMAX)
        uj=min(uc+D+brake,UMAX)
        if vc>=thr:
            v,u,th=C,uj,min(thr+G,TMAX); spikes.append(t)
        else:
            v,u,th=vc,uc,thr
        us.append(u)
    return spikes,v,u,th
for I in (0,):
    s,v,u,th=sim(I,20000); print(f"I=0 RTL as-is: spikes={len(s)} final V={v/ONE:.4f} U={u/ONE:.4f}")
    s,v,u,th=sim(I,20000,sign_fix=True); print(f"I=0 sign-fixed: spikes={len(s)} final V={v/ONE:.4f} U={u/ONE:.4f}")
for I in (650000,820000,850000,int(0.3125*ONE)):
    s,_,_,_=sim(I); isi=[b-a for a,b in zip(s,s[1:])]
    print(f"I_syn={I} ({I/ONE:.3f}): n={len(s)} first={s[:6]} ISI_tail={isi[-3:]}")
s,_,_,_=sim(int(0.3125*ONE),sign_fix=True); print("TN I_hw=0.3125 sign-fixed: n=",len(s), "ISI tail", [b-a for a,b in zip(s,s[1:])][-3:])
