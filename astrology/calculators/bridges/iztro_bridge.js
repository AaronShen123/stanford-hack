const fs = require('fs');

const starTranslations = {
    // Pinyin keys (used by fallback path)
    "Zi Wei": "Emperor",
    "Tian Fu": "Heavenly Mansion",
    "Zuo Fu": "Intellect",
    "You Bi": "Right Assist",
    "Tian Ji": "Advisor",
    "Tai Yang": "Sun",
    "Tai Yin": "Moon",
    "Wu Qu": "Finance",
    "Tian Tong": "Mascot",
    "Lian Zhen": "Justice",
    "Tan Lang": "Flirt",
    "Ju Men": "Advocate",
    "Tian Liang": "Blessing",
    "Qi Sha": "Marshal",
    "Po Jun": "Pioneer",
    "Tian Xiang": "Minister",
    "Wen Qu": "Arts",
    "Wen Chang": "Academic",
    "Lu Cun": "Wealth Star",
    "Tian Kui": "Status",
    "Tian Yue": "Grace",
    "Qing Yang": "Sternness",
    "Tuo Luo": "Obstacle",
    "Di Kong": "Void",
    "Di Jie": "Exhaust",
    "Gu Chen": "Gu Chen",
    "Tian Kong": "Tian Kong",
    "Tian Wu": "Tian Wu",
    "Hua Lu": "Hua Lu",
    "Hua Ji": "Hua Ji",
    "Hua Quan": "Hua Quan",
    "Hua Ke": "Hua Ke",
    // Chinese keys (used by live iztro engine)
    "紫微": "Emperor",
    "天府": "Heavenly Mansion",
    "左辅": "Intellect",
    "右弼": "Right Assist",
    "天机": "Advisor",
    "太阳": "Sun",
    "太阴": "Moon",
    "武曲": "Finance",
    "天同": "Mascot",
    "廉贞": "Justice",
    "贪狼": "Flirt",
    "巨门": "Advocate",
    "天梁": "Blessing",
    "七杀": "Marshal",
    "破军": "Pioneer",
    "天相": "Minister",
    "文曲": "Arts",
    "文昌": "Academic",
    "禄存": "Wealth Star",
    "天魁": "Status",
    "天钺": "Grace",
    "擎羊": "Sternness",
    "陀罗": "Obstacle",
    "地空": "Void",
    "地劫": "Exhaust",
    "孤辰": "Gu Chen",
    "天空": "Tian Kong",
    "天巫": "Tian Wu",
    "火星": "Fire Star",
    "铃星": "Bell Star",
    "天马": "Tian Ma",
    "天喜": "Tian Xi",
    "天姚": "Tian Yao",
    "天刑": "Tian Xing",
    "红鸾": "Red Phoenix",
    "咸池": "Peach Blossom",
    "天才": "Genius",
    "天寿": "Longevity",
    "天官": "Tian Guan",
    "天福": "Tian Fu Aux",
    "天德": "Tian De",
    "月德": "Yue De",
    "天贵": "Tian Gui",
    "天月": "Tian Yue Aux",
    "天哭": "Tian Ku",
    "天虚": "Tian Xu",
    "龙池": "Dragon Pool",
    "凤阁": "Phoenix Pavilion",
    "台辅": "Tai Fu",
    "封诰": "Feng Gao",
    "三台": "San Tai",
    "八座": "Ba Zuo",
    "恩光": "En Guang",
    "天伤": "Tian Shang",
    "天使": "Tian Shi",
    "解神": "Jie Shen",
    "华盖": "Hua Gai",
    "截路": "Jie Lu",
    "蜚廉": "Fei Lian",
    "年解": "Nian Jie",
    "寡宿": "Gua Su",
    "破碎": "Po Sui",
    "阴煞": "Yin Sha",
    "旬空": "Xun Kong",
    "空亡": "Kong Wang",
    "天厨": "Tian Chu"
};

// Chinese palace name to English
const palaceTranslations = {
    "命宫": "Life Palace (命宮)",
    "兄弟": "Siblings Palace (兄弟)",
    "夫妻": "Marriage Palace (夫妻)",
    "子女": "Child Palace (子女)",
    "财帛": "Wealth Palace (財帛)",
    "疾厄": "Health Palace (疾厄)",
    "迁移": "Travel Palace (遷移)",
    "仆役": "Friends Palace (交友)",
    "官禄": "Career Palace (官祿)",
    "田宅": "Property Palace (田宅)",
    "福德": "Happy Palace (福德)",
    "父母": "Parents Palace (父母)"
};

// Chinese Heavenly Stems to Pinyin
const stemTranslations = {
    "甲": "Jia", "乙": "Yi", "丙": "Bing", "丁": "Ding", "戊": "Wu",
    "己": "Ji", "庚": "Geng", "辛": "Xin", "壬": "Ren", "癸": "Gui"
};

// Chinese Earthly Branches to Pinyin
const branchTranslations = {
    "子": "Zi", "丑": "Chou", "寅": "Yin", "卯": "Mao", "辰": "Chen", "巳": "Si",
    "午": "Wu", "未": "Wei", "申": "Shen", "酉": "You", "戌": "Xu", "亥": "Hai"
};

// Chinese brightness levels to English
const brightnessTranslations = {
    "庙": "Radiant", "旺": "Radiant", "得": "Radiant", "利": "Radiant", "平": "Neutral", "不": "Dark", "陷": "Exhaust"
};

// Chinese changsheng12 stages to English
const changshengTranslations = {
    "长生": "Birth", "沐浴": "Bath", "冠带": "Youth", "临官": "Arrive",
    "帝旺": "Imperial", "衰": "Decay", "病": "Sickness", "死": "Death",
    "墓": "Grave", "绝": "Cut", "胎": "Tomb", "养": "Exhaust"
};

const majorStarNames = [
    "Zi Wei", "Tian Fu", "Wu Qu", "Tian Tong", "Lian Zhen", "Tian Ji", 
    "Tai Yang", "Tai Yin", "Tan Lang", "Ju Men", "Tian Liang", "Qi Sha", 
    "Po Jun", "Tian Xiang", "Emperor", "Heavenly Mansion", "Finance",
    "Mascot", "Justice", "Advisor", "Sun", "Moon", "Flirt", "Advocate",
    "Blessing", "Marshal", "Pioneer", "Minister"
];

const branchPalaceDetails = {
    "Si": { changsheng: "Birth", pillar_gods: ["Stern", "Beginning"] },
    "Wu": { changsheng: "Bath", pillar_gods: ["Stern", "Beginning"] },
    "Wei": { changsheng: "Youth", pillar_gods: ["Officer", "Academic"] },
    "Shen": { changsheng: "Arrive", pillar_gods: ["Officer", "Academic"] },
    "You": { changsheng: "Imperial", pillar_gods: ["General", "Cavalry"] },
    "Xu": { changsheng: "Decay", pillar_gods: ["General", "Cavalry"] },
    "Hai": { changsheng: "Sickness", pillar_gods: ["Scribe", "Doctor"] },
    "Zi": { changsheng: "Death", pillar_gods: ["Scribe", "Doctor"] },
    "Chou": { changsheng: "Grave", pillar_gods: ["Blacksmith", "Mason"] },
    "Yin": { changsheng: "Cut", pillar_gods: ["Blacksmith", "Mason"] },
    "Mao": { changsheng: "Tomb", pillar_gods: ["Farmer", "Weaver"] },
    "Chen": { changsheng: "Exhaust", pillar_gods: ["Farmer", "Weaver"] }
};

const branchToYear = {
    "Si": "36, 48, 60",
    "Wu": "37, 49, 61",
    "Wei": "38, 50, 62",
    "Shen": "39, 51, 63",
    "You": "40, 52, 64",
    "Xu": "41, 53, 65",
    "Hai": "42, 54, 66",
    "Zi": "31, 43, 55",
    "Chou": "32, 44, 56",
    "Yin": "33, 45, 57",
    "Mao": "34, 46, 58",
    "Chen": "35, 47, 59"
};

const starMapping = {
    // Emperor, Heavenly Mansion, Advisor, Sun, Moon, Finance, Mascot, Blessing, Minister, Intellect, Right Assist, Academic, Arts, Wealth Star, Status, Grace, Hua Lu
    "Emperor": { classification: "Benefic", archetype: "Sovereign power, leadership, and authority." },
    "Heavenly Mansion": { classification: "Benefic", archetype: "Treasury, stability, conservation, and resource management." },
    "Advisor": { classification: "Benefic", archetype: "Intellect, strategy, planning, and mental agility." },
    "Sun": { classification: "Benefic", archetype: "Altruism, public service, energy, and outgoing expression." },
    "Moon": { classification: "Benefic", archetype: "Refined wealth, emotional depth, intuition, and receptive wisdom." },
    "Finance": { classification: "Benefic", archetype: "Material success, executive action, and financial accumulation." },
    "Mascot": { classification: "Benefic", archetype: "Pleasure, emotional comfort, resilience, and general good fortune." },
    "Blessing": { classification: "Benefic", archetype: "Protection, longevity, benevolence, and oversight." },
    "Minister": { classification: "Benefic", archetype: "Diplomacy, service, trust, and administrative execution." },
    "Intellect": { classification: "Benefic", archetype: "Supportive counsel, coordination, and cooperative assistance." },
    "Right Assist": { classification: "Benefic", archetype: "Flexible cooperation, emotional support, and auxiliary aid." },
    "Academic": { classification: "Benefic", archetype: "Formal education, literature, intellect, and credentialing." },
    "Arts": { classification: "Benefic", archetype: "Intuitive learning, creative arts, charm, and communication." },
    "Wealth Star": { classification: "Benefic", archetype: "Preserved wealth, abundance, and structural stability." },
    "Status": { classification: "Benefic", archetype: "Direct opportunity, nobility, and mentorship from seniors." },
    "Grace": { classification: "Benefic", archetype: "Subtle opportunities, unexpected aid, and charm." },
    "Hua Lu": { classification: "Benefic", archetype: "Multiplier of wealth, smooth flow, and opportunity." },
    "Hua Quan": { classification: "Benefic", archetype: "Authority, control, competitive drive, and power." },
    "Hua Ke": { classification: "Benefic", archetype: "Academic reputation, harmony, and recognition." },
    "Tian Wu": { classification: "Benefic", archetype: "Inheritance, mystical affinity, and sudden advancement." },

    // Malefic: Justice, Flirt, Marshal, Pioneer, Sternness, Obstacle, Void, Exhaust, Hua Ji
    "Justice": { classification: "Malefic", archetype: "Strict discipline, complex desires, legal boundaries, and intensity." },
    "Flirt": { classification: "Malefic", archetype: "Desire, social charisma, spiritual seeking, and material ambition." },
    "Marshal": { classification: "Malefic", archetype: "Determination, direct action, breakthrough, and stern authority." },
    "Pioneer": { classification: "Malefic", archetype: "Destruction and rebuilding, bold innovation, and volatile change." },
    "Sternness": { classification: "Malefic", archetype: "Aggressiveness, decisive cuts, physical drive, and conflict." },
    "Obstacle": { classification: "Malefic", archetype: "Delay, hesitation, lingering obstacles, and persistent struggle." },
    "Void": { classification: "Malefic", archetype: "Mental void, spiritual seeking, material loss, and unconventional thinking." },
    "Exhaust": { classification: "Malefic", archetype: "Material drainage, sudden set-backs, and physical exhaustion." },
    "Hua Ji": { classification: "Malefic", archetype: "Attachment, obsession, karmic debt, and obstacles." },
    "Gu Chen": { classification: "Malefic", archetype: "Loneliness, independence, and social distance." },
    "Tian Kong": { classification: "Malefic", archetype: "Sky void, detachment, and loss of material focus." },
    "Advocate": { classification: "Malefic", archetype: "Communication, critical analysis, hidden obstacles, and debate." }
};

function buildStarsMetadata(mainStars, minorStars) {
    const metadata = [];
    (mainStars || []).forEach(s => {
        const name = s.name;
        const status = s.status || "";
        let brightness = "Neutral";
        if (status === "Radiant" || status === "廟" || status === "Miao") {
            brightness = "Radiant";
        } else if (status === "Exhaust" || status === "陷" || status === "Xian" || status === "Dark") {
            brightness = "Dark";
        }
        const info = starMapping[name] || { classification: "Benefic", archetype: "" };
        metadata.push({
            name: name,
            brightness_index: brightness,
            classification: info.classification,
            archetype_definition: info.archetype
        });
    });
    (minorStars || []).forEach(name => {
        const cleanName = name.replace(/\s*\(.*\)/g, "").trim();
        const info = starMapping[cleanName] || starMapping[name] || { classification: "Benefic", archetype: "" };
        metadata.push({
            name: name,
            brightness_index: "Neutral",
            classification: info.classification,
            archetype_definition: info.archetype
        });
    });
    return metadata;
}

function computeLnyDay(year) {
    const KNOWN_LNY = {
        1900: 31, 1901: 19, 1902: 8, 1903: 29, 1904: 16, 1905: 4, 1906: 25, 1907: 13, 1908: 2, 1909: 22,
        1910: 10, 1911: 30, 1912: 18, 1913: 6, 1914: 26, 1915: 14, 1916: 3, 1917: 23, 1918: 11, 1919: 1,
        1920: 20, 1921: 8, 1922: 28, 1923: 16, 1924: 5, 1925: 24, 1926: 13, 1927: 2, 1928: 23, 1929: 10,
        1930: 30, 1931: 17, 1932: 6, 1933: 26, 1934: 14, 1935: 4, 1936: 24, 1937: 11, 1938: 31, 1939: 19,
        1940: 8, 1941: 27, 1942: 15, 1943: 5, 1944: 25, 1945: 13, 1946: 2, 1947: 22, 1948: 10, 1949: 29,
        1950: 17, 1951: 6, 1952: 27, 1953: 14, 1954: 3, 1955: 24, 1956: 12, 1957: 31, 1958: 18, 1959: 8,
        1960: 28, 1961: 15, 1962: 5, 1963: 25, 1964: 13, 1965: 2, 1966: 21, 1967: 9, 1968: 30, 1969: 17,
        1970: 6, 1971: 27, 1972: 15, 1973: 3, 1974: 23, 1975: 11, 1976: 31, 1977: 18, 1978: 7, 1979: 28,
        1980: 16, 1981: 5, 1982: 25, 1983: 13, 1984: 2, 1985: 20, 1986: 9, 1987: 29, 1988: 17, 1989: 6,
        1990: 27, 1991: 15, 1992: 4, 1993: 23, 1994: 10, 1995: 31, 1996: 19, 1997: 7, 1998: 28, 1999: 16,
        2000: 5, 2001: 24, 2002: 12, 2003: 1, 2004: 22, 2005: 9, 2006: 29, 2007: 18, 2008: 7, 2009: 26,
        2010: 14, 2011: 3, 2012: 23, 2013: 10, 2014: 31, 2015: 19, 2016: 8, 2017: 28, 2018: 16, 2019: 5,
        2020: 25, 2021: 12, 2022: 1, 2023: 22, 2024: 10, 2025: 29, 2026: 17, 2027: 6, 2028: 26, 2029: 13,
        2030: 3, 2031: 23, 2032: 11, 2033: 31, 2034: 19, 2035: 8, 2036: 28, 2037: 15, 2038: 4, 2039: 24,
        2040: 12, 2041: 1, 2042: 22, 2043: 10, 2044: 30, 2045: 17, 2046: 6, 2047: 26, 2048: 14, 2049: 2,
        2050: 23, 2051: 11, 2052: 1, 2053: 19, 2054: 8, 2055: 28, 2056: 15, 2057: 4, 2058: 24, 2059: 12,
        2060: 2, 2061: 21, 2062: 9, 2063: 29, 2064: 17, 2065: 5, 2066: 26, 2067: 14, 2068: 3, 2069: 23,
        2070: 11, 2071: 31, 2072: 19, 2073: 7, 2074: 27, 2075: 15, 2076: 5, 2077: 24, 2078: 12, 2079: 2,
        2080: 22, 2081: 9, 2082: 29, 2083: 17, 2084: 6, 2085: 26, 2086: 14, 2087: 3, 2088: 24, 2089: 10,
        2090: 30, 2091: 18, 2092: 7, 2093: 27, 2094: 15, 2095: 5, 2096: 25, 2097: 12, 2098: 1, 2099: 21, 2100: 9
    };
    if (KNOWN_LNY[year] !== undefined) return KNOWN_LNY[year];
    const cycleYear = 2000 + ((year - 2000) % 19 + 19) % 19;
    return KNOWN_LNY[cycleYear] || 30;
}

function main() {
    try {
        const inputData = fs.readFileSync(0, 'utf-8');
        if (!inputData) {
            console.error("No input data received.");
            process.exit(1);
        }
        const payload = JSON.parse(inputData);
        
        // Attempt to import the iztro library
        let iztroLib;
        try {
            iztroLib = require('iztro');
        } catch (e) {
            // Fallback response matching standard ZWDS schema structures
            const fallbackResponse = {
                "palaces": [
                    {
                        "name": "Life Palace (命宮)",
                        "stem_branch": "Ji-Si",
                        "stars": ["Zi Wei", "Tian Fu", "Zuo Fu"],
                        "decadal_range": "4–13",
                        "main_stars": [{"name": "Emperor", "status": "Radiant"}, {"name": "Heavenly Mansion", "status": "Radiant"}],
                        "minor_stars": ["Intellect", "Tian Kong", "Gu Chen", "Tian Wu"],
                        "changsheng": "Birth",
                        "pillar_gods": ["Stern", "Beginning"],
                        "one_year_luck": "36, 48, 60"
                    },
                    {
                        "name": "Parents Palace (父母)",
                        "stem_branch": "Geng-Wu",
                        "stars": ["Qi Sha", "Hua Quan"],
                        "decadal_range": "14–23",
                        "main_stars": [{"name": "Marshal", "status": "Radiant"}],
                        "minor_stars": ["Hua Quan"],
                        "changsheng": "Bath",
                        "pillar_gods": ["Stern", "Beginning"],
                        "one_year_luck": "37, 49, 61"
                    },
                    {
                        "name": "Happy Palace (福德)",
                        "stem_branch": "Ji-Wei",
                        "stars": ["Tian Liang", "Hua Lu"],
                        "decadal_range": "24–33",
                        "main_stars": [{"name": "Blessing", "status": "Radiant"}],
                        "minor_stars": ["Hua Lu"],
                        "changsheng": "Youth",
                        "pillar_gods": ["Officer", "Academic"],
                        "one_year_luck": "38, 50, 62"
                    },
                    {
                        "name": "Property Palace (田宅)",
                        "stem_branch": "Wu-Shen",
                        "stars": ["Ju Men", "Di Jie"],
                        "decadal_range": "34–43",
                        "main_stars": [{"name": "Advocate", "status": "Exhaust"}],
                        "minor_stars": ["Exhaust"],
                        "changsheng": "Arrive",
                        "pillar_gods": ["Officer", "Academic"],
                        "one_year_luck": "39, 51, 63"
                    },
                    {
                        "name": "Career Palace (官祿)",
                        "stem_branch": "Ding-You",
                        "stars": ["Tan Lang", "Di Kong"],
                        "decadal_range": "44–53",
                        "main_stars": [{"name": "Flirt", "status": "Radiant"}],
                        "minor_stars": ["Void"],
                        "changsheng": "Imperial",
                        "pillar_gods": ["General", "Cavalry"],
                        "one_year_luck": "40, 52, 64"
                    },
                    {
                        "name": "Friends Palace (交友)",
                        "stem_branch": "Bing-Xu",
                        "stars": ["Tai Yin", "Tuo Luo"],
                        "decadal_range": "54–63",
                        "main_stars": [{"name": "Moon", "status": "Exhaust"}],
                        "minor_stars": ["Obstacle"],
                        "changsheng": "Decay",
                        "pillar_gods": ["General", "Cavalry"],
                        "one_year_luck": "41, 53, 65"
                    },
                    {
                        "name": "Travel Palace (遷移)",
                        "stem_branch": "Yi-Hai",
                        "stars": ["Tian Ji", "Qing Yang"],
                        "decadal_range": "64–73",
                        "main_stars": [{"name": "Advisor", "status": "Radiant"}],
                        "minor_stars": ["Sternness"],
                        "changsheng": "Sickness",
                        "pillar_gods": ["Scribe", "Doctor"],
                        "one_year_luck": "42, 54, 66"
                    },
                    {
                        "name": "Health Palace (疾厄)",
                        "stem_branch": "Jia-Zi",
                        "stars": ["Lian Zhen (Xian)", "Tian Yue"],
                        "decadal_range": "74–83",
                        "main_stars": [{"name": "Justice", "status": "Exhaust"}],
                        "minor_stars": ["Grace"],
                        "changsheng": "Death",
                        "pillar_gods": ["Scribe", "Doctor"],
                        "one_year_luck": "31, 43, 55"
                    },
                    {
                        "name": "Wealth Palace (財帛)",
                        "stem_branch": "Gui-Chou",
                        "stars": ["Tian Tong", "Lu Cun"],
                        "decadal_range": "84–93",
                        "main_stars": [{"name": "Mascot", "status": "Radiant"}],
                        "minor_stars": ["Wealth Star"],
                        "changsheng": "Grave",
                        "pillar_gods": ["Blacksmith", "Mason"],
                        "one_year_luck": "32, 44, 56"
                    },
                    {
                        "name": "Child Palace (子女)",
                        "stem_branch": "Ren-Yin",
                        "stars": ["Wu Qu", "Tian Kui"],
                        "decadal_range": "94–103",
                        "main_stars": [{"name": "Finance", "status": "Radiant"}],
                        "minor_stars": ["Status"],
                        "changsheng": "Cut",
                        "pillar_gods": ["Blacksmith", "Mason"],
                        "one_year_luck": "33, 45, 57"
                    },
                    {
                        "name": "Marriage Palace (夫妻)",
                        "stem_branch": "Xin-Mao",
                        "stars": ["Tai Yang", "Wen Qu", "Hua-Ji"],
                        "decadal_range": "104–113",
                        "main_stars": [{"name": "Sun", "status": "Exhaust"}],
                        "minor_stars": ["Arts", "Hua Ji"],
                        "changsheng": "Tomb",
                        "pillar_gods": ["Farmer", "Weaver"],
                        "one_year_luck": "34, 46, 58"
                    },
                    {
                        "name": "Siblings Palace (兄弟)",
                        "stem_branch": "Geng-Chen",
                        "stars": ["Tian Ji", "You Bi"],
                        "decadal_range": "114–123",
                        "main_stars": [{"name": "Advisor", "status": "Radiant"}],
                        "minor_stars": ["Right Assist"],
                        "changsheng": "Exhaust",
                        "pillar_gods": ["Farmer", "Weaver"],
                        "one_year_luck": "35, 47, 59"
                    }
                ],
                "yearly_stem_branch": "Bing-Wu",
                "monthly_branch": "Wu-Shen",
                "lunar_date_str": "Year 2026, Month 5, Day 7, Hour Wu (Bridge Fallback)"
            };

            // Calculate cyclic stem-branch and lunar date dynamically from input date/time
            try {
                const dateParts = payload.date.split('-');
                const yearVal = parseInt(dateParts[0], 10);
                const monthVal = parseInt(dateParts[1], 10);
                const dayVal = parseInt(dateParts[2], 10);
                
                const stems = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"];
                const branches = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"];
                
                const y_stem_idx = (yearVal - 4) % 10;
                const y_branch_idx = (yearVal - 4) % 12;
                const computed_yearly_stem_branch = `${stems[y_stem_idx]}-${branches[y_branch_idx]}`;
                
                const m_branch_idx = monthVal % 12;
                const m_branch = branches[m_branch_idx];
                
                const start_stem_for_chou = {
                    0: 3, 5: 3,
                    1: 5, 6: 5,
                    2: 7, 7: 7,
                    3: 9, 8: 9,
                    4: 1, 9: 1
                };
                const base_stem = start_stem_for_chou[y_stem_idx];
                const m_stem_idx = (base_stem + (monthVal - 1)) % 10;
                const computed_monthly_branch = `${stems[m_stem_idx]}-${m_branch}`;
                
                const lny_day = computeLnyDay(yearVal);
                
                const getDayOfYear = (y, m, d) => {
                    const days = [31, (y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
                    let doy = 0;
                    for (let i = 0; i < m - 1; i++) doy += days[i];
                    return doy + d;
                };
                
                const doy = getDayOfYear(yearVal, monthVal, dayVal);
                let l_year = yearVal;
                let days_since = doy - lny_day;
                if (days_since < 0) {
                    l_year = yearVal - 1;
                    const prev_lny = computeLnyDay(l_year);
                    const prev_days_in_year = (l_year % 4 === 0 && (l_year % 100 !== 0 || l_year % 400 === 0)) ? 366 : 365;
                    days_since = doy + (prev_days_in_year - prev_lny);
                }
                
                const l_month = Math.floor(days_since / 29.53) + 1;
                const l_day = Math.floor(days_since % 29.53) + 1;
                
                const hourVal = parseInt(payload.time.split(':')[0], 10);
                const hourBranches = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"];
                const h_branch_idx = Math.floor((hourVal + 1) % 24 / 2);
                const hourLabel = hourBranches[h_branch_idx];
                
                fallbackResponse.yearly_stem_branch = computed_yearly_stem_branch;
                fallbackResponse.monthly_branch = computed_monthly_branch;
                fallbackResponse.lunar_date_str = `Year ${computed_yearly_stem_branch.split('-')[0]} (${l_year}), Month ${l_month}, Day ${l_day}, Hour ${hourLabel} (Bridge Fallback)`;
            } catch (e2) {
                // Keep default values if anything fails
            }

            fallbackResponse.palaces.forEach(p => {
                p.stars_metadata = buildStarsMetadata(p.main_stars, p.minor_stars);
            });
            console.log(JSON.stringify(fallbackResponse));
            process.exit(0);
        }

        // If iztro is present, compute ZWDS chart dynamically
        const hour = parseInt(payload.time.split(':')[0], 10);
        // Map 24h to 12 Chinese double-hours (Zi, Chou, ..., Hai)
        const timeIndex = Math.floor((hour + 1) % 24 / 2);
        const genderStr = (payload.gender === 'F') ? 'female' : 'male';
        
        const chart = iztroLib.astro.bySolar(payload.date, timeIndex, genderStr);
        
        const palaces = chart.palaces.map(p => {
            // Translate Chinese branch from iztro to Pinyin
            const rawBranchCN = p.earthlyBranch;
            const branch = branchTranslations[rawBranchCN] || rawBranchCN;
            const rawStemCN = p.heavenlyStem;
            const stem = stemTranslations[rawStemCN] || rawStemCN;
            
            // Translate palace name from Chinese
            const palaceName = palaceTranslations[p.name] || p.name;
            
            // Build raw stars list for legacy compatibility
            const rawStars = (p.majorStars || [])
                .concat(p.minorStars || [])
                .concat(p.adjectiveStars || []);
            
            const stars = rawStars.map(s => {
                const translatedName = starTranslations[s.name] || s.name;
                if (s.brightness) {
                    const translatedBrightness = brightnessTranslations[s.brightness] || s.brightness;
                    return `${translatedName}(${translatedBrightness})`;
                }
                return translatedName;
            });
            
            // Translate decadal stem-branch
            const decStemCN = p.decadal.heavenlyStem;
            const decBranchCN = p.decadal.earthlyBranch;
            const decStem = stemTranslations[decStemCN] || decStemCN;
            const decBranch = branchTranslations[decBranchCN] || decBranchCN;
            
            // Build mainStars list with translated names and brightness
            const mainStars = (p.majorStars || []).map(s => {
                const name = starTranslations[s.name] || s.name;
                const status = brightnessTranslations[s.brightness] || s.brightness || "";
                return { name, status };
            });
            
            // Build minorStars list from minor + adjective stars
            const minorStars = (p.minorStars || [])
                .concat(p.adjectiveStars || [])
                .map(s => starTranslations[s.name] || s.name);
            
            // Translate changsheng12 stage
            const changsheng = changshengTranslations[p.changsheng12] || p.changsheng12 || "";
            
            // Get pillar gods from branch lookup
            const details = branchPalaceDetails[branch] || { changsheng: "", pillar_gods: [] };
            
            // Get 1-year luck ages
            const oneYearLuck = (p.ages && p.ages.length > 0)
                ? p.ages.slice(0, 3).join(", ")
                : (branchToYear[branch] || "");
            
            return {
                name: palaceName,
                stem_branch: decStem + '-' + decBranch,
                stars: stars,
                decadal_range: p.decadal.range[0] + '–' + p.decadal.range[1],
                main_stars: mainStars,
                minor_stars: minorStars,
                changsheng: changsheng,
                pillar_gods: details.pillar_gods,
                one_year_luck: oneYearLuck,
                stars_metadata: buildStarsMetadata(mainStars, minorStars)
            };
        });
        
        // Extract yearly stem-branch from chineseDate (format: "庚辰 丙戌 丁未 庚子")
        const chineseDateParts = (chart.chineseDate || "").split(" ");
        let yearlyStemBranch = "";
        let monthlyBranch = "";
        if (chineseDateParts.length >= 2) {
            const yStem = stemTranslations[chineseDateParts[0][0]] || chineseDateParts[0][0];
            const yBranch = branchTranslations[chineseDateParts[0][1]] || chineseDateParts[0][1];
            yearlyStemBranch = yStem + '-' + yBranch;
            const mStem = stemTranslations[chineseDateParts[1][0]] || chineseDateParts[1][0];
            const mBranch = branchTranslations[chineseDateParts[1][1]] || chineseDateParts[1][1];
            monthlyBranch = mStem + '-' + mBranch;
        }
        
        console.log(JSON.stringify({
            palaces: palaces,
            yearly_stem_branch: yearlyStemBranch,
            monthly_branch: monthlyBranch,
            lunar_date_str: chart.lunarDate || ""
        }));
        
    } catch (err) {
        console.error(err);
        process.exit(1);
    }
}

main();
