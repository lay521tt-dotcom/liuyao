# -*- coding: utf-8 -*-
"""六爻静态数据生成器：用纳甲筮法定式规则生成数据并自校验，校验通过才输出SQL"""

# ---------- 基础定义 ----------
TRIGRAMS = {  # binary自下而上,阳1阴0
    '111':'乾','110':'兑','101':'离','100':'震','011':'巽','010':'坎','001':'艮','000':'坤'}
TRI_WUXING = {'乾':'金','兑':'金','离':'火','震':'木','巽':'木','坎':'水','艮':'土','坤':'土'}
ZHI_WUXING = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
# 纳甲定式: 天干(内,外), 地支(内三爻, 外三爻)
NAJIA = {
 '乾':(('甲','壬'),(['子','寅','辰'],['午','申','戌'])),
 '坎':(('戊','戊'),(['寅','辰','午'],['申','戌','子'])),
 '艮':(('丙','丙'),(['辰','午','申'],['戌','子','寅'])),
 '震':(('庚','庚'),(['子','寅','辰'],['午','申','戌'])),
 '巽':(('辛','辛'),(['丑','亥','酉'],['未','巳','卯'])),
 '离':(('己','己'),(['卯','丑','亥'],['酉','未','巳'])),
 '坤':(('乙','癸'),(['未','巳','卯'],['丑','亥','酉'])),
 '兑':(('丁','丁'),(['巳','卯','丑'],['亥','酉','未'])),
}
# 通行本卦序: id -> (卦名, 下卦, 上卦)
KINGWEN = {
1:('乾','乾','乾'),2:('坤','坤','坤'),3:('屯','震','坎'),4:('蒙','坎','艮'),5:('需','乾','坎'),
6:('讼','坎','乾'),7:('师','坎','坤'),8:('比','坤','坎'),9:('小畜','乾','巽'),10:('履','兑','乾'),
11:('泰','乾','坤'),12:('否','坤','乾'),13:('同人','离','乾'),14:('大有','乾','离'),15:('谦','艮','坤'),
16:('豫','坤','震'),17:('随','震','兑'),18:('蛊','巽','艮'),19:('临','兑','坤'),20:('观','坤','巽'),
21:('噬嗑','震','离'),22:('贲','离','艮'),23:('剥','坤','艮'),24:('复','震','坤'),25:('无妄','震','乾'),
26:('大畜','乾','艮'),27:('颐','震','艮'),28:('大过','巽','兑'),29:('坎','坎','坎'),30:('离','离','离'),
31:('咸','艮','兑'),32:('恒','巽','震'),33:('遁','艮','乾'),34:('大壮','乾','震'),35:('晋','坤','离'),
36:('明夷','离','坤'),37:('家人','离','巽'),38:('睽','兑','离'),39:('蹇','艮','坎'),40:('解','坎','震'),
41:('损','兑','艮'),42:('益','震','巽'),43:('夬','乾','兑'),44:('姤','巽','乾'),45:('萃','坤','兑'),
46:('升','巽','坤'),47:('困','坎','兑'),48:('井','巽','坎'),49:('革','离','兑'),50:('鼎','巽','离'),
51:('震','震','震'),52:('艮','艮','艮'),53:('渐','艮','巽'),54:('归妹','兑','震'),55:('丰','离','震'),
56:('旅','艮','离'),57:('巽','巽','巽'),58:('兑','兑','兑'),59:('涣','坎','巽'),60:('节','兑','坎'),
61:('中孚','兑','巽'),62:('小过','艮','震'),63:('既济','离','坎'),64:('未济','坎','离')}
TRI_BIN = {v:k for k,v in TRIGRAMS.items()}
bin2name = {TRI_BIN[lo]+TRI_BIN[up]:(i,n) for i,(n,lo,up) in KINGWEN.items()}
assert len(bin2name)==64

def flip(b,pos): l=list(b); l[pos-1]='1' if l[pos-1]=='0' else '0'; return ''.join(l)

# ---------- 八宫推演 ----------
PALACE_NAMES=['乾','坎','艮','震','巽','离','坤','兑']
SHI_POS=[6,1,2,3,4,5,4,3]
palace_of={}  # binary -> (宫,宫序idx)
for p in PALACE_NAMES:
    cur=TRI_BIN[p]*2; seq=[cur]
    for line in [1,2,3,4,5]: cur=flip(cur,line); seq.append(cur)
    seq.append(flip(seq[5],4))            # 游魂
    youhun=seq[6]
    gui=youhun[3:] ; gui=TRI_BIN[p]+youhun[3:]  # 归魂:内卦还原为本宫
    seq.append(gui)
    for idx,b in enumerate(seq):
        assert b not in palace_of, f"重复 {b}"
        palace_of[b]=(p,idx)
assert len(palace_of)==64

# ---------- 自校验断言(权威定式) ----------
EXPECT={'乾':['乾','姤','遁','否','观','剥','晋','大有'],
        '坎':['坎','节','屯','既济','革','丰','明夷','师'],
        '艮':['艮','贲','大畜','损','睽','履','中孚','渐'],
        '震':['震','豫','解','恒','升','井','大过','随'],
        '巽':['巽','小畜','家人','益','无妄','噬嗑','颐','蛊'],
        '离':['离','旅','鼎','未济','蒙','涣','讼','同人'],
        '坤':['坤','复','临','泰','大壮','夬','需','比'],
        '兑':['兑','困','萃','咸','蹇','谦','小过','归妹']}
report=[]
for p in PALACE_NAMES:
    got=[None]*8
    for b,(pp,idx) in palace_of.items():
        if pp==p: got[idx]=bin2name[b][1]
    assert got==EXPECT[p], f"{p}宫不符: {got}"
    report.append(f"[PASS] {p}宫八卦: {' '.join(got)}")

# ---------- 纳甲生成 ----------
def najia_lines(binary):
    lo,up=TRIGRAMS[binary[:3]],TRIGRAMS[binary[3:]]
    res=[]
    g_in=NAJIA[lo][0][0]; z_in=NAJIA[lo][1][0]
    g_out=NAJIA[up][0][1]; z_out=NAJIA[up][1][1]
    for i in range(3): res.append((i+1,g_in,z_in[i],ZHI_WUXING[z_in[i]]))
    for i in range(3): res.append((i+4,g_out,z_out[i],ZHI_WUXING[z_out[i]]))
    return res
# 纳甲断言: 乾初爻甲子水 上爻壬戌土; 坤初爻乙未土 上爻癸酉金; 姤(巽下乾上)初爻辛丑土
qian=najia_lines('111111'); kun=najia_lines('000000'); gou=najia_lines('011111')
assert qian[0][1:]==('甲','子','水') and qian[5][1:]==('壬','戌','土')
assert kun[0][1:]==('乙','未','土') and kun[5][1:]==('癸','酉','金')
assert gou[0][1:]==('辛','丑','土')
report.append("[PASS] 纳甲抽核: 乾·坤·姤 关键爻全部正确")

# ---------- 旬空表(60甲子) ----------
GAN='甲乙丙丁戊己庚辛壬癸'; ZHI='子丑寅卯辰巳午未申酉戌亥'
jiazi=[GAN[i%10]+ZHI[i%12] for i in range(60)]
xunkong={}
for x in range(6):
    used=[ZHI[(i)%12] for i in range(x*10, x*10+10)]
    kong=[z for z in ZHI if z not in [jiazi[x*10+i][1] for i in range(10)]]
    for i in range(10): xunkong[jiazi[x*10+i]]=kong
assert xunkong['甲子']==['戌','亥'] and xunkong['甲戌']==['申','酉'] and xunkong['癸亥']==['子','丑']
report.append("[PASS] 旬空: 甲子旬空戌亥 / 甲戌旬空申酉 等断言通过")

# ---------- 输出SQL ----------
sym=lambda kid: chr(0x4DC0+kid-1)
out=[]
out.append("-- seed_core.sql 由 generate.py 规则生成,经断言自校验. 禁止手改,改规则请改脚本\nBEGIN;")
out.append("INSERT INTO trigram(id,name,symbol,wu_xing,binary_code) VALUES")
tri_id={n:i+1 for i,n in enumerate(['乾','兑','离','震','巽','坎','艮','坤'])}
tris=[f"({tri_id[n]},'{n}','{chr(0x2630+i)}','{TRI_WUXING[n]}','{TRI_BIN[n]}')" for i,n in enumerate(['乾','兑','离','震','巽','坎','艮','坤'])]
out.append(',\n'.join(tris)+';')
hx=[]; nj=[]; pal_idx_cn=['本宫','一世','二世','三世','四世','五世','游魂','归魂']
for kid in sorted(KINGWEN):
    name,lo,up=KINGWEN[kid]; b=TRI_BIN[lo]+TRI_BIN[up]
    p,idx=palace_of[b]; shi=SHI_POS[idx]; ying=((shi+3-1)%6)+1
    hx.append(f"({kid},'{name}','{sym(kid)}',{tri_id[up]},{tri_id[lo]},'{b}',{tri_id[p]},{idx},{shi},{ying},NULL,NULL)")
    for pos,g,z,w in najia_lines(b):
        nj.append(f"({kid},{pos},'{g}','{z}','{w}')")
out.append("INSERT INTO hexagram(id,name,symbol_unicode,upper_trigram_id,lower_trigram_id,binary_code,palace_trigram_id,palace_index,shi_position,ying_position,gua_ci,gua_annotation) VALUES\n"+',\n'.join(hx)+';')
out.append("INSERT INTO najia(hexagram_id,line_position,tian_gan,di_zhi,wu_xing) VALUES\n"+',\n'.join(nj)+';')
ls=[('甲','青龙'),('乙','青龙'),('丙','朱雀'),('丁','朱雀'),('戊','勾陈'),('己','腾蛇'),('庚','白虎'),('辛','白虎'),('壬','玄武'),('癸','玄武')]
out.append("INSERT INTO liushen_rule(day_gan,first_liushen) VALUES\n"+',\n'.join([f"('{g}','{s}')" for g,s in ls])+';')
out.append("INSERT INTO xun_kong(day_ganzhi,kong1,kong2) VALUES\n"+',\n'.join([f"('{d}','{k[0]}','{k[1]}')" for d,k in xunkong.items()])+';')
out.append("COMMIT;")
open('seed_core.sql','w').write('\n'.join(out))
open('verification_report.txt','w').write('\n'.join(report)+f"\n\n统计: 八卦8 / 六十四卦64 / 纳甲{len(nj)}行 / 六神规则10 / 旬空60\n结论: 全部断言通过, seed_core.sql 可入库")
print('\n'.join(report)); print("纳甲行数:",len(nj))
