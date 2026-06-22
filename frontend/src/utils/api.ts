import type { AstrologyRequest, AstrologyCompletionResponse, AstrologyResponse } from "../types";

const host = typeof window !== "undefined" ? window.location.hostname : "localhost";
const BASE_URL = `http://${host}:8000/api/v1/astrology`;

export async function fetchAstrologySynthesis(payload: AstrologyRequest): Promise<AstrologyResponse> {
  const response = await fetch(`${BASE_URL}/synthesis`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Astrological synthesis calculation failed.");
  }

  return response.json();
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface ChatReply {
  answer: string;
  horoscope_date?: string | null;
}

export async function fetchChatReply(
  request: AstrologyRequest,
  messages: ChatTurn[],
  question: string,
  targetDate?: string | null,
  timeIndex?: number | null
): Promise<ChatReply> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      request,
      messages,
      question,
      target_date: targetDate ?? null,
      time_index: timeIndex ?? null,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "The master could not read the chart right now.");
  }

  return response.json();
}

export async function fetchAstrologyCompletion(payload: AstrologyRequest): Promise<AstrologyCompletionResponse> {
  const response = await fetch(`${BASE_URL}/completion`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Astrological completion analysis failed.");
  }

  return response.json();
}
