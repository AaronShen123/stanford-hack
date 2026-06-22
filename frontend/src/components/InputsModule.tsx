import { useState, useEffect } from "react";
import type { AstrologyRequest, TargetVector, Gender } from "../types";
import { Search, MapPin, Loader2, Compass } from "lucide-react";

interface InputsModuleProps {
  onSubmit: (data: AstrologyRequest, locationName: string) => void;
  isLoading: boolean;
}

const TIME_BRANCHES = [
  { value: "Zi", label: "子 (23:00 - 00:59)" },
  { value: "Chou", label: "丑 (01:00 - 02:59)" },
  { value: "Yin", label: "寅 (03:00 - 04:59)" },
  { value: "Mao", label: "卯 (05:00 - 06:59)" },
  { value: "Chen", label: "辰 (07:00 - 08:59)" },
  { value: "Si", label: "巳 (09:00 - 10:59)" },
  { value: "Wu", label: "午 (11:00 - 12:59)" },
  { value: "Wei", label: "未 (13:00 - 14:59)" },
  { value: "Shen", label: "申 (15:00 - 16:59)" },
  { value: "You", label: "酉 (17:00 - 18:59)" },
  { value: "Xu", label: "戌 (19:00 - 20:59)" },
  { value: "Hai", label: "亥 (21:00 - 22:59)" }
];

export default function InputsModule({ onSubmit, isLoading }: InputsModuleProps) {
  const [birthDate, setBirthDate] = useState("1990-05-15");
  const [birthTime, setBirthTime] = useState("Wu");
  const [gender, setGender] = useState<Gender>("M");
  const [targetVector, setTargetVector] = useState<TargetVector>("wealth");
  
  // Geocoding states
  const [locationQuery, setLocationQuery] = useState("");
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [useManualCoords, setUseManualCoords] = useState(false);
  
  const [latitude, setLatitude] = useState(37.7749);
  const [longitude, setLongitude] = useState(-122.4194);
  const [selectedPlaceName, setSelectedPlaceName] = useState("San Francisco, CA");

  // Debounced geocoding query matching OSM Nominatim usage requirements
  useEffect(() => {
    if (locationQuery.trim().length < 3) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoadingSuggestions(true);
      try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          locationQuery
        )}&limit=5`;
        
        const response = await fetch(url, {
          headers: {
            "User-Agent": "AstrologySynthesisDashboard/1.0 (contact: developer@metaphysics-engine.local)",
          },
        });

        if (response.ok) {
          const data = await response.json();
          setSuggestions(data);
          setShowSuggestions(true);
        } else {
          setUseManualCoords(true);
        }
      } catch (err) {
        console.warn("OSM Nominatim API request failed or timed out. Falling back to manual coordinates.");
        setUseManualCoords(true);
      } finally {
        setLoadingSuggestions(false);
      }
    }, 600); // 600ms debounce to prevent geocoding rate bans

    return () => clearTimeout(timer);
  }, [locationQuery]);

  const handleSelectSuggestion = (suggestion: any) => {
    const lat = parseFloat(suggestion.lat);
    const lon = parseFloat(suggestion.lon);
    setLatitude(lat);
    setLongitude(lon);
    setSelectedPlaceName(suggestion.display_name);
    setShowSuggestions(false);
    setLocationQuery("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      birth_date: birthDate,
      birth_time: birthTime,
      latitude,
      longitude,
      target_vector: targetVector,
      gender,
      timezone_offset: null
    }, selectedPlaceName);
  };

  return (
    <div className="bg-white border border-stone-200 p-6 rounded-2xl shadow-sm">
      <h2 className="text-xl font-bold text-stone-900 mb-6 flex items-center gap-2">
        <Compass className="text-stone-850 w-5 h-5 animate-spin-slow" />
        Input Parameters
      </h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Date & Time */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-[11px] font-bold tracking-wider text-stone-500 uppercase font-sans mb-2">
              Birth Date
            </label>
            <input
              type="date"
              required
              max="2100-12-31"
              min="1900-01-01"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              className="w-full h-11 px-3 bg-white border border-stone-300 rounded-lg text-stone-900 placeholder-stone-400 focus:outline-none focus:border-stone-950 text-sm flex items-center font-sans font-medium transition-colors duration-200 hover:border-stone-400"
            />
          </div>
          <div>
            <label className="block text-[11px] font-bold tracking-wider text-stone-500 uppercase font-sans mb-2">
              Birth Time (Local Branch)
            </label>
            <select
              value={birthTime}
              onChange={(e) => setBirthTime(e.target.value)}
              className="w-full h-11 px-3 bg-white border border-stone-300 rounded-lg text-stone-900 focus:outline-none focus:border-stone-950 text-sm font-sans font-medium transition-colors duration-200 hover:border-stone-400 cursor-pointer"
            >
              {TIME_BRANCHES.map((tb) => (
                <option key={tb.value} value={tb.value}>
                  {tb.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Location Search Autocomplete */}
        <div className="relative">
          <label className="block text-[11px] font-bold tracking-wider text-stone-500 uppercase font-sans mb-2 flex justify-between items-center">
            <span>Location Search</span>
            <button
              type="button"
              onClick={() => setUseManualCoords(!useManualCoords)}
              className="text-[10px] text-stone-600 hover:text-stone-900 transition uppercase tracking-widest font-bold font-sans"
            >
              {useManualCoords ? "Use Search" : "Manual Coordinates"}
            </button>
          </label>

          {!useManualCoords ? (
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5" />
              <input
                type="text"
                placeholder="Search birth city (e.g. San Francisco)..."
                value={locationQuery}
                onChange={(e) => setLocationQuery(e.target.value)}
                className="w-full h-11 pl-11 pr-4 bg-white border border-stone-300 rounded-lg text-stone-900 placeholder-stone-400 focus:outline-none focus:border-stone-950 text-sm flex items-center font-sans font-medium transition-colors duration-200 hover:border-stone-400"
              />
              {loadingSuggestions && (
                <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-450 animate-spin w-4 h-4" />
              )}

              {/* Suggestions dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <ul className="absolute z-50 w-full mt-2 bg-white border border-stone-200 rounded-xl shadow-lg overflow-hidden max-h-60 overflow-y-auto">
                  {suggestions.map((s, idx) => (
                    <li
                      key={idx}
                      onClick={() => handleSelectSuggestion(s)}
                      className="px-4 py-3 hover:bg-stone-50 text-xs text-stone-755 border-b border-stone-100 cursor-pointer flex items-start gap-2.5 transition font-sans"
                    >
                      <MapPin className="w-4 h-4 text-stone-500 shrink-0 mt-0.5" />
                      <span>{s.display_name}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <input
                  type="number"
                  step="any"
                  placeholder="Latitude (-90 to 90)"
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value))}
                  className="w-full h-11 px-3 bg-white border border-stone-300 rounded-lg text-stone-900 placeholder-stone-400 focus:outline-none focus:border-stone-950 text-sm flex items-center font-sans font-medium transition-colors duration-200 hover:border-stone-400"
                />
              </div>
              <div>
                <input
                  type="number"
                  step="any"
                  placeholder="Longitude (-180 to 180)"
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value))}
                  className="w-full h-11 px-3 bg-white border border-stone-300 rounded-lg text-stone-900 placeholder-stone-400 focus:outline-none focus:border-stone-950 text-sm flex items-center font-sans font-medium transition-colors duration-200 hover:border-stone-400"
                />
              </div>
            </div>
          )}

          {/* Current coordinates preview */}
          <div className="mt-2 text-[10px] text-stone-400 flex items-center gap-1.5 px-1 font-sans">
            <MapPin className="w-3 h-3 text-stone-500" />
            <span className="truncate max-w-[280px]">
              {selectedPlaceName} ({latitude.toFixed(4)}°N, {longitude.toFixed(4)}°E)
            </span>
          </div>
        </div>

        {/* Gender & Target Vector */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-[11px] font-bold tracking-wider text-stone-500 uppercase font-sans mb-2">
              Gender (Polarity)
            </label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value as Gender)}
              className="w-full h-11 px-3 bg-white border border-stone-300 rounded-lg text-stone-900 focus:outline-none focus:border-stone-950 text-sm font-sans font-medium transition-colors duration-200 hover:border-stone-400 cursor-pointer"
            >
              <option value="M">Male (Yang)</option>
              <option value="F">Female (Yin)</option>
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-bold tracking-wider text-stone-500 uppercase font-sans mb-2">
              Target Vector
            </label>
            <select
              value={targetVector}
              onChange={(e) => setTargetVector(e.target.value as TargetVector)}
              className="w-full h-11 px-3 bg-white border border-stone-300 rounded-lg text-stone-900 focus:outline-none focus:border-stone-950 text-sm font-sans font-medium transition-colors duration-200 hover:border-stone-400 cursor-pointer"
            >
              <option value="wealth">Wealth Flow</option>
              <option value="affinity">Relational Affinity</option>
              <option value="vitality">Somatic Vitality</option>
              <option value="macro_evolution">Macro Evolution</option>
            </select>
          </div>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3.5 px-4 bg-stone-900 text-stone-50 hover:bg-stone-800 font-extrabold rounded-xl shadow-sm active:scale-[0.98] transition flex justify-center items-center gap-2 cursor-pointer disabled:opacity-50 disabled:pointer-events-none"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin text-stone-50" />
              Synthesizing Engine...
            </>
          ) : (
            "Generate Astrology Chart"
          )}
        </button>
      </form>
    </div>
  );
}
