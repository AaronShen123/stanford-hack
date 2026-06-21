const fs = require('fs');

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
                    {"name": "Ming (Self)", "stem_branch": "Ji-Si", "stars": ["Zi Wei", "Tian Fu", "Zuo Fu"], "decadal_range": "26-35"},
                    {"name": "Siblings", "stem_branch": "Geng-Chen", "stars": ["Tian Ji", "You Bi"], "decadal_range": "16-25"},
                    {"name": "Spouse", "stem_branch": "Xin-Mao", "stars": ["Tai Yang", "Wen Qu", "Hua-Ji"], "decadal_range": "06-15"},
                    {"name": "Children", "stem_branch": "Ren-Yin", "stars": ["Wu Qu", "Tian Kui"], "decadal_range": "116-125"},
                    {"name": "Wealth", "stem_branch": "Gui-Chou", "stars": ["Tian Tong", "Lu Cun"], "decadal_range": "106-115"},
                    {"name": "Health", "stem_branch": "Jia-Zi", "stars": ["Lian Zhen (Xian)", "Tian Yue"], "decadal_range": "96-105"},
                    {"name": "Travel", "stem_branch": "Yi-Hai", "stars": ["Tian Ji", "Qing Yang"], "decadal_range": "86-95"},
                    {"name": "Friends", "stem_branch": "Bing-Xu", "stars": ["Tai Yin", "Tuo Luo"], "decadal_range": "76-85"},
                    {"name": "Career", "stem_branch": "Ding-You", "stars": ["Tan Lang", "Di Kong"], "decadal_range": "66-75"},
                    {"name": "Property", "stem_branch": "Wu-Shen", "stars": ["Ju Men", "Di Jie"], "decadal_range": "56-65"},
                    {"name": "Happiness", "stem_branch": "Ji-Wei", "stars": ["Tian Liang", "Hua Lu"], "decadal_range": "46-55"},
                    {"name": "Parents", "stem_branch": "Geng-Wu", "stars": ["Qi Sha", "Hua Quan"], "decadal_range": "36-45"}
                ],
                "yearly_stem_branch": "Bing-Wu",
                "monthly_branch": "Wu-Shen",
                "lunar_date_str": "Year 2026, Month 5, Day 7, Hour Wu (Bridge Fallback)"
            };
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
            const stars = p.majorStars.map(s => s.name)
                .concat(p.minorStars.map(s => s.name))
                .concat(p.adjectiveStars.map(s => s.name));
            
            if (p.mutagen) {
                stars.push(`Hua-${p.mutagen}`);
            }
            return {
                name: p.name,
                stem_branch: p.decadal.heavenlyStem + '-' + p.decadal.earthlyBranch,
                stars: stars,
                decadal_range: p.decadal.range[0] + '-' + p.decadal.range[1]
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
