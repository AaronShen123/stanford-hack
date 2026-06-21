import { useState } from "react";
import type { AstrologyRequest, AstrologyResponse, AstrologyCompletionResponse } from "./types";
import { fetchAstrologyCompletion, fetchAstrologySynthesis } from "./utils/api";
import { generateStorageKey } from "./utils/storage";
import InputsModule from "./components/InputsModule";
import WesternChart from "./components/WesternChart";
import ZWDSPalaceGrid from "./components/ZWDSPalaceGrid";
import VectorDashboard from "./components/VectorDashboard";
import ClientChat from "./components/ClientChat";
import SafetyBanners from "./components/SafetyBanners";
import { Compass, Database, ShieldAlert, AlertCircle } from "lucide-react";

// Offline hardcoded fallback data for expo demo safety (protects against CalHacks Wi-Fi dropouts)
const MOCK_GOD_MODE_RESPONSE: Record<string, any> = {
  wealth: {
    synthesis: {
      birth_time_metrics: {
        local_datetime: "2000-10-16T12:00:00",
        utc_datetime: "2000-10-16T20:00:00",
        lmt_datetime: "2000-10-16T11:50:19.344000",
        tlt_datetime: "2000-10-16T11:54:01.460902",
        timezone_offset: -8.0,
        jd_ut: 2451834.3333333335,
        jd_et: 2451834.3339942857,
        eot_seconds: 222.1169018935825,
        branch_boundary_anomaly: false
      },
      western_matrix: {
        sun_degree: 54.71750461549791,
        moon_degree: 301.2933385213661,
        ascendant_degree: 148.25070762581666,
        midheaven_degree: 53.25780832849757,
        saturn_degree: 295.2437220033629,
        mars_degree: 348.58140369703324,
        neptune_degree: 284.34797286640253,
        pluto_degree: 226.15820593603982,
        houses: {
          1: 148.25070762581666,
          2: 171.8707066717837,
          3: 200.35080903198048,
          4: 233.25780832849756,
          5: 267.6176599951293,
          6: 299.74312392941414,
          7: 328.25070762581663,
          8: 351.8707066717837,
          9: 20.350809031980475,
          10: 53.25780832849757,
          11: 87.61765999512933,
          12: 119.74312392941414
        }
      },
      zwds_matrix: {
        palaces: [
          {
            name: "Life Palace (命宮)",
            stem_branch: "Ji-Si",
            stars: ["Zi Wei", "Tian Fu", "Zuo Fu"],
            decadal_range: "4–13",
            main_stars: [{ name: "Emperor", status: "Radiant" }, { name: "Heavenly Mansion", status: "Radiant" }],
            minor_stars: ["Intellect", "Tian Kong", "Gu Chen", "Tian Wu"],
            changsheng: "Birth",
            pillar_gods: ["Stern", "Beginning"],
            one_year_luck: "36, 48, 60"
          },
          {
            name: "Parents Palace (父母)",
            stem_branch: "Geng-Wu",
            stars: ["Qi Sha", "Hua Quan"],
            decadal_range: "14–23",
            main_stars: [{ name: "Marshal", status: "Radiant" }],
            minor_stars: ["Hua Quan"],
            changsheng: "Bath",
            pillar_gods: ["Stern", "Beginning"],
            one_year_luck: "37, 49, 61"
          },
          {
            name: "Happy Palace (福德)",
            stem_branch: "Ji-Wei",
            stars: ["Tian Liang", "Hua Lu"],
            decadal_range: "24–33",
            main_stars: [{ name: "Blessing", status: "Radiant" }],
            minor_stars: ["Hua Lu"],
            changsheng: "Youth",
            pillar_gods: ["Officer", "Academic"],
            one_year_luck: "38, 50, 62"
          },
          {
            name: "Property Palace (田宅)",
            stem_branch: "Wu-Shen",
            stars: ["Ju Men", "Di Jie"],
            decadal_range: "34–43",
            main_stars: [{ name: "Advocate", status: "Exhaust" }],
            minor_stars: ["Exhaust"],
            changsheng: "Arrive",
            pillar_gods: ["Officer", "Academic"],
            one_year_luck: "39, 51, 63"
          },
          {
            name: "Career Palace (官祿)",
            stem_branch: "Ding-You",
            stars: ["Tan Lang", "Di Kong"],
            decadal_range: "44–53",
            main_stars: [{ name: "Flirt", status: "Radiant" }],
            minor_stars: ["Void"],
            changsheng: "Imperial",
            pillar_gods: ["General", "Cavalry"],
            one_year_luck: "40, 52, 64"
          },
          {
            name: "Friends Palace (交友)",
            stem_branch: "Bing-Xu",
            stars: ["Tai Yin", "Tuo Luo"],
            decadal_range: "54–63",
            main_stars: [{ name: "Moon", status: "Exhaust" }],
            minor_stars: ["Obstacle"],
            changsheng: "Decay",
            pillar_gods: ["General", "Cavalry"],
            one_year_luck: "41, 53, 65"
          },
          {
            name: "Travel Palace (遷移)",
            stem_branch: "Yi-Hai",
            stars: ["Tian Ji", "Qing Yang"],
            decadal_range: "64–73",
            main_stars: [{ name: "Advisor", status: "Radiant" }],
            minor_stars: ["Sternness"],
            changsheng: "Sickness",
            pillar_gods: ["Scribe", "Doctor"],
            one_year_luck: "42, 54, 66"
          },
          {
            name: "Health Palace (疾厄)",
            stem_branch: "Jia-Zi",
            stars: ["Lian Zhen (Xian)", "Tian Yue"],
            decadal_range: "74–83",
            main_stars: [{ name: "Justice", status: "Exhaust" }],
            minor_stars: ["Grace"],
            changsheng: "Death",
            pillar_gods: ["Scribe", "Doctor"],
            one_year_luck: "31, 43, 55"
          },
          {
            name: "Wealth Palace (財帛)",
            stem_branch: "Gui-Chou",
            stars: ["Tian Tong", "Lu Cun"],
            decadal_range: "84–93",
            main_stars: [{ name: "Mascot", status: "Radiant" }],
            minor_stars: ["Wealth Star"],
            changsheng: "Grave",
            pillar_gods: ["Blacksmith", "Mason"],
            one_year_luck: "32, 44, 56"
          },
          {
            name: "Child Palace (子女)",
            stem_branch: "Ren-Yin",
            stars: ["Wu Qu", "Tian Kui"],
            decadal_range: "94–103",
            main_stars: [{ name: "Finance", status: "Radiant" }],
            minor_stars: ["Status"],
            changsheng: "Cut",
            pillar_gods: ["Blacksmith", "Mason"],
            one_year_luck: "33, 45, 57"
          },
          {
            name: "Marriage Palace (夫妻)",
            stem_branch: "Xin-Mao",
            stars: ["Tai Yang", "Wen Qu", "Hua-Ji"],
            decadal_range: "104–113",
            main_stars: [{ name: "Sun", status: "Exhaust" }],
            minor_stars: ["Arts", "Hua Ji"],
            changsheng: "Tomb",
            pillar_gods: ["Farmer", "Weaver"],
            one_year_luck: "34, 46, 58"
          },
          {
            name: "Siblings Palace (兄弟)",
            stem_branch: "Geng-Chen",
            stars: ["Tian Ji", "You Bi"],
            decadal_range: "114–123",
            main_stars: [{ name: "Advisor", status: "Radiant" }],
            minor_stars: ["Right Assist"],
            changsheng: "Exhaust",
            pillar_gods: ["Farmer", "Weaver"],
            one_year_luck: "35, 47, 59"
          }
        ],
        yearly_stem_branch: "Geng-Chen",
        monthly_branch: "Bing-Xu",
        lunar_date_str: "Year Geng-Chen (2000), Month 9, Day 19 (Local Bypass)"
      },
      synthesis_flags: {
        friction_index: 1.34,
        friction_points: [
          "Moon opposition Saturn (orb 2.14°)",
          "Ascendant square Midheaven (orb 3.50°)"
        ],
        aspects: [
          { planet1: "Sun", planet2: "Moon", aspect_type: "trine", degree_difference: 113.42, orb: 6.57 },
          { planet1: "Sun", planet2: "Ascendant", aspect_type: "square", degree_difference: 93.53, orb: 3.53 },
          { planet1: "Sun", planet2: "Midheaven", aspect_type: "conjunction", degree_difference: 1.45, orb: 1.45 },
          { planet1: "Sun", planet2: "Saturn", aspect_type: "trine", degree_difference: 119.47, orb: 0.52 },
          { planet1: "Moon", planet2: "Saturn", aspect_type: "conjunction", degree_difference: 6.04, orb: 6.04 },
          { planet1: "Ascendant", planet2: "Midheaven", aspect_type: "square", degree_difference: 94.99, orb: 4.99 },
          { planet1: "Midheaven", planet2: "Saturn", aspect_type: "trine", degree_difference: 118.01, orb: 1.98 },
          { planet1: "Midheaven", planet2: "Pluto", aspect_type: "opposition", degree_difference: 172.90, orb: 7.09 }
        ],
        synthesis_notes: ["God-Mode Demo: Relational alignment & material flow parsed entirely offline."],
        dual_matrix_indicator: false,
        critical_bottleneck: false,
        interpersonal_risk: false,
        systemic_exhaustion: false
      }
    },
    compiled_prompt: "God-Mode Offline Synthesis",
    reading: `# [God-Mode Bypass Active] Synthesis Reading

**Native Profile:** 2000-10-16 | Sun Libra | Geng-Chen Year | Current Age: 25
**Demo Status:** Offline Simulation Mode (CalHacks Wi-Fi Dropouts Insulated)

---

## 1. Primary Alignment Dynamics

- **Deterministic Axis:** **Ascendant square Midheaven** cross-mapped with the **Career Palace (You)**. Professional focus is centered on high-scale analytical architectures (Data Science and engineering trajectory).
- **ZWDS Prosperity Anchor:** **Lu Cun (禄存)** in the **Wealth Palace (Chou)** guarantees a resilient baseline flow.

---

## 2. Potential Vulnerabilities & Frictions (Cross-System Resonance)

| Palace / Axis | Aspect / Catalyst | Core Impact | Risk Rating |
|---|---|---|---|
| **Career Palace (官祿) [You]** | Tan Lang + Di Kong | speculative drain | Moderate |
| **Wealth Palace (財帛) [Chou]** | Tian Tong + Lu Cun | accumulation bottleneck | Low |
| **Spouse Palace (夫妻) [Mao]** | Tai Yang + Hua-Ji | relational friction | High |

---

## 3. Cross-System Translation Framework (The Dual-Matrix Resonance)

The synthesis model resolves the dual-matrix translation by mapping Western aspect vectors as operational modifiers over ZWDS palace structures:
- The **Ascendant-Midheaven square** acts as a structural catalyst, translating personal execution stress into Career Palace (You) speculation blocks.
- The **Spouse Palace (Mao) Hua-Ji** resonance maps to relational boundaries, indicating that personal/professional tension points should be managed through explicit, decoupled boundaries.

---

## 4. Recommended Actions

1. Align Data Science and engineering trajectory with institutional, equity-based growth channels.
2. Avoid short-term high-leverage speculation (neutralizing the Tan Lang + Di Kong void block in You).
3. Preemptively run conflict-resolution cycles to safeguard the Spouse Palace (Mao) Hua-Ji risk vector.
`
  }
};

export default function App() {
  const [activeRequest, setActiveRequest] = useState<AstrologyRequest | null>(null);
  const [synthesis, setSynthesis] = useState<AstrologyResponse | null>(null);
  const [completion, setCompletion] = useState<AstrologyCompletionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLLMLoading, setIsLLMLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [storageKey, setStorageKey] = useState("");
  
  // God-Mode, Preflight Deflection & Active tab
  const [isGodMode, setIsGodMode] = useState(false);
  const [preflightDeflection, setPreflightDeflection] = useState(false);
  const [activeTab, setActiveTab] = useState<"zwds" | "western">("zwds");
  const [locationName, setLocationName] = useState("San Francisco, CA");

  const executeAstrologySynthesis = async (payload: AstrologyRequest, locName?: string) => {
    setIsLoading(true);
    setIsLLMLoading(true);
    setError(null);
    setPreflightDeflection(false);
    setCompletion(null); // Clear previous reading to trigger streaming state

    if (locName) {
      setLocationName(locName);
    } else {
      setLocationName(`${payload.latitude.toFixed(4)}°N, ${payload.longitude.toFixed(4)}°E`);
    }

    // Trigger pre-flight deflection warning if coordinates are extreme
    if (Math.abs(payload.latitude) > 80 || Math.abs(payload.longitude) > 170) {
      setPreflightDeflection(true);
    }

    // GOD-MODE: Skip API requests if enabled, simulate local delay and load pre-calculated data
    if (isGodMode) {
      await new Promise(resolve => setTimeout(resolve, 600));
      const response = MOCK_GOD_MODE_RESPONSE[payload.target_vector] || MOCK_GOD_MODE_RESPONSE["wealth"];
      setActiveRequest(payload);
      setSynthesis(response.synthesis);
      setCompletion(response);
      setStorageKey(generateStorageKey(payload));
      setIsLoading(false);
      setIsLLMLoading(false);
      return;
    }

    // Step 1: Ingest deterministic calculations (extremely fast, <20ms)
    try {
      const mathResponse = await fetchAstrologySynthesis(payload);
      setSynthesis(mathResponse);
      setActiveRequest(payload);
      setStorageKey(generateStorageKey(payload));
      
      // Stop the overlay spinner since visual charts are ready to render
      setIsLoading(false);
    } catch (err: any) {
      console.error("Mathematical API Error:", err);
      setError(err.message || "Failed to calculate deterministic astrological matrices.");
      setIsLoading(false);
      setIsLLMLoading(false);
      return;
    }

    // Step 2: Background call to compile prompt and fetch LLM Reading (takes 5-15s)
    try {
      const llmResponse = await fetchAstrologyCompletion(payload);
      setCompletion(llmResponse);
    } catch (err: any) {
      console.error("LLM Generation API Error:", err);
      setError(err.message || "Failed to fetch structured AI reading synthesis from Claude.");
    } finally {
      setIsLLMLoading(false);
    }
  };

  // View 1: Input Gate (displayed only when chart is not generated yet)
  if (!synthesis) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center p-6 font-sans">
        <div className="max-w-md w-full select-none animate-fadeIn">
          {/* Logo Title */}
          <div 
            onClick={(e) => {
              if (e.detail === 3) {
                setIsGodMode(prev => !prev);
              }
            }}
            className="text-center mb-8 cursor-pointer active:scale-[0.99] transition"
            title="Triple-click to toggle offline God-Mode demo"
          >
            <div className="w-12 h-12 rounded-2xl bg-stone-900 flex items-center justify-center shadow-md mx-auto mb-4">
              <Compass className="w-6 h-6 text-stone-50 animate-spin-slow" />
            </div>
            <div className="flex items-center justify-center gap-2">
              <h1 className="text-2xl font-black text-stone-900 tracking-tight">
                Astro-Synthesis Matrix
              </h1>
              {isGodMode && (
                <span className="text-[9px] bg-amber-100 border border-amber-300 text-amber-800 px-1.5 py-0.5 rounded font-extrabold tracking-wider leading-none animate-pulse">
                  ⚡ GOD-MODE
                </span>
              )}
            </div>
            <p className="text-[10px] text-stone-500 tracking-widest uppercase font-semibold mt-1.5">
              Hybrid Ephemeris & ZWDS Downstream Inference Pipeline
            </p>
          </div>

          <InputsModule
            onSubmit={executeAstrologySynthesis}
            isLoading={isLoading}
          />
        </div>
      </div>
    );
  }

  // View 2: Dashboard (displayed once synthesis is computed)
  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 p-6 md:p-8 flex flex-col font-sans">
      
      {/* Page Header */}
      <header className="max-w-7xl w-full mx-auto mb-6 flex justify-between items-center border-b border-stone-200 pb-4 shrink-0">
        <div 
          onClick={(e) => {
            if (e.detail === 3) {
              setIsGodMode(prev => !prev);
            }
          }}
          className="flex items-center gap-3 cursor-pointer select-none active:scale-[0.99] transition"
          title="Triple-click to toggle offline God-Mode demo"
        >
          <div className="w-10 h-10 rounded-xl bg-stone-900 flex items-center justify-center shadow-md">
            <Compass className="w-5.5 h-5.5 text-stone-50 animate-spin-slow" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-stone-900">
                Astro-Synthesis Matrix Engine
              </h1>
              {isGodMode && (
                <span className="text-[9px] bg-amber-100 border border-amber-300 text-amber-800 px-1.5 py-0.5 rounded font-extrabold tracking-wider animate-pulse leading-none shrink-0">
                  ⚡ GOD-MODE
                </span>
              )}
            </div>
            <p className="text-[10px] text-stone-500 tracking-wider uppercase font-semibold mt-0.5">
              Hybrid Ephemeris & ZWDS Downstream Inference Pipeline
            </p>
          </div>
        </div>
 
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setSynthesis(null);
              setCompletion(null);
            }}
            className="text-[10px] font-bold uppercase tracking-wider text-stone-600 hover:text-stone-950 px-3.5 py-2 border border-stone-200 rounded-xl bg-white hover:bg-stone-50 shadow-sm transition cursor-pointer"
          >
            ← Change Parameters
          </button>
          <div className="flex items-center gap-2 text-[10px] text-stone-600 border border-stone-200 px-3 py-1.5 rounded-xl bg-white shadow-sm">
            <Database className="w-3.5 h-3.5 text-stone-600" />
            <span>Local Engine Status: <strong className="text-emerald-600 font-bold">Online</strong></span>
          </div>
        </div>
      </header>
 
      {/* Main Container */}
      <main className="max-w-7xl w-full mx-auto flex-1 flex flex-col gap-4 overflow-hidden">
        
        {/* Safety Warnings Banner */}
        <SafetyBanners
          dualMatrix={synthesis.birth_time_metrics.branch_boundary_anomaly}
          preflightDeflection={preflightDeflection}
        />
 
        {/* Global Error Notice */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-5 py-4 rounded-2xl text-xs flex items-center gap-3 shadow-sm shrink-0">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
            <div>
              <strong className="font-bold">Backend Integration Error:</strong> {error}
            </div>
          </div>
        )}
 
        {/* Split View Dashboard Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-180px)] min-h-[580px]">
          
          {/* LEFT COLUMN (2/3 width): Cleansed Chart Display Area */}
          <div className="lg:col-span-2 flex flex-col gap-4 h-full">
            {/* System Toggles */}
            <div className="flex bg-stone-100 rounded-lg p-1 border border-stone-200 shrink-0 select-none">
              <button
                onClick={() => setActiveTab("zwds")}
                className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-md transition cursor-pointer ${
                  activeTab === "zwds"
                    ? "bg-white text-stone-900 shadow-sm border border-stone-200/50"
                    : "text-stone-600 hover:bg-stone-50 hover:text-stone-950"
                }`}
              >
                Chinese Zi Wei Dou Shu
              </button>
              <button
                onClick={() => setActiveTab("western")}
                className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-md transition cursor-pointer ${
                  activeTab === "western"
                    ? "bg-white text-stone-900 shadow-sm border border-stone-200/50"
                    : "text-stone-600 hover:bg-stone-50 hover:text-stone-950"
                }`}
              >
                Western Ephemeris Natal
              </button>
            </div>
            
            {/* The Interactive Chart Stage */}
            <div className="flex-1 bg-white border border-stone-200 rounded-xl p-6 shadow-sm flex items-center justify-center overflow-hidden">
              <div className="w-full max-h-full overflow-y-auto">
                {activeTab === "zwds" ? (
                  <ZWDSPalaceGrid
                    matrix={synthesis.zwds_matrix}
                    birthDate={activeRequest?.birth_date || ""}
                    birthTime={activeRequest?.birth_time || ""}
                    gender={activeRequest?.gender || "M"}
                    locationName={locationName}
                    targetVector={activeRequest?.target_vector || "wealth"}
                  />
                ) : (
                  <WesternChart matrix={synthesis.western_matrix} aspects={synthesis.synthesis_flags.aspects} />
                )}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN (1/3 width): Pinned Dynamic Copilot Sidebar */}
          <div className="lg:col-span-1 bg-white border border-stone-200 rounded-xl shadow-sm flex flex-col h-full overflow-hidden">
            
            {/* Pinned Top Block: Unified Friction Metric Index */}
            <div className="p-4 border-b border-stone-100 bg-stone-50/50 shrink-0">
              <VectorDashboard
                flags={synthesis.synthesis_flags}
                targetVector={activeRequest?.target_vector || "wealth"}
              />
            </div>

            {/* Scrollable Bottom Block & Chat Input */}
            <ClientChat
              storageKey={storageKey}
              initialReading={completion?.reading || ""}
              onSelectSession={executeAstrologySynthesis}
              isLLMLoading={isLLMLoading}
              activeChartPayload={synthesis?.zwds_matrix}
            />
            
          </div>
        </div>
 
      </main>
 
      {/* Footer */}
      <footer className="max-w-7xl w-full mx-auto border-t border-stone-200 mt-6 pt-4 text-center text-[10px] text-stone-400 flex flex-col sm:flex-row justify-between items-center gap-3 shrink-0">
        <span>© 2026 Astro-Synthesis Project for CalHacks. All rights reserved.</span>
        <span className="flex items-center gap-1">
          <ShieldAlert className="w-3.5 h-3.5 text-stone-400" />
          Zero-PII Data Policy. Local browser session isolation active.
        </span>
      </footer>

    </div>
  );
}
