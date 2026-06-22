export type TargetVector = "wealth" | "affinity" | "vitality" | "macro_evolution";
export type Gender = "M" | "F";

export interface AstrologyRequest {
  birth_date: string; // YYYY-MM-DD
  birth_time: string; // HH:MM:SS
  latitude: number;
  longitude: number;
  target_vector: TargetVector;
  timezone_offset?: number | null;
  gender?: Gender;
}

export interface TimeMetricsModel {
  local_datetime: string;
  utc_datetime: string;
  lmt_datetime: string;
  tlt_datetime: string;
  timezone_offset: number;
  jd_ut: number;
  jd_et: number;
  eot_seconds: number;
  branch_boundary_anomaly: boolean;
}

export interface WesternMatrix {
  sun_degree: number;
  moon_degree: number;
  ascendant_degree: number;
  midheaven_degree: number;
  saturn_degree: number;
  mars_degree: number;
  neptune_degree: number;
  pluto_degree: number;
  houses: Record<number, number>;
}

export interface StarMetadata {
  name: string;
  brightness_index: string;
  classification: string;
  archetype_definition: string;
  is_borrowed?: boolean;
  mutagen?: string;
}

export interface ZWDSPalace {
  name: string;
  stem_branch: string;
  stars: string[];
  decadal_range?: string;
  main_stars?: { name: string; status?: string; is_borrowed?: boolean; mutagen?: string }[];
  minor_stars?: string[];
  changsheng?: string;
  pillar_gods?: string[];
  one_year_luck?: string;
  stars_metadata?: StarMetadata[];
  intensity?: number;
}

export interface ZWDSMatrix {
  palaces: ZWDSPalace[];
  yearly_stem_branch: string;
  monthly_branch: string;
  lunar_date_str: string;
  life_master?: string;
  body_master?: string;
}

export interface AstrologyAspect {
  planet1: string;
  planet2: string;
  aspect_type: "conjunction" | "sextile" | "square" | "trine" | "opposition";
  degree_difference: number;
  orb: number;
}

export interface ZWDSPattern {
  name: string;
  is_triggered: boolean;
  description: string;
}

export interface SynthesisFlags {
  friction_index: number;
  friction_points: string[];
  aspects: AstrologyAspect[];
  synthesis_notes: string[];
  dual_matrix_indicator: boolean;
  critical_bottleneck: boolean;
  interpersonal_risk: boolean;
  systemic_exhaustion: boolean;
  palace_friction_index: number;
  detected_patterns: ZWDSPattern[];
}

export interface AstrologyResponse {
  birth_time_metrics: TimeMetricsModel;
  western_matrix: WesternMatrix;
  zwds_matrix: ZWDSMatrix;
  synthesis_flags: SynthesisFlags;
}

export interface AstrologyCompletionResponse {
  synthesis: AstrologyResponse;
  compiled_prompt: string;
  reading: string;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
  timestamp: string;
}
