# -*- coding: utf-8 -*-
"""测试方独立黄金用例生成器 —— 与数据工程师的 generate.py 完全独立实现,
   用于交叉验证. 任何与数据库的分歧都将作为缺陷上报."""
import json, datetime as dt

GAN='甲乙丙丁戊己庚辛壬癸'; ZHI='子丑寅卯辰巳午未申酉戌亥'
ZWX={'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
TWX={'乾':'金','兑':'金','离':'火','震':'木','巽':'木','坎':'水','艮':'土','坤':'土'}
SHENG={'木':'火','火':'土','土':'金','金':'水','水':'木'}  # A生B
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
T2B={'乾':'111','兑':'110','离':'101','震':'100','巽':'011','坎':'010','艮':'001','坤':'000'}
B2T={v:k for k,v in T2B.items()}
NJ_GAN={'乾':('甲','壬'),'坤':('乙','癸'),'震':('庚','庚'),'巽':('辛','辛'),'坎':('戊','戊'),'离':('己','己'),'艮':('丙','丙'),'兑':('丁','丁')}
NJ_ZHI={'乾':('子寅辰','午申戌'),'坎':('寅辰午','申戌子'),'艮':('辰午申','戌子寅'),'震':('子寅辰','午申戌'),
        '巽':('丑亥酉','未巳卯'),'离':('卯丑亥','酉未巳'),'坤':('未巳卯','丑亥酉'),'兑':('巳卯丑','亥酉未')}
NAMES={ # (下,上)->卦名, 通行本
('乾','乾'):'乾',('坤','坤'):'坤',('震','坎'):'屯',('坎','艮'):'蒙',('乾','坎'):'需',('坎','乾'):'讼',
('坎','坤'):'师',('坤','坎'):'比',('乾','巽'):'小畜',('兑','乾'):'履',('乾','坤'):'泰',('坤','乾'):'否',
('离','乾'):'同人',('乾','离'):'大有',('艮','坤'):'谦',('坤','震'):'豫',('震','兑'):'随',('巽','艮'):'蛊',
('兑','坤'):'临',('坤','巽'):'观',('震','离'):'噬嗑',('离','艮'):'贲',('坤','艮'):'剥',('震','坤'):'复',
('震','乾'):'无妄',('乾','艮'):'大畜',('震','艮'):'颐',('巽','兑'):'大过',('坎','坎'):'坎',('离','离'):'离',
('艮','兑'):'咸',('巽','震'):'恒',('艮','乾'):'遁',('乾','震'):'大壮',('坤','离'):'晋',('离','坤'):'明夷',
('离','巽'):'家人',('兑','离'):'睽',('艮','坎'):'蹇',('坎','震'):'解',('兑','艮'):'损',('震','巽'):'益',
('乾','兑'):'夬',('巽','乾'):'姤',('坤','兑'):'萃',('巽','坤'):'升',('坎','兑'):'困',('巽','坎'):'井',
('离','兑'):'革',('巽','离'):'鼎',('震','震'):'震',('艮','艮'):'艮',('艮','巽'):'渐',('兑','震'):'归妹',
('离','震'):'丰',('艮','离'):'旅',('巽','巽'):'巽',('兑','兑'):'兑',('坎','巽'):'涣',('兑','坎'):'节',
('兑','巽'):'中孚',('艮','震'):'小过',('离','坎'):'既济',('坎','离'):'未济'}

def flip(b,p): l=list(b); l[p-1]='10'[int(l[p-1])]; return ''.join(l)
def palace(b):
    """独立推演: 从64卦反查其所属宫与宫序"""
    for p in T2B:
        cur=T2B[p]*2; seq=[cur]
        for ln in (1,2,3,4,5): cur=flip(cur,ln); seq.append(cur)
        seq.append(flip(seq[5],4)); seq.append(T2B[p]+seq[6][3:])
        if b in seq: return p, seq.index(b)
    raise ValueError(b)
SHI=[6,1,2,3,4,5,4,3]

def hexname(b): return NAMES[(B2T[b[:3]],B2T[b[3:]])]
def najia(b):
    lo,up=B2T[b[:3]],B2T[b[3:]]; out=[]
    for i in range(3): z=NJ_ZHI[lo][0][i]; out.append((NJ_GAN[lo][0],z,ZWX[z]))
    for i in range(3): z=NJ_ZHI[up][1][i]; out.append((NJ_GAN[up][1],z,ZWX[z]))
    return out
def liuqin(pal_wx,z_wx):
    if pal_wx==z_wx: return '兄弟'
    if SHENG[z_wx]==pal_wx: return '父母'
    if SHENG[pal_wx]==z_wx: return '子孙'
    if KE[z_wx]==pal_wx: return '官鬼'
    if KE[pal_wx]==z_wx: return '妻财'
LIUSHEN_START={'甲':0,'乙':0,'丙':1,'丁':1,'戊':2,'己':3,'庚':4,'辛':4,'壬':5,'癸':5}
LIUSHEN=['青龙','朱雀','勾陈','腾蛇','白虎','玄武']
CHONG={'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}

# 日柱: 锚点 1949-10-01 = 甲子日 (史载锚点), 23点换日
ANCHOR=dt.date(1949,10,1)
def day_gz(local_dt):
    d=local_dt.date()
    if local_dt.hour>=23: d=d+dt.timedelta(days=1)
    n=(d-ANCHOR).days%60
    return GAN[n%10]+ZHI[n%12]
def hour_zhi(h): return ZHI[((h+1)//2)%12]
WUSHU={'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊','丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
def hour_gz(dgz,h):
    z=hour_zhi(h); zi_gan=WUSHU[dgz[0]]
    return GAN[(GAN.index(zi_gan)+ZHI.index(z))%10]+z
def xunkong(dgz):
    n=(GAN.index(dgz[0]) - 0)  # 旬首: 日柱序号取整十
    idx=( (GAN.index(dgz[0])*6 - ZHI.index(dgz[1])*5) % 60 )  # 六十甲子序
    xun_start=idx//10*10
    used={ZHI[(xun_start+i)%12] for i in range(10)}
    return sorted([z for z in ZHI if z not in used], key=ZHI.index)
WUHU={'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
def month_gz(year_gan,m_branch):
    start=WUHU[year_gan]; off=(ZHI.index(m_branch)-ZHI.index('寅'))%12
    return GAN[(GAN.index(start)+off)%10]+m_branch

# 安全日期表(远离节气边界, 月支无歧义; 年柱均在立春后): 测试方人工核定
SAFE_DATES=[("2025-03-20T10:30","乙巳","卯"),("2025-04-20T15:00","乙巳","辰"),("2025-05-20T09:00","乙巳","巳"),
 ("2025-06-15T10:00","乙巳","午"),("2025-07-20T14:00","乙巳","未"),("2025-08-20T11:00","乙巳","申"),
 ("2025-09-20T16:00","乙巳","酉"),("2025-10-20T08:00","乙巳","戌"),("2025-11-20T13:00","乙巳","亥"),
 ("2025-12-20T10:00","乙巳","子"),("2026-03-15T10:00","丙午","卯"),("2026-06-11T10:30","丙午","午")]

def paipan(yaos,iso,ygz,mbr):
    t=dt.datetime.fromisoformat(iso)
    ben=''.join('1' if y in (7,9) else '0' for y in yaos)
    moving=[i+1 for i,y in enumerate(yaos) if y in (6,9)]
    bian=ben
    for m in moving: bian=flip(bian,m)
    dgz=day_gz(t); kong=xunkong(dgz); mgz=month_gz(ygz[0],mbr)
    p,idx=palace(ben); pwx=TWX[p]
    nj=najia(ben); start=LIUSHEN_START[dgz[0]]
    lines=[]
    for i in range(6):
        g,z,w=nj[i]
        lines.append({"pos":i+1,"yinYang":"yang" if ben[i]=='1' else "yin",
          "isMoving":(i+1) in moving,"naJia":{"gan":g,"zhi":z,"wuXing":w},
          "liuQin":liuqin(pwx,w),"liuShen":LIUSHEN[(start+i)%6],
          "shiYing":"shi" if SHI[idx]==i+1 else ("ying" if ((SHI[idx]+2)%6)+1==i+1 else None),
          "isXunKong":z in kong,"isYueBreak":CHONG[mbr]==z,
          "changedYinYang":(("yin" if ben[i]=='1' else "yang") if (i+1) in moving else None)})
    res={"benGua":{"name":hexname(ben),"palace":p,"palaceIndex":idx,"shi":SHI[idx],"ying":((SHI[idx]+2)%6)+1,"binary":ben},
         "bianGua":None if not moving else {"name":hexname(bian),"palace":palace(bian)[0],"palaceIndex":palace(bian)[1],"binary":bian},
         "siZhu":{"year":ygz,"month":mgz,"day":dgz,"hour":hour_gz(dgz,t.hour)},
         "xunKong":kong,"yueJian":mbr,"lines":lines}
    return res

# ---- 用例编排: 64卦各一例(动爻模式 id mod 7) + 8个专项边界例 = 72 ----
cases=[]; n=0
for b in sorted(NAMES.keys(), key=lambda k:(k[0],k[1])):
    ben=T2B[b[0]]+T2B[b[1]]
    n+=1; mv=n%7  # 0=无动爻, 1..6=该爻动
    yaos=[]
    for i in range(6):
        yang=ben[i]=='1'
        if mv==i+1: yaos.append(9 if yang else 6)
        else: yaos.append(7 if yang else 8)
    d=SAFE_DATES[n%len(SAFE_DATES)]
    cases.append({"id":f"G{n:03d}","desc":f"{hexname(ben)}卦 动爻:{mv if mv else '无'}","input":{"yaos":yaos,"datetime":d[0]+"+08:00"},"_date_meta":d,"expected":paipan(yaos,d[0],d[1],d[2])})
# 专项边界
SP=[("S065 乾六爻全动变坤",[9]*6,SAFE_DATES[3]),("S066 坤六爻全动变乾",[6]*6,SAFE_DATES[4]),
    ("S067 既济三爻动",[9,8,9,8,9,8][:6],SAFE_DATES[5]),
    ("S068 23点前(22:59)日柱",[7,8,7,8,7,8],("2025-06-15T22:59","乙巳","午")),
    ("S069 23点后(23:01)换日",[7,8,7,8,7,8],("2025-06-15T23:01","乙巳","午")),
    ("S070 游魂卦晋无动爻",None,SAFE_DATES[0]),("S071 归魂卦大有上爻动",None,SAFE_DATES[1]),
    ("S072 当代日期回归例",[8,7,7,7,8,8],("2026-06-11T10:30","丙午","午"))]
def yaos_for(b,mv): 
    return [ (9 if b[i]=='1' else 6) if mv==i+1 else (7 if b[i]=='1' else 8) for i in range(6)]
jin=T2B['坤']+T2B['离']; dayou=T2B['乾']+T2B['离']
SP[5]=("S070 游魂卦晋无动爻",yaos_for(jin,0),SAFE_DATES[0])
SP[6]=("S071 归魂卦大有上爻动",yaos_for(dayou,6),SAFE_DATES[1])
for desc,y,d in SP:
    n+=1
    cases.append({"id":desc.split()[0],"desc":desc,"input":{"yaos":y,"datetime":d[0]+"+08:00"},"_date_meta":d,"expected":paipan(y,d[0],d[1],d[2])})

# 断言: S068/S069 日柱必须不同且相差一天干支
a=[c for c in cases if c['id']=='S068'][0]['expected']['siZhu']['day']
b_=[c for c in cases if c['id']=='S069'][0]['expected']['siZhu']['day']
i1=(GAN.index(a[0]), ZHI.index(a[1])); 
seq=[GAN[i%10]+ZHI[i%12] for i in range(60)]
assert (seq.index(b_)-seq.index(a))%60==1, "23点换日边界失败"
# 晋/大有 宫位断言
jj=[c for c in cases if c['id']=='S070'][0]['expected']['benGua']
assert jj['palace']=='乾' and jj['palaceIndex']==6 and jj['shi']==4
dy=[c for c in cases if c['id']=='S071'][0]['expected']['benGua']
assert dy['palace']=='乾' and dy['palaceIndex']==7 and dy['shi']==3
for c in cases: c.pop('_date_meta')
json.dump({"version":"1.0","generator":"测试方独立实现","count":len(cases),"cases":cases},
          open('golden/paipan_golden.json','w'),ensure_ascii=False,indent=1)
print(f"黄金用例 {len(cases)} 条生成完成; 边界断言通过")
print("示例 S069:", json.dumps(cases[-4]['expected']['siZhu'],ensure_ascii=False))
