import type { SynthesisFlags, TargetVector } from "../types";
import { TrendingUp, ShieldAlert, Award } from "lucide-react";

interface VectorDashboardProps {
  flags: SynthesisFlags;
  targetVector: TargetVector;
}

export default function VectorDashboard({ flags, targetVector }: VectorDashboardProps) {
  // Determine vector metadata
  const vectorMeta = {
    wealth: {
      title: "Wealth Flow",
      icon: <TrendingUp className="w-5.5 h-5.5 text-emerald-600" />,
      colorClass: "text-emerald-800 border-emerald-200 bg-emerald-50/50",
      description: "Assesses material acquisition capacity, professional blocks, and decadal career friction."
    },
    affinity: {
      title: "Relational Affinity",
      icon: <Award className="w-5.5 h-5.5 text-stone-750" />,
      colorClass: "text-stone-800 border-stone-200 bg-stone-50",
      description: "Analyzes marital configurations, business partnerships, and social communication channels."
    },
    vitality: {
      title: "Somatic Vitality",
      icon: <Award className="w-5.5 h-5.5 text-rose-600" />,
      colorClass: "text-rose-800 border-rose-200 bg-rose-50/50",
      description: "Evaluates physical integration, energy depletion risk, and health brightness indices."
    },
    macro_evolution: {
      title: "Macro Evolution",
      icon: <Award className="w-5.5 h-5.5 text-stone-900" />,
      colorClass: "text-stone-900 border-stone-200 bg-stone-100/50",
      description: "Outlines life path trajectory, identity alignment, and public visibility thresholds."
    }
  }[targetVector];

  // Dynamic status of the friction level
  const frictionPercentage = Math.min(100, (flags.friction_index / 8.0) * 100);
  let statusText = "Harmonious";
  let barColor = "bg-emerald-500";
  if (flags.friction_index > 2.0) {
    statusText = "Moderate Friction";
    barColor = "bg-yellow-500";
  }
  if (flags.friction_index > 5.0) {
    statusText = "High Structural Pressure";
    barColor = "bg-rose-500";
  }

  return (
    <div className="bg-white border border-stone-200 p-5 rounded-2xl shadow-sm space-y-4">
      {/* Title */}
      <div className={`border p-4 rounded-xl flex items-start gap-3 ${vectorMeta.colorClass}`}>
        {vectorMeta.icon}
        <div>
          <h3 className="font-bold text-stone-900 text-xs">{vectorMeta.title} Strategic Matrix</h3>
          <p className="text-[11px] text-stone-500 mt-1 leading-relaxed">{vectorMeta.description}</p>
        </div>
      </div>

      {/* Friction Index Progress Gauge */}
      <div className="bg-stone-50 border border-stone-200 p-4 rounded-xl space-y-3">
        <div className="flex justify-between items-center text-xs">
          <span className="font-semibold text-stone-500 uppercase tracking-wider">
            Continuous Friction Index
          </span>
          <span className="font-extrabold text-stone-900">
            {flags.friction_index.toFixed(2)} / 8.00
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-stone-200 h-2.5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${barColor}`}
            style={{ width: `${frictionPercentage}%` }}
          ></div>
        </div>

        <div className="flex justify-between items-center text-[10px] text-stone-400">
          <span>Scale 0.0 (Min) - 8.0 (Max)</span>
          <span className="font-bold uppercase tracking-wider text-stone-600">{statusText}</span>
        </div>
      </div>

      {/* Unified System Actions / Critical Warnings */}
      {(flags.critical_bottleneck || flags.interpersonal_risk || flags.systemic_exhaustion) && (
        <div className="border border-red-200 bg-red-50 p-4 rounded-xl space-y-2">
          <div className="flex items-center gap-2 text-red-800 font-bold text-xs uppercase tracking-wider">
            <ShieldAlert className="w-5 h-5 shrink-0 text-red-600" />
            Critical System Warning
          </div>
          <div className="text-[11px] text-red-700 space-y-1.5 pl-1 leading-relaxed">
            {flags.critical_bottleneck && (
              <p>
                ⚠️ <strong>Wealth Bottleneck Triggered:</strong> Saturn opposition/square Midheaven combined with a ZWDS Hua-Ji block.
              </p>
            )}
            {flags.interpersonal_risk && (
              <p>
                ⚠️ <strong>Interpersonal Risk Triggered:</strong> Mars/Pluto opposition combined with Spouse/Friends Hua-Ji catalyst.
              </p>
            )}
            {flags.systemic_exhaustion && (
              <p>
                ⚠️ <strong>Systemic Vitality Exhaustion:</strong> Moon/Neptune hard aspects coinciding with ZWDS Health Palace star dimming.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
