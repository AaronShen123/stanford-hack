// ── Chat data layer ───────────────────────────────────────────────────────
// Owns conversation state, persistence, and the call to the ZWDS-master
// backend. No JSX — the UI (ClientChat) only renders what this returns.

import { useState, useEffect, useCallback } from "react";
import type { ChatMessage, AstrologyRequest, ZWDSMatrix } from "../types";
import { loadChatHistory, saveChatHistory, getAllSessions } from "../utils/storage";
import { fetchChatReply, type ChatTurn } from "../utils/api";
import { resolveBranch } from "../ziwei/useZiweiChart";

const newId = () => Math.random().toString(36).substr(2, 9);
const now = () => new Date().toLocaleTimeString();

interface UseMasterChatArgs {
  storageKey: string;
  activeRequest?: AstrologyRequest | null;
  activeChartPayload?: ZWDSMatrix;
}

export interface MasterChat {
  messages: ChatMessage[];
  isThinking: boolean;
  sessions: any[];
  quickActions: string[];
  /** Send a question to the master; appends user + assistant turns. */
  send: (text: string) => Promise<void>;
}

const QUICK_ACTIONS = [
  "📅 What happened to me in 2021? (流年 reading)",
  "💰 Read my Wealth & Career palaces — where does my money come from?",
  "💗 Read my Marriage palace — what is my love life like?",
];

export function useMasterChat({ storageKey, activeRequest, activeChartPayload }: UseMasterChatArgs): MasterChat {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [sessions, setSessions] = useState<any[]>([]);

  // Load saved history (or seed a chart-aware greeting) when a chart loads.
  useEffect(() => {
    if (!storageKey || !activeChartPayload) return;
    const history = loadChatHistory(storageKey);
    if (history.length === 0) {
      const palaces = activeChartPayload.palaces || [];
      const life = palaces.find(p => p.stem_branch.split("-")[1] === "Si");
      const stars = life?.main_stars?.map(s => `${s.name}${s.status ? `(${s.status})` : ""}`).join(", ") || "your major stars";
      const greeting: ChatMessage = {
        id: "initial_reading",
        sender: "ai",
        timestamp: now(),
        text: `Your chart is cast. Ask me anything about your life — career, wealth, love, health — and I'll read it strictly from your chart (命盤). You can also give me a **past date or year** (e.g. "what happened to me in 2021?") and I'll reconstruct that period and the people you met from your 流年/流日 transits.`,
      };
      setMessages([greeting]);
      saveChatHistory(storageKey, [greeting]);
    } else {
      setMessages(history);
    }
    setSessions(getAllSessions());
  }, [storageKey, activeChartPayload]);

  const send = useCallback(async (text: string) => {
    const question = text.trim();
    if (!storageKey || !question || isThinking) return;

    if (!activeRequest) {
      const warn: ChatMessage = { id: newId(), sender: "ai", timestamp: now(),
        text: "Please calculate a chart first — submit the birth parameters and I'll read it for you." };
      setMessages(prev => { const next = [...prev, warn]; saveChatHistory(storageKey, next); return next; });
      return;
    }

    const userMsg: ChatMessage = { id: newId(), sender: "user", text: question, timestamp: now() };
    let prior: ChatMessage[] = [];
    setMessages(prev => { prior = prev; const next = [...prev, userMsg]; saveChatHistory(storageKey, next); return next; });
    setIsThinking(true);

    try {
      const history: ChatTurn[] = prior
        .filter(m => m.id !== "initial_reading")
        .map(m => ({ role: m.sender === "ai" ? "assistant" : "user", content: m.text }));

      // Same branch the on-screen chart uses → AI reads the identical chart.
      const timeIndex = resolveBranch(activeRequest.birth_time, activeRequest.longitude ?? 120);

      const reply = await fetchChatReply(activeRequest, history, question, null, timeIndex);
      const note = reply.horoscope_date
        ? `\n\n---\n*Anchored to the 流年/流日 transits for ${reply.horoscope_date}.*`
        : "";
      const aiMsg: ChatMessage = { id: newId(), sender: "ai", text: reply.answer + note, timestamp: now() };
      setMessages(prev => { const next = [...prev, aiMsg]; saveChatHistory(storageKey, next); return next; });
    } catch (err: any) {
      const errMsg: ChatMessage = { id: newId(), sender: "ai", timestamp: now(),
        text: `⚠️ ${err?.message || "The reading could not be completed. Please try again."}` };
      setMessages(prev => { const next = [...prev, errMsg]; saveChatHistory(storageKey, next); return next; });
    } finally {
      setIsThinking(false);
    }
  }, [storageKey, activeRequest, isThinking]);

  return { messages, isThinking, sessions, quickActions: QUICK_ACTIONS, send };
}
