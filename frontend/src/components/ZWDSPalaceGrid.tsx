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
    
    // Parse stars
    const mainStars: { name: string; status: string }[] = [];
    let auxiliaryCount = 0;
    let hasHuaJi = false;
    let hasHuaLu = false;

    const majorStarNames = [
      "Zi Wei", "Tian Fu", "Wu Qu", "Tian Tong", "Lian Zhen", "Tian Ji", 
      "Tai Yang", "Tai Yin", "Tan Lang", "Ju Men", "Tian Liang", "Qi Sha", 
      "Po Jun", "Tian Xiang"
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
      
      const isMajor = majorStarNames.some(keyword => name.toLowerCase().includes(keyword.toLowerCase()));
      if (isMajor) {
        mainStars.push({ name, status });
      } else {
        auxiliaryCount++;
      }
    });

    const branchToAgeRange: Record<string, string> = {
      "Si": "4–13",
      "Wu": "14–23",
      "Wei": "24–33",
      "Shen": "34–43",
      "You": "44–53",
      "Xu": "54–63",
      "Hai": "64–73",
      "Zi": "74–83",
      "Chou": "84–93",
      "Yin": "94–103",
      "Mao": "104–113",
      "Chen": "114–123"
    };

    const decadalAgeRange = branchToAgeRange[branch] || palace.decadal_range || "00-00";

    return {
      palace,
      coords,
      hasHuaJi,
      hasHuaLu,
      branch,
      mainStars,
      auxiliaryCount,
      decadalAgeRange
    };
  });

  return (
    <div className="w-full flex flex-col items-center">
      <h2 className="text-xs font-bold text-stone-400 uppercase tracking-widest mb-4 flex items-center gap-2 self-start pl-1 shrink-0">
        <Shield className="text-stone-550 w-4 h-4" />
        Chinese Zi Wei Dou Shu (ZWDS) Ming Pan
      </h2>

      {/* 4x4 Grid layout with custom border mappings */}
      <div className="grid grid-cols-4 grid-rows-4 gap-2 h-full aspect-square max-w-[480px] mx-auto w-full">
        
        {/* Render Palaces around the border */}
        {gridCells.map(({ palace, coords, hasHuaJi, hasHuaLu, branch, mainStars, auxiliaryCount, decadalAgeRange }, idx) => {
          let cardBgClasses = "bg-stone-50/40 border-stone-200/60 hover:border-stone-400";
          if (hasHuaJi) cardBgClasses = "bg-rose-50/30 border-rose-200/60 hover:border-rose-300 shadow-sm shadow-rose-50";
          if (hasHuaLu) cardBgClasses = "bg-emerald-50/30 border-emerald-200/60 hover:border-emerald-300 shadow-sm shadow-emerald-50";

          const palaceName = palace.name.replace(" (Self)", "");
          const branchLabel = branch;

          return (
            <div
              key={idx}
              style={{
                gridRowStart: coords.r,
                gridColumnStart: coords.c,
              }}
              className={`relative flex flex-col justify-between p-3 min-h-[110px] rounded-lg transition-colors select-none ${cardBgClasses}`}
            >
              {/* Top Header Row of the Cell */}
              <div className="flex justify-between items-start w-full">
                <div>
                  <span className="text-xs font-bold text-stone-400 uppercase tracking-wider">{palaceName}</span>
                  {/* Main Stars Column Stacking */}
                  <div className="mt-1 flex flex-col gap-0.5">
                    {mainStars.map((star, sIdx) => {
                      let starColorClass = "text-stone-800";
                      if (star.status === 'Xian') {
                        starColorClass = "text-rose-600 font-bold";
                      } else if (star.status === 'Miao') {
                        starColorClass = "text-amber-600 font-bold";
                      }
                      return (
                        <span key={sIdx} className={`text-xs font-semibold ${starColorClass}`}>
                          {star.name}
                          {star.status && (
                            <span className="text-[10px] font-normal opacity-70 ml-0.5">
                              ({star.status})
                            </span>
                          )}
                        </span>
                      );
                    })}
                  </div>
                </div>
                {/* Top Right: Catalyst Badge or Fixed Branch Tag */}
                <div className="flex flex-col items-end gap-1 shrink-0">
                  <span className="text-[10px] font-bold px-1 bg-stone-200/60 text-stone-600 rounded font-mono">{branchLabel}</span>
                  {hasHuaJi && (
                    <span className="px-1.5 py-0.5 bg-rose-100 text-rose-700 text-[9px] font-extrabold rounded border border-rose-200 uppercase tracking-tighter">
                      JI
                    </span>
                  )}
                  {hasHuaLu && (
                    <span className="px-1.5 py-0.5 bg-emerald-100 text-emerald-700 text-[9px] font-extrabold rounded border border-emerald-200 uppercase tracking-tighter">
                      LU
                    </span>
                  )}
                </div>
              </div>

              {/* Bottom Metadata Row of the Cell */}
              <div className="flex justify-between items-end w-full border-t border-stone-100/80 pt-1 mt-1">
                <span className="text-[10px] font-mono text-stone-400 font-medium">{decadalAgeRange || "00-00"}</span>
                <span className="text-[9px] text-stone-400 italic font-medium">{auxiliaryCount} Aux</span>
              </div>
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
            <div className="text-[7.5px] text-stone-450 truncate mt-0.5">
              {matrix.lunar_date_str}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
