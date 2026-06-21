import React from "react";
import { ShieldAlert, AlertTriangle, X } from "lucide-react";

interface SafetyBannersProps {
  dualMatrix: boolean;
  preflightDeflection?: boolean;
}

export default function SafetyBanners({ dualMatrix, preflightDeflection }: SafetyBannersProps) {
  const [showDualMatrixWarning, setShowDualMatrixWarning] = React.useState(true);

  if (!dualMatrix && !preflightDeflection) return null;

  return (
    <div className="w-full space-y-3 mb-6 select-none animate-fadeIn shrink-0">
      {/* Pre-flight deflection deflection warning */}
      {preflightDeflection && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-xl flex items-start gap-3 shadow-sm">
          <ShieldAlert className="w-5 h-5 text-red-650 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-red-900 uppercase tracking-wider">
              Safety Router Deflection Active
            </h4>
            <p className="text-xs text-red-700 mt-1 leading-relaxed">
              Pre-flight payload check detected critical coordinate variance or sensitive query vectors. 
              Downstream completion model has been routed through maximum alignment parameters.
            </p>
          </div>
        </div>
      )}

      {/* Dual matrix branch shift warning */}
      {dualMatrix && showDualMatrixWarning && (
        <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl flex items-start justify-between gap-3 shadow-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-amber-900 uppercase tracking-wider">
                Branch Shift Boundary Anomaly ($\pm$60s)
              </h4>
              <p className="text-xs text-amber-700 mt-1 leading-relaxed">
                The computed True Local Time (TLT) falls within 60 seconds of a traditional Earthly Branch hour boundary. 
                Dual-matrix calculations are active to prevent cusp variance. The reasoning model is warned of potential structural drift.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowDualMatrixWarning(false)}
            className="text-stone-400 hover:text-stone-700 transition shrink-0 p-1 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
