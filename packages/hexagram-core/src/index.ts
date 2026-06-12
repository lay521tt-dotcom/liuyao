// packages/hexagram-core/src/index.ts
// 排盘引擎: 纯函数, 全部卦理数据来自快照(开发文档6.1纪律), 禁止硬编码卦理
export type YaoValue = 6 | 7 | 8 | 9;
export interface Snapshot {
  hexagrams: Record<string, { id: number; name: string; palace: string; palaceIndex: number; shi: number; ying: number; guaCi: string; guaAnn: string }>;
  najia: Record<string, Record<string, { gan: string; zhi: string; wuXing: string }>>;
  liushen: Record<string, string>;
  xunkong: Record<string, [string, string]>;
  yaoText: Record<string, { ci: string; ann: string }>;
  idToBinary: Record<string, string>;
  jieqi: [string, string][]; // ["YYYY-MM-DDTHH:MM"(北京时间), 月支] 升序
}

const GAN = '甲乙丙丁戊己庚辛壬癸';
const ZHI = '子丑寅卯辰巳午未申酉戌亥';
const TRI_WX: Record<string, string> = { 乾: '金', 兑: '金', 离: '火', 震: '木', 巽: '木', 坎: '水', 艮: '土', 坤: '土' };
const SHENG: Record<string, string> = { 木: '火', 火: '土', 土: '金', 金: '水', 水: '木' };
const KE: Record<string, string> = { 木: '土', 土: '水', 水: '火', 火: '金', 金: '木' };
const LIUSHEN_SEQ = ['青龙', '朱雀', '勾陈', '腾蛇', '白虎', '玄武'];
const CHONG: Record<string, string> = { 子: '午', 午: '子', 丑: '未', 未: '丑', 寅: '申', 申: '寅', 卯: '酉', 酉: '卯', 辰: '戌', 戌: '辰', 巳: '亥', 亥: '巳' };

// ---- ganzhi-calendar ----
// 日柱锚点: 1949-10-01 = 甲子日(史载锚点); 23点换日【甲方定稿口径】
const ANCHOR_UTC = Date.UTC(1949, 9, 1);
// 历法口径: 四柱按北京时间(UTC+8)推算; 输入含时区偏移时先换算为北京墙上时间.
// 月支分界采用快照中的权威节气数据(寿星天文历法, 双库交叉验证), 交节时刻起即入新月.
const WUHU: Record<string, string> = { 甲: '丙', 己: '丙', 乙: '戊', 庚: '戊', 丙: '庚', 辛: '庚', 丁: '壬', 壬: '壬', 戊: '甲', 癸: '甲' };
const WUSHU: Record<string, string> = { 甲: '甲', 己: '甲', 乙: '丙', 庚: '丙', 丙: '戊', 辛: '戊', 丁: '庚', 壬: '庚', 戊: '壬', 癸: '壬' };
const jiazi = (n: number) => GAN[((n % 10) + 10) % 10] + ZHI[((n % 12) + 12) % 12];

export interface LocalTime { y: number; mo: number; d: number; h: number; mi: number }
export function parseLocal(iso: string): LocalTime {
  const m = iso.match(/(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::\d{2})?(Z|[+-]\d{2}:?\d{2})?/);
  if (!m) throw new Error('bad datetime: ' + iso);
  let ms = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
  const tz = m[6];
  if (tz) { // 有时区信息: 换算为北京墙上时间(UTC+8)
    let off = 0;
    if (tz !== 'Z') { const t = tz.replace(':', ''); off = (t[0] === '-' ? -1 : 1) * (+t.slice(1, 3) * 60 + +t.slice(3, 5)); }
    ms = ms - off * 60000 + 480 * 60000;
  } // 无时区信息: 视为北京时间(产品口径)
  const d = new Date(ms);
  return { y: d.getUTCFullYear(), mo: d.getUTCMonth() + 1, d: d.getUTCDate(), h: d.getUTCHours(), mi: d.getUTCMinutes() };
}
function addDays(t: LocalTime, n: number): LocalTime {
  const dt = new Date(Date.UTC(t.y, t.mo - 1, t.d + n));
  return { y: dt.getUTCFullYear(), mo: dt.getUTCMonth() + 1, d: dt.getUTCDate(), h: t.h, mi: t.mi };
}
const fmt = (t: LocalTime) => `${String(t.y).padStart(4, '0')}-${String(t.mo).padStart(2, '0')}-${String(t.d).padStart(2, '0')}T${String(t.h).padStart(2, '0')}:${String(t.mi).padStart(2, '0')}`;
export function toSiZhu(t0: LocalTime, jieqi: [string, string][]) {
  // 日柱(23点换日)
  const t = t0.h >= 23 ? addDays(t0, 1) : t0;
  const days = Math.round((Date.UTC(t.y, t.mo - 1, t.d) - ANCHOR_UTC) / 86400000);
  const day = jiazi(days);
  // 月支与年柱: 查权威节气表(交节时刻起即入新月/新年)
  const key = fmt(t0);
  let idx = -1;
  for (let i = 0; i < jieqi.length; i++) { if (jieqi[i][0] <= key) idx = i; else break; }
  if (idx < 0) throw new Error('日期早于节气表范围: ' + key);
  const mBranch = jieqi[idx][1];
  let gzYearNum = t0.y;
  // 最近一个已过立春所在公历年 = 干支年
  for (let i = idx; i >= 0; i--) { if (jieqi[i][1] === '寅') { gzYearNum = +jieqi[i][0].slice(0, 4); break; } }
  const yearGz = jiazi(gzYearNum - 4);
  // 月柱天干: 五虎遁
  const mOff = (ZHI.indexOf(mBranch) - ZHI.indexOf('寅') + 12) % 12;
  const month = GAN[(GAN.indexOf(WUHU[yearGz[0]]) + mOff) % 10] + mBranch;
  // 时柱: 五鼠遁(日干以换日后的为准)
  const hZhi = ZHI[Math.floor((t0.h + 1) / 2) % 12];
  const hour = GAN[(GAN.indexOf(WUSHU[day[0]]) + ZHI.indexOf(hZhi)) % 10] + hZhi;
  return { year: yearGz, month, day, hour };
}

// ---- 排盘流水线 ----
const flip = (b: string, p: number) => b.slice(0, p - 1) + (b[p - 1] === '1' ? '0' : '1') + b.slice(p);
function liuQin(palaceWx: string, lineWx: string): string {
  if (palaceWx === lineWx) return '兄弟';
  if (SHENG[lineWx] === palaceWx) return '父母';
  if (SHENG[palaceWx] === lineWx) return '子孙';
  if (KE[lineWx] === palaceWx) return '官鬼';
  return '妻财';
}
export function paiPan(input: { yaos: YaoValue[]; datetime: string }, snap: Snapshot) {
  if (input.yaos.length !== 6 || input.yaos.some(y => ![6, 7, 8, 9].includes(y))) throw new Error('yaos须为6个6/7/8/9');
  const ben = input.yaos.map(y => (y === 7 || y === 9 ? '1' : '0')).join('');
  const moving = input.yaos.map((y, i) => (y === 6 || y === 9 ? i + 1 : 0)).filter(Boolean) as number[];
  let bianB = ben; for (const m of moving) bianB = flip(bianB, m);
  const H = snap.hexagrams[ben]; if (!H) throw new Error('未知卦象 ' + ben);
  const HB = snap.hexagrams[bianB];
  const siZhu = toSiZhu(parseLocal(input.datetime), snap.jieqi);
  const kong = snap.xunkong[siZhu.day]; if (!kong) throw new Error('旬空表缺 ' + siZhu.day);
  const mBranch = siZhu.month[1];
  const startLs = LIUSHEN_SEQ.indexOf(snap.liushen[siZhu.day[0]]);
  const palaceWx = TRI_WX[H.palace];
  const nj = snap.najia[String(H.id)];
  const lines = Array.from({ length: 6 }, (_, i) => {
    const L = nj[String(i + 1)];
    const isMv = moving.includes(i + 1);
    return {
      pos: i + 1,
      yinYang: ben[i] === '1' ? 'yang' : 'yin',
      isMoving: isMv,
      naJia: { gan: L.gan, zhi: L.zhi, wuXing: L.wuXing },
      liuQin: liuQin(palaceWx, L.wuXing),
      liuShen: LIUSHEN_SEQ[(startLs + i) % 6],
      shiYing: H.shi === i + 1 ? 'shi' : H.ying === i + 1 ? 'ying' : null,
      isXunKong: kong.includes(L.zhi),
      isYueBreak: CHONG[mBranch] === L.zhi,
      changedYinYang: isMv ? (ben[i] === '1' ? 'yin' : 'yang') : null,
    };
  });
  return {
    benGua: { name: H.name, palace: H.palace, palaceIndex: H.palaceIndex, shi: H.shi, ying: H.ying, binary: ben },
    bianGua: moving.length ? { name: HB.name, palace: HB.palace, palaceIndex: HB.palaceIndex, binary: bianB } : null,
    siZhu, xunKong: kong, yueJian: mBranch, lines,
  };
}
// 掷爻: 密码学随机, 三枚独立; 任何手势参数不得进入本函数(交互说明书4.4)
export function throwCoins(rand?: () => number): YaoValue {
  const g = rand ?? (() => { const a = new Uint8Array(1); (globalThis.crypto as Crypto).getRandomValues(a); return a[0] & 1; });
  const backs = g() + g() + g();
  return ([6, 7, 8, 9] as YaoValue[])[backs];
}
