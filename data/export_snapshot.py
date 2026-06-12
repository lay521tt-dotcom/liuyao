# export-snapshot: DB -> 前端数据快照(唯一数据通道, 禁止手改JSON)
import json, subprocess
def q(sql):
    r=subprocess.run(['runuser','-u','postgres','--','psql','-d','liuyao','-t','-A','-F',chr(9),'-c',sql],capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    return [ (l.split(chr(9))+['']*9)[: max(9, l.count(chr(9))+1)][:9] if False else l.split(chr(9)) for l in r.stdout.split(chr(10)) if l]
hex_rows=q("""SELECT h.id,h.name,h.binary_code,t.name,h.palace_index,h.shi_position,h.ying_position,
 coalesce(h.gua_ci,''),coalesce(h.gua_annotation,''),coalesce(h.gua_modern,'') FROM hexagram h JOIN trigram t ON t.id=h.palace_trigram_id ORDER BY h.id""")
naj=q("SELECT hexagram_id,line_position,tian_gan,di_zhi,wu_xing FROM najia ORDER BY hexagram_id,line_position")
ls=q("SELECT day_gan,first_liushen FROM liushen_rule")
xk=q("SELECT day_ganzhi,kong1,kong2 FROM xun_kong")
yt=q("SELECT hexagram_id,line_position,yao_ci,coalesce(annotation,'') FROM yao_text ORDER BY hexagram_id,line_position")
assert len(hex_rows)==64 and len(naj)==384 and len(xk)==60, "快照样本量校验失败"
snap={"version":1,
 "hexagrams":{r[2]:{"id":int(r[0]),"name":r[1],"palace":r[3],"palaceIndex":int(r[4]),"shi":int(r[5]),"ying":int(r[6]),"guaCi":r[7],"guaAnn":r[8],"guaModern":r[9]} for r in hex_rows},
 "najia":{}, "liushen":{r[0]:r[1] for r in ls}, "xunkong":{r[0]:[r[1],r[2]] for r in xk},
 "yaoText":{f"{r[0]}-{r[1]}":{"ci":r[2],"ann":r[3]} for r in yt},
 "idToBinary":{int(r[0]):r[2] for r in hex_rows}}

jq=q("SELECT term_name, to_char(exact_time AT TIME ZONE 'Asia/Shanghai','YYYY-MM-DD\"T\"HH24:MI') FROM solar_term WHERE term_name IN ('立春','惊蛰','清明','立夏','芒种','小暑','立秋','白露','寒露','立冬','大雪','小寒') ORDER BY exact_time")
BR={'立春':'寅','惊蛰':'卯','清明':'辰','立夏':'巳','芒种':'午','小暑':'未','立秋':'申','白露':'酉','寒露':'戌','立冬':'亥','大雪':'子','小寒':'丑'}
snap["jieqi"]=[[t,BR[n]] for n,t in jq]
for hid,pos,g,z,w in naj: snap["najia"].setdefault(hid,{})[pos]={"gan":g,"zhi":z,"wuXing":w}
json.dump(snap,open(__import__('os').path.join(__import__('os').path.dirname(__file__),'data-snapshot.json'),'w'),ensure_ascii=False)
print("快照导出完成: 卦64 纳甲384 旬空60 爻辞",len(yt))
