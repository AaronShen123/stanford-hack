import React, { useState, useEffect, useRef } from "react";
import type { ChatMessage, AstrologyRequest, ZWDSMatrix } from "../types";
import { loadChatHistory, saveChatHistory, getAllSessions } from "../utils/storage";
import { MessageSquare, Send, History, Sparkles, User, Database, ArrowRight } from "lucide-react";

// Helper to parse simple markdown bold elements
function parseInline(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} className="font-extrabold text-stone-900">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

// Simple regex-based markdown parser for structured AI readings
function parseMarkdown(text: string): React.ReactNode[] {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let tableRows: string[][] = [];
  let isTable = false;

  const flushTable = (key: string | number) => {
    if (tableRows.length === 0) return;
    const headers = tableRows[0];
    const dataRows = tableRows.slice(1);
    elements.push(
      <div key={`table-${key}`} className="overflow-x-auto my-3.5 border border-stone-200 rounded-xl max-w-full">
        <table className="min-w-full divide-y divide-stone-200 text-[11px] leading-normal">
          <thead className="bg-stone-50 text-stone-700 font-bold uppercase tracking-wider">
            <tr>
              {headers.map((h, i) => (
                <th key={i} className="px-3 py-2 text-left">{parseInline(h)}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-150 bg-stone-50/10 text-stone-800">
            {dataRows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-stone-100/50">
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-3 py-2 whitespace-normal break-words">{parseInline(cell)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
    tableRows = [];
    isTable = false;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Handle tables
    if (line.startsWith("|") && line.endsWith("|")) {
      isTable = true;
      if (line.includes("---") || line.includes("===")) {
        continue;
      }
      const cells = line.split("|").slice(1, -1).map(c => c.trim());
      tableRows.push(cells);
      continue;
    } else if (isTable) {
      flushTable(i);
    }

    if (line.startsWith("### ")) {
      elements.push(
        <h4 key={i} className="text-[12px] font-bold text-stone-850 mt-4 mb-2 uppercase tracking-wider">
          {parseInline(line.slice(4))}
        </h4>
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <h3 key={i} className="text-[13px] font-extrabold text-stone-900 mt-5 mb-2.5 border-b border-stone-200 pb-1">
          {parseInline(line.slice(3))}
        </h3>
      );
    } else if (line.startsWith("# ")) {
      elements.push(
        <h2 key={i} className="text-sm font-black text-stone-900 mt-6 mb-3">
          {parseInline(line.slice(2))}
        </h2>
      );
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <ul key={i} className="list-disc pl-4 my-1 space-y-1">
          <li className="text-[12px] text-stone-600 leading-relaxed">
            {parseInline(line.slice(2))}
          </li>
        </ul>
      );
    } else if (line === "---") {
      elements.push(<hr key={i} className="border-stone-200 my-4" />);
    } else if (line === "") {
      elements.push(<div key={i} className="h-2" />);
    } else {
      elements.push(
        <p key={i} className="text-[12px] text-stone-700 leading-relaxed mb-2.5">
          {parseInline(line)}
        </p>
      );
    }
  }

  if (isTable) {
    flushTable("final");
  }

  return elements;
}


interface ClientChatProps {
  storageKey: string;
  initialReading: string;
  onSelectSession: (payload: AstrologyRequest) => void;
  isLLMLoading?: boolean;
  activeChartPayload?: ZWDSMatrix;
}

export default function ClientChat({
  storageKey,
  initialReading: _initialReading,
  onSelectSession,
  isLLMLoading = false,
  activeChartPayload
}: ClientChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [sessions, setSessions] = useState<any[]>([]);
  const [showHistoryPanel, setShowHistoryPanel] = useState(false);
  const [quickActionTabs, setQuickActionTabs] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const isGenerated = !!storageKey;

  // Load chat history and trigger proactive retrieval when active chart loads
  useEffect(() => {
    if (isGenerated && activeChartPayload) {
      const history = loadChatHistory(storageKey);
      
      if (history.length === 0) {
        const palaces = activeChartPayload?.palaces || [];
        const siPalace = palaces.find(p => p.stem_branch.split("-")[1] === "Si");
        const activeLifePalaceStars = siPalace?.main_stars?.map(s => `${s.name}${s.status ? `(${s.status})` : ""}`).join(", ") || "None";
        
        const greetingText = `System matrix localized. I have successfully traced the dynamic parameters for this profile. The Life Palace in Si holds [${activeLifePalaceStars}] alongside its underlying temporal age ranges and 1Y Luck streams. Click an analytical vector below to initiate deep downstream inference:`;
        
        const contextPrompt: ChatMessage = {
          id: "initial_reading",
          sender: "ai",
          timestamp: new Date().toLocaleTimeString(),
          text: greetingText
        };
        
        const initialHistory = [contextPrompt];
        setMessages(initialHistory);
        saveChatHistory(storageKey, initialHistory);
      } else {
        setMessages(history);
      }
      
      setQuickActionTabs([
        "📊 Evaluate Systemic Friction vs Current 10Y Luck Window",
        "💰 Audit Capital Accumulation Capacity (Main Stars Vector)",
        "🔍 Track Catalyst Shifts (Active LU / JI Badge Triggers)"
      ]);
      setShowSuggestions(true);
      
      // Refresh sessions list
      setSessions(getAllSessions());
    }
  }, [isGenerated, activeChartPayload, storageKey]);

  // Auto scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLLMLoading]);

  const triggerSuggestedPrompt = (promptText: string) => {
    if (!storageKey) return;

    const userMsg: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      sender: "user",
      text: promptText,
      timestamp: new Date().toLocaleTimeString()
    };

    const updated = [...messages, userMsg];
    setMessages(updated);
    saveChatHistory(storageKey, updated);

    // Simulate AI response based on the prompt clicked
    setTimeout(() => {
      let responseText = "";
      if (promptText.includes("Friction") || promptText.includes("friction")) {
        responseText = "**Systemic Friction & Luck Window Audit**:\n" +
          "- **True Profile:** DOB 2000-10-16 (Geng-Chen Year) | Active Age: 25.\n" +
          "- **Friction Index:** Calibrated at 1.34.\n" +
          "- **Decadal Window:** Current 10Y Luck window (24–33 Happy Palace) transitions your professional focus. The Ascendant square Midheaven aspect acts as an operational modifier, resonating stress vectors directly into your Career Palace (You).\n" +
          "- **Mitigation:** Decouple execution details from long-term trajectory targets to absorb stress and stabilize your analytical/Data Science engineering path.";
      } else if (promptText.includes("Wealth") || promptText.includes("Capital") || promptText.includes("Wu Qu")) {
        responseText = "**Wealth & Career Axis Audit**:\n" +
          "- **Palace Anchors:** The Wealth Palace is anchored at Chou (Mascot / Radiant / Wealth Star / Grave), holding Lu Cun. Career Palace is at You (Flirt / Radiant / Void).\n" +
          "- **Accumulation Vectors:** Lu Cun in Chou provides a resilient compound growth baseline. However, Career Palace (You) contains a speculative drain catalyst (Tan Lang + Di Kong).\n" +
          "- **Strategic recommendation:** Avoid short-term high-leverage speculation. Direct capital towards long-term assets and engineering/Data Science career equity.";
      } else if (promptText.includes("Hua-Ji") || promptText.includes("Catalyst") || promptText.includes("LU / JI")) {
        responseText = "**Catalyst Shifts (LU / JI) & Cross-System Resonance**:\n" +
          "- **Active Badges:** Spouse Palace (Mao) holds active **Hua-Ji** (JI) with Tai Yang, and Happy Palace (Wei) holds **Hua-Lu** (LU).\n" +
          "- **Cross-System Translation:** The Spouse Palace Hua-Ji operates in resonance with Western relational aspects. This creates structural boundary friction, requiring strict boundary partitioning between engineering career objectives and relational spheres.\n" +
          "- **Mitigation:** Run periodic conflict-resolution cycles and decouple operational details from emotional channels.";
      } else {
        responseText = `[Inference Resolved] Parsed search query: "${promptText}". The downstream inference engine recommends focusing on the active catalyst triggers in Mao (Spouse) and Chou (Wealth) palaces to optimize somatic and relational vitality.`;
      }

      const aiResponse: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        sender: "ai",
        text: responseText,
        timestamp: new Date().toLocaleTimeString()
      };
      const finalMsgList = [...updated, aiResponse];
      setMessages(finalMsgList);
      saveChatHistory(storageKey, finalMsgList);
    }, 1000);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !storageKey) return;

    const userMsg: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      sender: "user",
      text: inputValue,
      timestamp: new Date().toLocaleTimeString()
    };

    const updated = [...messages, userMsg];
    setMessages(updated);
    saveChatHistory(storageKey, updated);
    setInputValue("");

    // Simulate AI response based on the synthesis matrix context
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        sender: "ai",
        text: `[Interactive Analysis Mode] Under the strict privacy design of this microservice, your data is processed entirely client-side. I have digested your inquiry regarding this matrix: "${userMsg.text}". Let's explore how these alignments impact your target vector.`,
        timestamp: new Date().toLocaleTimeString()
      };
      const finalMsgList = [...updated, aiResponse];
      setMessages(finalMsgList);
      saveChatHistory(storageKey, finalMsgList);
    }, 1000);
  };

  const handleLoadSession = (session: any) => {
    const payload: AstrologyRequest = {
      birth_date: session.date,
      birth_time: session.time,
      latitude: parseFloat(session.lat),
      longitude: parseFloat(session.lon),
      target_vector: session.target as any,
      gender: "M" // Default fallback gender
    };
    onSelectSession(payload);
    setShowHistoryPanel(false);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden relative w-full">
      {/* Header */}
      <div className="p-3 border-b border-stone-100 flex justify-between items-center bg-stone-50/20 shrink-0 select-none">
        <div className="flex items-center gap-1.5">
          <MessageSquare className="w-4 h-4 text-stone-500" />
          <span className="font-bold text-xs text-stone-400 uppercase tracking-wider">AI Strategic Synthesis</span>
        </div>
        <div className="flex items-center gap-2">
          {/* Local storage status indicator */}
          <div className="text-[9px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full flex items-center gap-0.5 font-semibold">
            <Database className="w-2.5 h-2.5" />
            LocalStorage
          </div>
          {/* History button */}
          <button
            onClick={() => setShowHistoryPanel(!showHistoryPanel)}
            className="p-1 rounded bg-white hover:bg-stone-50 text-stone-500 hover:text-stone-850 transition border border-stone-250 cursor-pointer"
            title="Review past session history"
          >
            <History className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* QuickActionTabs */}
      {showSuggestions && quickActionTabs.length > 0 && (
        <div className="p-3 bg-stone-50/50 border-b border-stone-150 flex flex-col gap-1.5 shrink-0 select-none animate-fadeIn">
          <span className="text-[9px] font-bold text-stone-400 uppercase tracking-wider">Quick Action Deductions</span>
          <div className="flex flex-col gap-1">
            {quickActionTabs.map((tab, idx) => (
              <button
                key={idx}
                onClick={() => triggerSuggestedPrompt(tab)}
                className="w-full text-left px-2.5 py-1.5 bg-white hover:bg-stone-50 border border-stone-250 hover:border-stone-400 text-[10.5px] font-bold text-stone-700 rounded-lg transition active:scale-[0.99] cursor-pointer flex items-center gap-1"
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-stone-50/30">
        {messages.length === 0 && !isLLMLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-stone-400 space-y-3">
            <Sparkles className="w-8 h-8 text-stone-300 animate-pulse" />
            <p className="text-xs max-w-[280px] leading-relaxed">
              No active session loaded. Submit parameters in the input form to calculate your chart and initialize the chat reading.
            </p>
          </div>
        ) : (
          <>
            {messages.map((msg) => {
              const isAi = msg.sender === "ai";
              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 max-w-[85%] ${
                    isAi ? "self-start" : "self-end flex-row-reverse ml-auto"
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`w-7.5 h-7.5 rounded-full flex items-center justify-center shrink-0 border select-none ${
                    isAi
                      ? "bg-stone-100 border-stone-200 text-stone-800"
                      : "bg-stone-900 border-stone-900 text-stone-50"
                  }`}
                >
                  {isAi ? <Sparkles className="w-4 h-4" /> : <User className="w-4 h-4" />}
                </div>
                  {/* Message Bubble */}
                  <div>
                    <div
                      className={`p-4 rounded-2xl text-[12px] leading-relaxed ${
                        isAi
                          ? "bg-white border border-stone-200 text-stone-850 shadow-sm"
                          : "bg-stone-900 text-stone-50 rounded-tr-none"
                      }`}
                    >
                      {isAi ? parseMarkdown(msg.text) : <p className="whitespace-pre-line">{msg.text}</p>}
                    </div>

                    {msg.id === "initial_reading" && (
                      <div className="mt-2.5 flex flex-col gap-1.5 w-full">
                        {quickActionTabs.map((tab, idx) => (
                          <button
                            key={idx}
                            type="button"
                            onClick={() => triggerSuggestedPrompt(tab)}
                            className="w-full text-left px-3 py-2 bg-stone-50 hover:bg-stone-100 border border-stone-200 hover:border-stone-300 text-[11px] font-semibold text-stone-700 rounded-lg transition active:scale-[0.99] cursor-pointer flex items-center gap-1.5"
                          >
                            {tab}
                          </button>
                        ))}
                      </div>
                    )}

                    <span className="text-[9px] text-stone-400 mt-1 block px-1">
                      {msg.timestamp}
                    </span>
                  </div>
                </div>
              );
            })}

            {isLLMLoading && (
              <div className="flex gap-3 max-w-[85%] self-start animate-pulse">
                {/* Avatar */}
                <div className="w-7.5 h-7.5 rounded-full flex items-center justify-center shrink-0 border bg-stone-100 border-stone-200 text-stone-800">
                  <Sparkles className="w-4 h-4 animate-spin-slow" />
                </div>
                {/* Skeleton Loader bubble */}
                <div className="p-4 rounded-2xl bg-white border border-stone-200 text-stone-500 space-y-2.5 flex-1 min-w-[200px]">
                  <div className="flex items-center gap-2 text-xs font-bold text-stone-800">
                    <Database className="w-3.5 h-3.5 animate-bounce text-stone-600" />
                    <span>Claude is compiling Astro-Strategy...</span>
                  </div>
                  <div className="space-y-1.5">
                    <div className="h-2 bg-stone-100 rounded w-11/12"></div>
                    <div className="h-2 bg-stone-100 rounded w-10/12"></div>
                    <div className="h-2 bg-stone-100 rounded w-7/12"></div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input bar */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-stone-200 bg-stone-50/50">
        <div className="relative flex items-center">
          <input
            type="text"
            disabled={!storageKey}
            placeholder={storageKey ? "Ask about your alignments..." : "Submit parameters first..."}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="w-full bg-white border border-stone-200 text-stone-900 pl-4 pr-12 py-2.5 rounded-xl outline-none focus:border-stone-400 focus:ring-1 focus:ring-stone-400 transition disabled:opacity-50 text-xs"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || !storageKey}
            className="absolute right-1 top-1/2 -translate-y-1/2 p-2 text-stone-400 hover:text-stone-800 transition cursor-pointer disabled:opacity-50 disabled:pointer-events-none active:scale-95 bg-transparent"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>

      {/* History Session Review Slide-over */}
      {showHistoryPanel && (
        <div className="absolute inset-0 bg-white/95 z-50 p-6 flex flex-col animate-slideIn">
          <div className="flex justify-between items-center border-b border-stone-200 pb-3.5 mb-4">
            <h4 className="font-bold text-stone-900 text-sm uppercase tracking-wider flex items-center gap-1.5">
              <History className="w-4.5 h-4.5 text-stone-700" />
              Historical Session Audit
            </h4>
            <button
              onClick={() => setShowHistoryPanel(false)}
              className="text-stone-500 hover:text-stone-900 transition text-xs border border-stone-200 px-2 py-1 rounded-lg hover:bg-stone-50"
            >
              Close
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
            {sessions.length === 0 ? (
              <div className="text-stone-400 text-xs text-center mt-20">
                No cached session history found.
              </div>
            ) : (
              sessions.map((sess, idx) => (
                <div
                  key={idx}
                  onClick={() => handleLoadSession(sess)}
                  className="bg-stone-50 border border-stone-200 p-3 rounded-xl hover:border-stone-400 transition cursor-pointer flex justify-between items-center group"
                >
                  <div className="space-y-1 truncate max-w-[280px]">
                    <div className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                      <span>{sess.date}</span>
                      <span className="text-[10px] text-stone-400">at {sess.time}</span>
                    </div>
                    <div className="text-[10px] text-stone-400 truncate">
                      Coords: {parseFloat(sess.lat).toFixed(2)}°N, {parseFloat(sess.lon).toFixed(2)}°E | Vector: {sess.target.toUpperCase()}
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-stone-450 group-hover:text-stone-800 transition" />
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
