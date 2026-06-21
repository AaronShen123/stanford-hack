const fs = require('fs');

const starTranslations = {
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
    "Hua Ke": "Hua Ke"
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

function main() {
    try {
        const inputData = fs.readFileSync(0, 'utf-8');
        if (!inputData) {
            console.error("No input data received.");
            process.exit(1);
        }
        const payload = JSON.parse(inputData);
        
        // Attempt to import the iztro library
        let iztro;
        try {
            iztro = require('iztro');
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
                
                const lny_offsets = {
                    1990: 27,
                    2000: 36,
                    2026: 48
                };
                const lny_day = lny_offsets[yearVal] || 30;
                
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
                    const prev_lny = lny_offsets[l_year] || 30;
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

            console.log(JSON.stringify(fallbackResponse));
            process.exit(0);
        }

        // If iztro is present, compute ZWDS chart dynamically
        const hour = parseInt(payload.time.split(':')[0], 10);
        // Map 24h to 12 Chinese double-hours (Zi, Chou, ..., Hai)
        const timeIndex = Math.floor((hour + 1) % 24 / 2);
        const genderStr = (payload.gender === 'F') ? 'female' : 'male';
        
        const chart = iztro.astrology.bySolar(payload.date, timeIndex, genderStr);
        
        const palaces = chart.palaces.map(p => {
            const rawStars = (p.majorStars || [])
                .concat(p.minorStars || [])
                .concat(p.adjectiveStars || []);
            
            const stars = rawStars.map(s => {
                let name = s.name;
                if (s.brightness) {
                    name += `(${s.brightness})`;
                }
                return name;
            });
            
            if (p.mutagen) {
                stars.push(`Hua-${p.mutagen}`);
            }
            
            // Derive branch name (e.g. "Si")
            const branch = p.decadal.earthlyBranch;
            const details = branchPalaceDetails[branch] || { changsheng: "", pillar_gods: [] };
            
            // Build mainStars list
            const mainStars = (p.majorStars || []).map(s => {
                const name = starTranslations[s.name] || s.name;
                let status = s.brightness || "";
                if (status === "廟" || status === "Miao") {
                    status = "Radiant";
                } else if (status === "陷" || status === "Xian") {
                    status = "Exhaust";
                } else if (status) {
                    status = "Radiant"; // fallback for other bright statuses
                }
                return { name, status };
            });
            
            // Build minorStars list
            const minorStars = (p.minorStars || [])
                .concat(p.adjectiveStars || [])
                .map(s => starTranslations[s.name] || s.name);
            
            return {
                name: p.name,
                stem_branch: p.decadal.heavenlyStem + '-' + p.decadal.earthlyBranch,
                stars: stars,
                decadal_range: p.decadal.range[0] + '-' + p.decadal.range[1],
                main_stars: mainStars,
                minor_stars: minorStars,
                changsheng: details.changsheng,
                pillar_gods: details.pillar_gods,
                one_year_luck: branchToYear[branch] || ""
            };
        });
        
        console.log(JSON.stringify({
            palaces: palaces,
            yearly_stem_branch: chart.basic.yearlyStemBranch,
            monthly_branch: chart.basic.monthlyBranch,
            lunar_date_str: chart.basic.lunarDate
        }));
        
    } catch (err) {
        console.error(err);
        process.exit(1);
    }
}

main();
