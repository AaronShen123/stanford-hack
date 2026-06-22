// ── UI layer ──────────────────────────────────────────────────────────────
// Presentation only. All chart computation lives in ../../ziwei/useZiweiChart.
import { useZiweiChart, type BirthParams } from "../../ziwei/useZiweiChart";
import ChartBoard from "./ChartBoard";

export default function ZiweiBoard(props: BirthParams) {
  const { chart, error } = useZiweiChart(props);

  if (error || !chart) {
    return (
      <div className="flex items-center justify-center min-h-[200px] text-sm text-stone-400 italic">
        {error || "No chart yet."}
      </div>
    );
  }

  return (
    <div className="ziwei-board w-full">
      <ChartBoard chart={chart} />
    </div>
  );
}
