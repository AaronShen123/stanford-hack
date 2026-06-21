import { useMemo } from "react";
import type { WesternMatrix, AstrologyAspect } from "../types";
import { Activity } from "lucide-react";

interface WesternChartProps {
  matrix: WesternMatrix;
  aspects: AstrologyAspect[];
}

export default function WesternChart({ matrix, aspects }: WesternChartProps) {
  const width = 400;
  const height = 400;
  const cx = width / 2;
  const cy = height / 2;
  const outerRadius = 160;
  const innerRadius = 135;
  const centerRingRadius = 45;

  const asc = matrix.ascendant_degree;

  // Converts a zodiac degree (0-360) into SVG (x, y) coordinates.
  // Rotates the entire chart so the Ascendant (ASC) is locked on the left horizontal axis (180 degrees).
  const getCoordinates = (degree: number, radius: number) => {
    // 0 Aries (left/ASC) is standard. 
    const angleRad = ((180 + (degree - asc)) * Math.PI) / 180;
    const x = cx + radius * Math.cos(angleRad);
    const y = cy + radius * Math.sin(angleRad);
    return { x, y };
  };

  // List of planets and angles to display (ASC/MC handled separately as dedicated axes)
  const planets = useMemo(() => [
    { name: "Sun", deg: matrix.sun_degree, symbol: "☀️", color: "text-amber-400" },
    { name: "Moon", deg: matrix.moon_degree, symbol: "🌙", color: "text-blue-300" },
    { name: "Saturn", deg: matrix.saturn_degree, symbol: "🪐", color: "text-orange-400" },
    { name: "Mars", deg: matrix.mars_degree, symbol: "♂️", color: "text-red-500" },
    { name: "Neptune", deg: matrix.neptune_degree, symbol: "♆", color: "text-cyan-400" },
    { name: "Pluto", deg: matrix.pluto_degree, symbol: "♇", color: "text-purple-400" }
  ], [matrix]);

  // Render house cusps lines (houses 1 to 12)
  const houseLines = useMemo(() => {
    return Object.entries(matrix.houses).map(([houseNum, cuspDeg]) => {
      const start = getCoordinates(cuspDeg, centerRingRadius);
      const end = getCoordinates(cuspDeg, outerRadius);
      const labelPos = getCoordinates(cuspDeg + 15, innerRadius - 25); // Midpoint of house (30deg wide avg)
      
      return {
        houseNum,
        x1: start.x,
        y1: start.y,
        x2: end.x,
        y2: end.y,
        labelX: labelPos.x,
        labelY: labelPos.y
      };
    });
  }, [matrix.houses, asc]);

  // Render aspect paths inside the center wheel
  const aspectLines = useMemo(() => {
    return aspects.map((aspect, idx) => {
      // Find planetary degree mappings
      const getPlanetDegree = (name: string): number => {
        if (name === "Sun") return matrix.sun_degree;
        if (name === "Moon") return matrix.moon_degree;
        if (name === "Saturn") return matrix.saturn_degree;
        if (name === "Mars") return matrix.mars_degree;
        if (name === "Neptune") return matrix.neptune_degree;
        if (name === "Pluto") return matrix.pluto_degree;
        if (name === "Ascendant") return matrix.ascendant_degree;
        if (name === "Midheaven") return matrix.midheaven_degree;
        return 0;
      };

      const deg1 = getPlanetDegree(aspect.planet1);
      const deg2 = getPlanetDegree(aspect.planet2);
      
      const start = getCoordinates(deg1, centerRingRadius);
      const end = getCoordinates(deg2, centerRingRadius);

      // Map aspect types to colors: Opposition (rose-500), Square (amber-500), Trine (emerald-500), Conjunction (stone-300)
      let strokeColor = "#3b82f6"; // default blue
      if (aspect.aspect_type === "opposition") strokeColor = "#f43f5e"; // rose-500
      if (aspect.aspect_type === "square") strokeColor = "#f59e0b"; // amber-500
      if (aspect.aspect_type === "trine") strokeColor = "#10b981"; // emerald-500
      if (aspect.aspect_type === "conjunction") strokeColor = "#d6d3d1"; // stone-300

      // Audited continuous decay curve opacity: W_friction = 1.0 - (orb / 8.0)
      // Raise minimum opacity to 0.35 to ensure contrast on screens/projectors
      const opacity = Math.max(0.35, 1.0 - (aspect.orb / 8.0) * 0.65);

      return {
        key: idx,
        x1: start.x,
        y1: start.y,
        x2: end.x,
        y2: end.y,
        stroke: strokeColor,
        opacity,
        type: aspect.aspect_type,
        planets: `${aspect.planet1} / ${aspect.planet2}`
      };
    });
  }, [aspects, matrix, asc]);

  return (
    <div className="w-full flex flex-col items-center">
      <h2 className="text-xs font-bold text-stone-400 uppercase tracking-widest mb-4 flex items-center gap-2 self-start pl-1 w-full shrink-0">
        <Activity className="text-stone-550 w-4 h-4" />
        Western Natal Wheel
      </h2>

      <div className="relative">
        <svg width={width} height={height} className="rounded-full shadow-inner bg-stone-50">
          {/* Outer circle - enhanced contrast */}
          <circle cx={cx} cy={cy} r={outerRadius} fill="none" stroke="#78716c" strokeWidth="2" />
          <circle cx={cx} cy={cy} r={innerRadius} fill="none" stroke="#a8a29e" strokeWidth="1.5" />
          {/* Inner aspects circle */}
          <circle cx={cx} cy={cy} r={centerRingRadius} fill="#ffffff" stroke="#78716c" strokeWidth="1.5" />

          {/* House lines & labels - enhanced contrast */}
          {houseLines.map((line) => (
            <g key={line.houseNum}>
              <line
                x1={line.x1}
                y1={line.y1}
                x2={line.x2}
                y2={line.y2}
                stroke="#a8a29e"
                strokeWidth="1"
                strokeDasharray="4 2"
              />
              <text
                x={line.labelX}
                y={line.labelY}
                fill="#57534e"
                fontSize="9"
                fontWeight="bold"
                textAnchor="middle"
                dominantBaseline="middle"
              >
                {line.houseNum}
              </text>
            </g>
          ))}

          {/* Aspect Lines (scaled opacity by continuous decay orb) */}
          {aspectLines.map((line) => (
            <line
              key={line.key}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke={line.stroke}
              strokeWidth={line.type === "opposition" || line.type === "square" ? "2.5" : "1.5"}
              strokeOpacity={line.opacity}
              className="hover:stroke-stone-600 transition cursor-pointer"
            >
              <title>{`${line.planets} - ${line.type} (opacity ${line.opacity.toFixed(2)})`}</title>
            </line>
          ))}

          {/* Dedicated ASC (Ascendant) Axis Line & External Label */}
          {(() => {
            const ascCoords = getCoordinates(matrix.ascendant_degree, outerRadius + 10);
            const ascStart = getCoordinates(matrix.ascendant_degree, centerRingRadius);
            const textCoords = getCoordinates(matrix.ascendant_degree, outerRadius + 24);
            return (
              <g>
                <line
                  x1={ascStart.x}
                  y1={ascStart.y}
                  x2={ascCoords.x}
                  y2={ascCoords.y}
                  stroke="#1c1917"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  className="drop-shadow-[0_0_2px_rgba(28,25,23,0.2)]"
                />
                <text
                  x={textCoords.x}
                  y={textCoords.y}
                  fill="#1c1917"
                  fontSize="11"
                  fontWeight="black"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="select-none"
                >
                  ASC
                </text>
              </g>
            );
          })()}

          {/* Dedicated MC (Midheaven) Axis Line & External Label */}
          {(() => {
            const mcCoords = getCoordinates(matrix.midheaven_degree, outerRadius + 10);
            const mcStart = getCoordinates(matrix.midheaven_degree, centerRingRadius);
            const textCoords = getCoordinates(matrix.midheaven_degree, outerRadius + 24);
            return (
              <g>
                <line
                  x1={mcStart.x}
                  y1={mcStart.y}
                  x2={mcCoords.x}
                  y2={mcCoords.y}
                  stroke="#059669"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  className="drop-shadow-[0_0_2px_rgba(5,150,105,0.2)]"
                />
                <text
                  x={textCoords.x}
                  y={textCoords.y}
                  fill="#059669"
                  fontSize="11"
                  fontWeight="black"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="select-none"
                >
                  MC
                </text>
              </g>
            );
          })()}

          {/* Planetary nodes */}
          {planets.map((p) => {
            const coords = getCoordinates(p.deg, outerRadius - 15);
            return (
              <g key={p.name} className="group cursor-pointer">
                <circle
                  cx={coords.x}
                  cy={coords.y}
                  r="10"
                  fill="#ffffff"
                  stroke="#78716c"
                  strokeWidth="1.5"
                  className="group-hover:stroke-stone-900 group-hover:fill-stone-50 transition"
                />
                <text
                  x={coords.x}
                  y={coords.y}
                  fontSize="10"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="select-none"
                >
                  {p.symbol}
                </text>
                {/* Tooltip trigger */}
                <title>{`${p.name}: ${p.deg.toFixed(2)}°`}</title>
              </g>
            );
          })}

          {/* Center decoration */}
          <circle cx={cx} cy={cy} r="6" fill="#1c1917" />
        </svg>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-4 gap-3 mt-6 text-[10px] text-stone-550 font-semibold tracking-wider uppercase">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block"></span>
          <span>Opposition</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span>
          <span>Square</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
          <span>Trine</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-stone-300 inline-block"></span>
          <span>Conj</span>
        </div>
      </div>
    </div>
  );
}
