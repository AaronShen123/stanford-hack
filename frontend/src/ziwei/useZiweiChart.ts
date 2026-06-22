// ── Chart computation layer (data/"rendering") ───────────────────────────
// Pure logic: birth parameters → a ZiweiChart data object. No JSX, no styling.
// The UI layer (ZiweiBoard / ChartBoard) only presents what this returns.

import { useMemo } from "react";
import type { BirthInfo, ZiweiChart } from "./types";
import { generateChart } from "./algorithm";

const BRANCH_INDEX: Record<string, number> = {
  Zi: 0, Chou: 1, Yin: 2, Mao: 3, Chen: 4, Si: 5,
  Wu: 6, Wei: 7, Shen: 8, You: 9, Xu: 10, Hai: 11,
};

/** Local clock time + longitude → 时辰 branch (0=Zi..11=Hai), matching the reference app. */
function clockToBranch(hour: number, minute: number, longitude: number): number {
  const clockMins = hour * 60 + minute;
  const offset = (longitude - 120) * 4; // 4 min per degree from the 120°E meridian
  const solar = ((clockMins + offset) % 1440 + 1440) % 1440;
  if (solar >= 1380 || solar < 60) return 0; // 23:00–01:00 → Zi
  return Math.floor((solar - 60) / 120) + 1;
}

/**
 * Resolve the 时辰 branch from whatever `birthTime` form the app supplies:
 * an Earthly-Branch name ("Si", "Wu", …) or a clock time ("HH:MM[:SS]").
 * Falls back to Wu (noon) rather than producing NaN, which would crash iztro.
 */
export function resolveBranch(birthTime: string, longitude: number): number {
  if (!birthTime) return 6;
  if (birthTime in BRANCH_INDEX) return BRANCH_INDEX[birthTime];
  const [h, m] = birthTime.split(":").map((n) => parseInt(n, 10));
  if (Number.isFinite(h)) return clockToBranch(h, Number.isFinite(m) ? m : 0, longitude);
  return 6;
}

export interface BirthParams {
  birthDate: string; // YYYY-MM-DD
  birthTime: string; // branch name ("Si") or clock "HH:MM:SS"
  gender: string;    // "M" | "F"
  longitude?: number;
  name?: string;
}

export interface ZiweiResult {
  chart: ZiweiChart | null;
  error: string | null;
}

/** Compute the chart from birth params; never throws — errors are returned. */
export function computeZiweiChart({
  birthDate, birthTime, gender, longitude = 120, name,
}: BirthParams): ZiweiResult {
  const [y, mo, d] = (birthDate || "").split("-").map((n) => parseInt(n, 10));
  if (!Number.isFinite(y) || !Number.isFinite(mo) || !Number.isFinite(d)) {
    return { chart: null, error: "Enter a valid birth date to cast the chart." };
  }
  const info: BirthInfo = {
    year: y,
    month: mo,
    day: d,
    hour: resolveBranch(birthTime, longitude),
    gender: gender?.toUpperCase().startsWith("F") ? "female" : "male",
    name,
    longitude,
  };
  try {
    return { chart: generateChart(info), error: null };
  } catch (e: any) {
    return { chart: null, error: e?.message || "Could not compute this chart." };
  }
}

/** React hook wrapper around computeZiweiChart (memoized on inputs). */
export function useZiweiChart(params: BirthParams): ZiweiResult {
  return useMemo(
    () => computeZiweiChart(params),
    [params.birthDate, params.birthTime, params.gender, params.longitude, params.name],
  );
}
