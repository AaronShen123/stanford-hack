import type { ZWDSMatrix } from "../types";
import { Shield } from "lucide-react";

interface ZWDSPalaceGridProps {
  matrix: ZWDSMatrix;
  birthDate: string;
  birthTime: string;
  gender: string;
  locationName: string;
  targetVector: string;
}

interface PalaceDataPayload {
  palaceName: string;
  branchLabel: string;
  decadalAgeRange: string;
  mainStars?: { name: string; status?: string; is_borrowed?: boolean; mutagen?: string }[]; 
  minorStars?: string[];   
  changshengStage?: string; 
  pillarGods?: string[];   
  oneYearLuck?: string;    
  hasHuaLu?: boolean;
  hasHuaJi?: boolean;
  intensity?: number;
}

const starTranslations: Record<string, string> = {
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

const branchPalaceDetails: Record<string, { changshengStage: string; pillarGods: string[] }> = {
  "Si": { changshengStage: "Birth", pillarGods: ["Stern", "Beginning"] },
  "Wu": { changshengStage: "Bath", pillarGods: ["Stern", "Beginning"] },
  "Wei": { changshengStage: "Youth", pillarGods: ["Officer", "Academic"] },
  "Shen": { changshengStage: "Arrive", pillarGods: ["Officer", "Academic"] },
  "You": { changshengStage: "Imperial", pillarGods: ["General", "Cavalry"] },
  "Xu": { changshengStage: "Decay", pillarGods: ["General", "Cavalry"] },
  "Hai": { changshengStage: "Sickness", pillarGods: ["Scribe", "Doctor"] },
  "Zi": { changshengStage: "Death", pillarGods: ["Scribe", "Doctor"] },
  "Chou": { changshengStage: "Grave", pillarGods: ["Blacksmith", "Mason"] },
  "Yin": { changshengStage: "Cut", pillarGods: ["Blacksmith", "Mason"] },
  "Mao": { changshengStage: "Tomb", pillarGods: ["Farmer", "Weaver"] },
  "Chen": { changshengStage: "Exhaust", pillarGods: ["Farmer", "Weaver"] }
};

const getEffectiveBrightness = (status: string | undefined, isBorrowed: boolean | undefined): string => {
  if (!status) return "";
  if (isBorrowed) {
    if (status === "Radiant" || status === "Bright" || status === "Shiny") {
      return "Neutral";
    }
  }
  return status;
};

const DynamicPalaceCell = ({ data }: { data: PalaceDataPayload }) => {
  if (!data) return <div className="bg-white border border-stone-200 rounded-xl min-h-[175px]" />;

  const cellOpacity = data.intensity !== undefined ? data.intensity : 1.0;

  return (
    <div 
      style={{ opacity: cellOpacity }}
      className="relative flex flex-col justify-between p-2.5 h-full min-h-[175px] bg-white border border-stone-200 rounded-xl hover:border-stone-950 transition-all duration-150 shadow-sm"
    >
      
      {/* Row 1: Palace Header & Fixed Coordinate Tag */}
      <div className="flex justify-between items-start w-full border-b border-stone-100 pb-1">
        <span className="text-[11px] font-black tracking-wider text-stone-900 uppercase font-sans">
          {data.palaceName}
        </span>
        <span className="text-[10px] font-mono font-bold bg-stone-100 text-stone-500 px-1 rounded">
          {data.branchLabel}
        </span>
      </div>

      {/* Row 2: Main Stars & Dynamic Radiance Tokens */}
      <div className="mt-1.5 flex flex-col gap-0.5">
        {data.mainStars && data.mainStars.length > 0 ? (
          data.mainStars.map((star, idx) => {
            const effectiveStatus = getEffectiveBrightness(star.status, star.is_borrowed);
            return (
              <div key={idx} className={`flex items-baseline gap-1 text-xs font-extrabold text-stone-900 tracking-tight ${star.is_borrowed ? "opacity-50" : ""}`}>
                <span className={star.is_borrowed ? "text-stone-400 font-medium italic" : ""}>
                  {star.name}
                  {star.is_borrowed && <span className="text-[9px] font-normal text-stone-400 font-sans ml-1">(Borrowed)</span>}
                </span>
                {effectiveStatus && (
                  <span className={`text-[9px] font-mono font-bold px-0.5 rounded ${
                    star.is_borrowed
                      ? 'text-stone-400 bg-stone-50/50'
                      : effectiveStatus === 'Radiant' || effectiveStatus === 'Bright' || effectiveStatus === 'Shiny'
                      ? 'text-amber-600 bg-amber-50' 
                      : effectiveStatus === 'Xian' || effectiveStatus === 'Dark' || effectiveStatus === 'Ruinous' || effectiveStatus === 'Exhaust'
                      ? 'text-rose-600 bg-rose-50'
                      : 'text-stone-400 bg-stone-50'
                  }`}>
                    ({effectiveStatus})
                  </span>
                )}
              </div>
            );
          })
        ) : (
          <span className="text-xs text-stone-300 italic">No Major Stars</span>
        )}
      </div>

      {/* Row 3: Minor Stars & Astral Badges Matrix */}
      {data.minorStars && data.minorStars.length > 0 && (
        <div className="mt-1.5 flex flex-wrap gap-x-1 gap-y-0.5 text-[9px] font-sans text-stone-500 leading-tight">
          {data.minorStars.map((minor, idx) => (
            <span key={idx} className="bg-stone-50/80 px-1 py-0.5 rounded border border-stone-100">
              {minor}
            </span>
          ))}
        </div>
      )}

      {/* Row 4: Chronological Cosmic Energy Stages */}
      <div className="mt-2 pt-1 border-t border-stone-100/60 grid grid-cols-2 gap-1 text-[9px] font-mono text-stone-400">
        <div>
          Stage: <span className="text-stone-700 font-bold">{data.changshengStage || "N/A"}</span>
        </div>
        <div className="text-right truncate text-stone-500">
          {data.pillarGods && data.pillarGods.length > 0 ? data.pillarGods.join(" · ") : "None"}
        </div>
      </div>

      {/* Row 5: Decadal Bounds & 1-Year Luck Horizon Streams */}
      <div className="flex flex-col gap-0.5 mt-2 pt-1 border-t border-stone-100 text-[9px] font-mono">
        <div className="text-stone-500 font-bold">10Y Luck: {data.decadalAgeRange || "00-00"}</div>
        <div className="text-stone-400 truncate">
          1Y Luck: {data.oneYearLuck || "None"}
        </div>
      </div>

      {/* Absolute Transformation Catalyst Layers */}
      <div className="absolute bottom-11 right-2.5 flex gap-0.5">
        {data.hasHuaLu && <span className="px-1 text-[8px] font-black bg-emerald-50 text-emerald-700 border border-emerald-200 rounded shadow-sm">LU</span>}
        {data.hasHuaJi && <span className="px-1 text-[8px] font-black bg-rose-50 text-rose-700 border border-rose-200 rounded shadow-sm">JI</span>}
      </div>

    </div>
  );
};

export default function ZWDSPalaceGrid({
  matrix,
  birthDate,
  birthTime,
  gender,
  locationName,
  targetVector
}: ZWDSPalaceGridProps) {
  // Mapping traditional Earthly Branches to grid row and column coordinates in a 4x4 container.
  // yin=bottom-left, si=top-left, shen=top-right, hai=bottom-right
  const branchToGrid: Record<string, { r: number; c: number }> = {
    "Yin": { r: 4, c: 1 },
    "Mao": { r: 3, c: 1 },
    "Chen": { r: 2, c: 1 },
    "Si": { r: 1, c: 1 },
    "Wu": { r: 1, c: 2 },
    "Wei": { r: 1, c: 3 },
    "Shen": { r: 1, c: 4 },
    "You": { r: 2, c: 4 },
    "Xu": { r: 3, c: 4 },
    "Hai": { r: 4, c: 4 },
    "Zi": { r: 4, c: 3 },
    "Chou": { r: 4, c: 2 }
  };

  // Maps the palaces to their correct coordinates
  const gridCells = matrix.palaces.map((palace, idx) => {
    // Parse earthly branch from stem_branch (e.g., "Ji-Si" -> "Si")
    const branch = palace.stem_branch.split("-")[1] || "";
    const coords = branchToGrid[branch] || { r: Math.floor(idx / 4) + 1, c: (idx % 4) + 1 };
    
    // Parse stars from backend or fallback to parsing from stars array
    const mainStarsFromBackend = palace.main_stars?.map(s => ({ name: s.name, status: s.status || "", is_borrowed: s.is_borrowed }));
    const minorStarsFromBackend = palace.minor_stars;
    const changshengFromBackend = palace.changsheng;
    const pillarGodsFromBackend = palace.pillar_gods;
    const oneYearLuckFromBackend = palace.one_year_luck;

    let mainStars: { name: string; status: string; is_borrowed?: boolean }[] = [];
    let minorStars: string[] = [];
    let changshengStage = "";
    let pillarGods: string[] = [];
    let oneYearLuck = "";
    let hasHuaJi = false;
    let hasHuaLu = false;

    if (mainStarsFromBackend && mainStarsFromBackend.length > 0) {
      mainStars = mainStarsFromBackend;
      minorStars = minorStarsFromBackend || [];
      changshengStage = changshengFromBackend || "";
      pillarGods = pillarGodsFromBackend || [];
      oneYearLuck = oneYearLuckFromBackend || "";
      hasHuaJi = (palace.stars || []).some(s => s.toLowerCase().includes("hua-ji") || s.toLowerCase().includes("hua ji") || s.toLowerCase().includes("化忌")) || minorStars.includes("Hua Ji") || minorStars.includes("Hua-Ji");
      hasHuaLu = (palace.stars || []).some(s => s.toLowerCase().includes("hua-lu") || s.toLowerCase().includes("hua lu") || s.toLowerCase().includes("化祿") || s.toLowerCase().includes("化禄")) || minorStars.includes("Hua Lu") || minorStars.includes("Hua-Lu");
    } else {
      const majorStarNames = [
        "Zi Wei", "Tian Fu", "Wu Qu", "Tian Tong", "Lian Zhen", "Tian Ji", 
        "Tai Yang", "Tai Yin", "Tan Lang", "Ju Men", "Tian Liang", "Qi Sha", 
        "Po Jun", "Tian Xiang", "Emperor", "Heavenly Mansion", "Finance",
        "Mascot", "Justice", "Advisor", "Sun", "Moon", "Flirt", "Advocate",
        "Blessing", "Marshal", "Pioneer", "Minister"
      ];

      (palace.stars || []).forEach(starStr => {
        const lower = starStr.toLowerCase();
        if (lower.includes("hua-ji") || lower.includes("hua ji") || lower.includes("化忌")) {
          hasHuaJi = true;
          return;
        }
        if (lower.includes("hua-lu") || lower.includes("hua lu") || lower.includes("化祿") || lower.includes("化禄")) {
          hasHuaLu = true;
          return;
        }
        
        const match = starStr.match(/^([^(]+)(?:\(([^)]+)\))?/);
        let name = starStr.trim();
        let status = "";
        if (match) {
          name = match[1].trim();
          status = match[2] ? match[2].trim() : "";
        }
        
        const translatedName = starTranslations[name] || name;
        let mappedStatus = "";
        if (status) {
          if (status.toLowerCase() === "miao" || status.toLowerCase() === "radiant") {
            mappedStatus = "Radiant";
          } else if (status.toLowerCase() === "xian" || status.toLowerCase() === "exhaust") {
            mappedStatus = "Exhaust";
          } else {
            mappedStatus = status;
          }
        }

        const isMajor = majorStarNames.some(keyword => name.toLowerCase().includes(keyword.toLowerCase()));
        if (isMajor) {
          mainStars.push({ name: translatedName, status: mappedStatus });
        } else {
          minorStars.push(translatedName);
        }
      });

      const staticDetails = branchPalaceDetails[branch] || { changshengStage: "", pillarGods: [] };
      changshengStage = staticDetails.changshengStage;
      pillarGods = staticDetails.pillarGods;

      const branchToYear: Record<string, string> = {
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
      oneYearLuck = branchToYear[branch] || "";
    }

    return {
      palace,
      coords,
      hasHuaJi,
      hasHuaLu,
      branch,
      mainStars,
      changshengStage,
      pillarGods,
      oneYearLuck,
      minorStars,
      intensity: palace.intensity !== undefined ? palace.intensity : 1.0
    };
  });

  return (
    <div className="w-full flex flex-col items-center">
      <h2 className="text-xs font-bold text-stone-400 uppercase tracking-widest mb-4 flex items-center gap-2 self-start pl-1 shrink-0">
        <Shield className="text-stone-550 w-4 h-4" />
        Chinese Zi Wei Dou Shu (ZWDS) Ming Pan
      </h2>

      {/* 4x4 Grid layout with custom border mappings */}
      <div className="grid grid-cols-4 grid-rows-4 gap-2 w-full max-w-[720px] mx-auto">
        
        {/* Render Palaces around the border */}
        {gridCells.map(({ palace, coords, hasHuaJi, hasHuaLu, branch, mainStars, changshengStage, pillarGods, oneYearLuck, minorStars, intensity }, idx) => {
          
          const cellData: PalaceDataPayload = {
            palaceName: palace.name,
            branchLabel: branch,
            decadalAgeRange: palace.decadal_range || "00-00",
            mainStars: mainStars,
            minorStars: minorStars,
            changshengStage: changshengStage,
            pillarGods: pillarGods,
            oneYearLuck: oneYearLuck,
            hasHuaLu: hasHuaLu,
            hasHuaJi: hasHuaJi,
            intensity: intensity
          };

          return (
            <div
              key={idx}
              style={{
                gridRowStart: coords.r,
                gridColumnStart: coords.c,
              }}
              className="h-full"
            >
              <DynamicPalaceCell data={cellData} />
            </div>
          );
        })}

        {/* Central hollow 2x2 cell block for Global Metadata & User Profile */}
        <div className="col-span-2 row-span-2 col-start-2 row-start-2 bg-stone-50 border border-stone-200 rounded-xl p-3 flex flex-col justify-between text-left select-none shadow-sm overflow-hidden">
          <div className="border-b border-stone-200 pb-1.5">
            <span className="text-[9px] uppercase tracking-widest font-black text-stone-400 block mb-0.5">
              Native Profile
            </span>
            <h3 className="text-[11px] font-bold text-stone-900 truncate">
              {locationName}
            </h3>
          </div>

          <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 my-1.5 text-[9px] leading-tight">
            <div>
              <span className="text-[8px] text-stone-400 block uppercase font-medium">Birth Date</span>
              <span className="text-stone-800 font-semibold">{birthDate}</span>
            </div>
            <div>
              <span className="text-[8px] text-stone-400 block uppercase font-medium">Birth Time</span>
              <span className="text-stone-800 font-semibold">{birthTime}</span>
            </div>
            <div>
              <span className="text-[8px] text-stone-400 block uppercase font-medium">Gender</span>
              <span className="text-stone-800 font-semibold">
                {gender === "M" ? "Male (Yang)" : "Female (Yin)"}
              </span>
            </div>
            <div>
              <span className="text-[8px] text-stone-400 block uppercase font-medium">Vector</span>
              <span className="text-stone-800 font-semibold uppercase tracking-tight truncate">
                {targetVector.replace("_", " ")}
              </span>
            </div>
          </div>

          <div className="border-t border-stone-200 pt-1.5 text-[8.5px] text-stone-500 leading-normal flex flex-col gap-0.5">
            <div>
              <span className="font-bold text-stone-600">Year Stem/Branch: </span>
              <span className="text-stone-800 font-semibold">{matrix.yearly_stem_branch}</span>
            </div>
            <div>
              <span className="font-bold text-stone-600">Month Branch: </span>
              <span className="text-stone-800 font-semibold">{matrix.monthly_branch}</span>
            </div>
            {matrix.life_master && (
              <div>
                <span className="font-bold text-stone-600">Life Master: </span>
                <span className="text-stone-800 font-semibold">{matrix.life_master}</span>
              </div>
            )}
            {matrix.body_master && (
              <div>
                <span className="font-bold text-stone-600">Body Master: </span>
                <span className="text-stone-800 font-semibold">{matrix.body_master}</span>
              </div>
            )}
            <div className="text-[7.5px] text-stone-450 truncate mt-0.5">
              {matrix.lunar_date_str}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
