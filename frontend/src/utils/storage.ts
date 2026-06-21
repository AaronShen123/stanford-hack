import type { ChatMessage, AstrologyRequest } from "../types";

export function generateStorageKey(payload: AstrologyRequest): string {
  const { birth_date, birth_time, latitude, longitude, target_vector } = payload;
  // URL-safe delimited string as explicit audited key to maintain local observability
  return `astrology_session_v1||${birth_date}||${birth_time}||${latitude.toFixed(4)}||${longitude.toFixed(4)}||${target_vector}`;
}

export function saveChatHistory(key: string, messages: ChatMessage[]): void {
  try {
    // FIFO Trimming Strategy: Cap message history at 50 messages to prevent QuotaExceededError
    const MAX_MESSAGES = 50;
    let trimmedMessages = messages;
    if (messages.length > MAX_MESSAGES) {
      trimmedMessages = messages.slice(messages.length - MAX_MESSAGES);
    }
    
    localStorage.setItem(key, JSON.stringify(trimmedMessages));
  } catch (error) {
    console.error("Failed to write to LocalStorage:", error);
  }
}

export function loadChatHistory(key: string): ChatMessage[] {
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error("Failed to read from LocalStorage:", error);
    return [];
  }
}

export function getAllSessions(): Array<{ key: string; date: string; time: string; lat: string; lon: string; target: string }> {
  const sessions: Array<{ key: string; date: string; time: string; lat: string; lon: string; target: string }> = [];
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith("astrology_session_v1||")) {
        const parts = key.split("||");
        sessions.push({
          key,
          date: parts[1] || "",
          time: parts[2] || "",
          lat: parts[3] || "",
          lon: parts[4] || "",
          target: parts[5] || ""
        });
      }
    }
  } catch (e) {
    console.error("Failed to fetch sessions:", e);
  }
  return sessions;
}
