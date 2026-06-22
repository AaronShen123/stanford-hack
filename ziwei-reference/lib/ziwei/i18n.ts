// English localization for the Zi Wei Dou Shu chart.
// iztro emits Chinese star/palace names; these maps render them in English.
// Star aliases match the companion FastAPI app's conventions for consistency.

export const STEMS_EN = ['Jia', 'Yi', 'Bing', 'Ding', 'Wu', 'Ji', 'Geng', 'Xin', 'Ren', 'Gui'];
export const BRANCHES_EN = ['Zi', 'Chou', 'Yin', 'Mao', 'Chen', 'Si', 'Wu', 'Wei', 'Shen', 'You', 'Xu', 'Hai'];

// 14 major + auxiliary stars.
export const STAR_EN: Record<string, string> = {
  '紫微': 'Emperor', '天机': 'Advisor', '太阳': 'Sun', '武曲': 'Finance', '天同': 'Mascot',
  '廉贞': 'Justice', '天府': 'Treasury', '太阴': 'Moon', '贪狼': 'Flirt', '巨门': 'Advocate',
  '天相': 'Minister', '天梁': 'Blessing', '七杀': 'Marshal', '破军': 'Pioneer',
  '左辅': 'Left Aid', '右弼': 'Right Aid', '文昌': 'Scholar', '文曲': 'Arts',
  '禄存': 'Fortune Star', '天魁': 'Noble (Yang)', '天钺': 'Noble (Yin)',
  '擎羊': 'Ram Blade', '陀罗': 'Spinning Top', '火星': 'Fire Star', '铃星': 'Bell Star',
  '地空': 'Void', '地劫': 'Plunder', '天马': 'Sky Horse', '天喜': 'Joy', '红鸾': 'Red Phoenix',
  '天姚': 'Charm', '天刑': 'Punishment', '咸池': 'Peach Blossom', '天才': 'Talent',
  '天寿': 'Longevity', '天官': 'Officialdom', '天福': 'Blessing Star', '天巫': 'Shaman',
  '天月': 'Sky Moon', '阴煞': 'Hidden Sha', '解神': 'Resolver', '天空': 'Sky Void',
  '孤辰': 'Loner', '寡宿': 'Solitude', '蜚廉': 'Gossip', '破碎': 'Broken', '华盖': 'Canopy',
  '三台': 'Three Terraces', '八座': 'Eight Seats', '恩光': 'Grace', '天贵': 'Nobility',
  '台辅': 'Aide', '封诰': 'Decree', '龙池': 'Dragon Pool', '凤阁': 'Phoenix Tower',
  '天德': 'Sky Virtue', '月德': 'Moon Virtue', '天厨': 'Kitchen', '截路': 'Blocked Road',
  '旬空': 'Cycle Void', '年解': 'Year Resolver', '天伤': 'Injury', '天使': 'Envoy',
};

// Palace names (iztro form; the 宫 suffix is stripped before lookup).
export const PALACE_EN: Record<string, string> = {
  '命': 'Life', '兄弟': 'Siblings', '夫妻': 'Spouse', '子女': 'Children',
  '财帛': 'Wealth', '疾厄': 'Health', '迁移': 'Travel', '仆役': 'Friends',
  '交友': 'Friends', '官禄': 'Career', '田宅': 'Property', '福德': 'Fortune',
  '父母': 'Parents',
};

// Four transformations 四化.
export const SIHUA_EN: Record<string, string> = { '禄': 'Lu', '权': 'Quan', '科': 'Ke', '忌': 'Ji' };
export const SIHUA_FULL: Record<string, string> = {
  '禄': 'Lu · Fortune', '权': 'Quan · Power', '科': 'Ke · Fame', '忌': 'Ji · Affliction',
};

// Five-Elements Bureau 五行局.
export const BUREAU_EN: Record<string, string> = {
  '水二局': 'Water Bureau (2)', '木三局': 'Wood Bureau (3)', '金四局': 'Metal Bureau (4)',
  '土五局': 'Earth Bureau (5)', '火六局': 'Fire Bureau (6)',
};

export function tStar(name: string): string {
  if (!name) return name;
  // Transit stars carry a 运/流/月/日 prefix (e.g. 运昌, 流魁) — translate the base.
  const m = name.match(/^([运流月日])(.+)$/);
  if (m) {
    const prefix = { '运': 'D.', '流': 'Y.', '月': 'M.', '日': 'd.' }[m[1]] || '';
    return `${prefix}${STAR_EN[m[2]] ?? m[2]}`;
  }
  return STAR_EN[name] ?? name;
}

export function tPalace(name: string): string {
  if (!name) return name;
  const base = name.replace(/宫$/, '');
  return (PALACE_EN[base] ?? PALACE_EN[name] ?? name) + ' Palace';
}

export function tGanzhi(stem: string, branch: string): string {
  return `${stem}-${branch}`; // already pinyin via STEMS_EN/BRANCHES_EN at call site
}

export function tSiHua(s: string): string {
  return SIHUA_EN[s] ?? s;
}

export function tBureau(name: string): string {
  return BUREAU_EN[name] ?? name;
}
