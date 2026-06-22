'use client';
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { ZiweiChart, Palace } from '@/lib/ziwei/types';
import type { TimeView } from './TimeNav';
import { tStar, tPalace, tSiHua } from '@/lib/ziwei/i18n';

// Every reading must be returned in English.
const REPLY_IN_ENGLISH = 'Respond entirely in fluent English (you may keep a Chinese star name in parentheses on first mention). ';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  hidden?: boolean; // don't show user bubble for auto/topic messages
}

interface SelectedSiHua {
  starName: string;
  siHua: string;
  view: TimeView;
}

interface InsightPanelProps {
  chart: ZiweiChart;
  selectedPalace?: Palace | null;
  selectedSiHua?: SelectedSiHua | null;
}

const TOPICS = [
  { key: 'overview',     label: 'Overview' },
  { key: 'love',        label: 'Love' },
  { key: 'career',      label: 'Career' },
  { key: 'wealth',      label: 'Wealth' },
  { key: 'health',      label: 'Health' },
  { key: 'personality', label: 'Character' },
] as const;

const TOPIC_PROMPTS: Record<string, string> = {
  overview: REPLY_IN_ENGLISH + `Give an overview reading of this natal chart, grounded ONLY in the chart data. Structure:

**Core Pattern** — one sentence on the chart's defining structure and the person's temperament.
**Life Palace Stars** — the core traits of the Life Palace major star(s).
**Trine Alignment (三方四正)** — how the Wealth, Career, and Travel palaces interact.
**Current Decade** — the direction of the current 10-year luck period and what to watch.
**Strengths & Cautions** — innate gifts and the risks or lessons to be mindful of.`,

  love: REPLY_IN_ENGLISH + `Analyze love and marriage from this chart. Structure:

**Love Pattern** — one sentence characterizing the romantic fortune.
**Spouse Palace** — its major stars and four-transformations, read concretely.
**Trine Influence** — how related palaces affect relationships.
**Current Decade in Love** — the 10-year romantic trajectory and key moments.
**Practical Advice** — concrete, actionable relationship guidance.`,

  career: REPLY_IN_ENGLISH + `Analyze career from this chart. Structure:

**Career Pattern** — one sentence; better suited to employment or entrepreneurship.
**Career Palace** — its major stars and four-transformations.
**Wealth Linkage** — how income relates to career; where money comes from.
**Current Decade in Career** — the 10-year career trajectory.
**Practical Advice** — fitting directions, industries, and strategy.`,

  wealth: REPLY_IN_ENGLISH + `Analyze wealth from this chart. Structure:

**Wealth Pattern** — active income vs passive income.
**Wealth Palace** — its major stars and four-transformations; sources and flow of money.
**Property Palace (the treasury)** — savings capacity and real-estate fortune.
**Current Decade in Wealth** — the trajectory and cautions.
**Financial Advice** — concrete guidance.`,

  health: REPLY_IN_ENGLISH + `Analyze health from this chart. Structure:

**Health Palace Stars** — the stars in the Health palace and their bodily meaning.
**Main Risks** — the primary health vulnerabilities and body areas to watch.
**Decade Health Trend** — the current trend and key periods.
**Prevention** — concrete precautions and wellness directions.`,

  personality: REPLY_IN_ENGLISH + `Analyze character from this chart. Structure:

**Life Palace Character** — core personality from the Life Palace major star(s).
**Trine Character** — how the Wealth, Career, and Travel palaces shape the personality.
**Interpersonal Style** — how this person relates to and deals with others.
**Strengths & Life Lessons** — innate gifts and the lessons to face.`,
};

const PALACE_ROLES: Record<string, string> = {
  '命':   'self, character, innate pattern',
  '兄弟': 'siblings, partners',
  '夫妻': 'love, marriage',
  '子女': 'children, subordinates',
  '财帛': 'income sources, money flow',
  '疾厄': 'health, accidents',
  '迁移': 'opportunities abroad, social standing',
  '仆役': 'friends, benefactors, detractors',
  '交友': 'friends, benefactors, detractors',
  '官禄': 'career, social status',
  '田宅': 'property, home environment',
  '福德': 'inner fortune, peace of mind',
  '父母': 'parents, documents & contracts',
};

/** Render AI markdown: **【Title】** → gold header, **bold** → strong */
function AiContent({ text, streaming }: { text: string; streaming?: boolean }) {
  const lines = text.split('\n');
  return (
    <div className="space-y-0.5">
      {lines.map((line, i) => {
        const sectionMatch = line.match(/^\*\*【(.+?)】\*\*$/);
        if (sectionMatch) {
          return (
            <div key={i} className="pt-3 pb-0.5 first:pt-0">
              <span className="text-[11px] font-semibold tracking-wide" style={{ color: 'var(--t-gold)' }}>
                【{sectionMatch[1]}】
              </span>
            </div>
          );
        }
        if (line.trim() === '') return <div key={i} className="h-1" />;
        const parts = line.split(/\*\*(.+?)\*\*/);
        return (
          <div key={i} className="text-[11px] leading-relaxed" style={{ color: 'var(--t-text2)' }}>
            {parts.map((part, j) =>
              j % 2 === 0
                ? part
                : <strong key={j} className="font-medium" style={{ color: 'var(--t-text)' }}>{part}</strong>
            )}
          </div>
        );
      })}
      {streaming && (
        <span
          className="inline-block w-1.5 h-3 ml-0.5 animate-pulse rounded-sm align-middle"
          style={{ background: 'var(--t-gold)', opacity: 0.6 }}
        />
      )}
    </div>
  );
}

export default function InsightPanel({ chart, selectedPalace, selectedSiHua }: InsightPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTopic, setActiveTopic] = useState<string>('overview');
  const messagesRef = useRef<Message[]>([]); // always-current copy for closures
  const loadingRef = useRef(false);
  const autoLoaded = useRef(false);
  const lastPalaceBranch = useRef<number | undefined>(undefined);
  const lastSiHuaKey = useRef<string | undefined>(undefined);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Keep refs in sync
  useEffect(() => { messagesRef.current = messages; }, [messages]);
  useEffect(() => { loadingRef.current = loading; }, [loading]);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Auto-generate 命格总览 on mount
  useEffect(() => {
    if (autoLoaded.current) return;
    autoLoaded.current = true;
    sendMessage(TOPIC_PROMPTS.overview, true);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Inject palace analysis when palace selected
  useEffect(() => {
    if (!selectedPalace || selectedPalace.branch === lastPalaceBranch.current) return;
    lastPalaceBranch.current = selectedPalace.branch;

    const majorStars = selectedPalace.stars.filter(s => s.type === 'major');
    const starDesc = majorStars.length > 0
      ? majorStars.map(s => `${tStar(s.name)}${s.siHua ? ' (' + tSiHua(s.siHua) + ')' : ''}`).join(', ')
      : 'empty (borrows the opposite palace)';
    const palaceEn = tPalace(selectedPalace.name);
    const role = PALACE_ROLES[selectedPalace.name.replace(/宫$/, '')] ?? '';

    const prompt = REPLY_IN_ENGLISH + `Focus on the ${palaceEn} (governs: ${role}). Its major stars are: ${starDesc}. Structure:

**Palace Character** — what the ${palaceEn} means in this chart and the overall read of this star configuration.
**Major Star Reading** — how the star(s) behave in this palace.
**Trine Alignment** — how the trine palaces influence this one.
**Practical Advice** — concrete guidance based on this palace.`;

    sendMessage(prompt, true);
  }, [selectedPalace]); // eslint-disable-line react-hooks/exhaustive-deps

  // 注入四化飞化分析
  useEffect(() => {
    if (!selectedSiHua) return;
    const key = `${selectedSiHua.starName}-${selectedSiHua.siHua}-${selectedSiHua.view}`;
    if (key === lastSiHuaKey.current) return;
    lastSiHuaKey.current = key;

    // 找出该星所在宫位
    const palaceOfStar = chart.palaces.find(p =>
      p.stars.some(s => s.name === selectedSiHua.starName)
    );
    const palaceName = tPalace(palaceOfStar?.name ?? '');
    const viewLabel = selectedSiHua.view === 'daxian' ? 'Decade' : 'Year';
    const star = tStar(selectedSiHua.starName);
    const sh = tSiHua(selectedSiHua.siHua);

    const prompt = REPLY_IN_ENGLISH + `Analyze the ${viewLabel} transformation: ${star} → Hua ${sh}. Structure:

**Meaning of Hua ${sh}** — the core meaning of this transformation, and the specific meaning of ${star} turning Hua ${sh}.
**Palace It Lands On** — ${star} Hua ${sh} falls on the ${palaceName}; how that life domain is affected.
**Trine Pathway** — how Hua ${sh} in the ${palaceName} ripples to its opposite and two trine palaces.
**Effect on Current Luck** — under the ${viewLabel} time frame, the concrete near-term impact.
**Practical Advice** — concrete, actionable guidance from this transformation.`;

    sendMessage(prompt, true);
  }, [selectedSiHua]); // eslint-disable-line react-hooks/exhaustive-deps

  const streamResponse = async (apiMessages: { role: 'user' | 'assistant'; content: string }[]) => {
    try {
      const res = await fetch('/api/interpret', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chart, messages: apiMessages }),
      });
      if (!res.ok) throw new Error('Request failed');
      if (!res.body) throw new Error('No response stream');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = '';

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          const data = line.slice(6);
          if (data === '[DONE]') break;
          try {
            const delta = JSON.parse(data).delta?.text ?? '';
            assistantText += delta;
            setMessages(prev => {
              const updated = [...prev];
              updated[updated.length - 1] = { role: 'assistant', content: assistantText };
              return updated;
            });
          } catch { /* skip */ }
        }
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'The reading failed. Please try again.' }]);
    } finally {
      setLoading(false);
      loadingRef.current = false;
    }
  };

  const sendMessage = (text: string, hidden = false) => {
    if (!text.trim() || loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);

    const userMsg: Message = { role: 'user', content: text, hidden };
    // Capture current messages synchronously via ref (avoids stale closure)
    const apiMessages = [...messagesRef.current, userMsg].map(m => ({
      role: m.role,
      content: m.content,
    }));

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    streamResponse(apiMessages);
  };

  const handleTopicClick = (topicKey: string) => {
    if (loadingRef.current) return;
    setActiveTopic(topicKey);
    sendMessage(TOPIC_PROMPTS[topicKey], true);
  };

  const handleSend = () => {
    sendMessage(input);
  };

  return (
    <div className="flex flex-col h-full rounded-xl overflow-hidden card-glass">

      {/* ── Topic buttons ── */}
      <div className="flex-shrink-0 px-2 pt-2.5 pb-2" style={{ borderBottom: '1px solid var(--t-border)' }}>
        <div className="grid grid-cols-6 gap-1">
          {TOPICS.map(t => {
            const isActive = activeTopic === t.key;
            return (
              <button
                key={t.key}
                onClick={() => handleTopicClick(t.key)}
                disabled={loading}
                className="py-1.5 text-[10px] font-medium rounded-lg transition-all duration-150 disabled:opacity-40"
                style={{
                  background: isActive ? 'rgba(212,168,67,0.12)' : 'transparent',
                  border: `1px solid ${isActive ? 'rgba(212,168,67,0.3)' : 'var(--t-border)'}`,
                  color: isActive ? 'var(--t-gold)' : 'var(--t-faint)',
                }}
              >
                {t.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Messages ── */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">

        {/* Loading state before first message */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-4xl mb-3" style={{ color: 'var(--t-gold)', opacity: 0.1 }}>✦</div>
            <p className="text-[10px] animate-pulse" style={{ color: 'var(--t-faint)' }}>Generating your reading…</p>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg, i) => {
            if (msg.role === 'user' && msg.hidden) return null;

            if (msg.role === 'user') {
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-end"
                >
                  <div
                    className="max-w-[85%] rounded-xl px-3 py-2 text-[11px]"
                    style={{
                      background: 'rgba(212,168,67,0.08)',
                      border: '1px solid rgba(212,168,67,0.18)',
                      color: 'var(--t-gold)',
                    }}
                  >
                    {msg.content}
                  </div>
                </motion.div>
              );
            }

            // Assistant message
            const isLastMsg = i === messages.length - 1;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div
                  className="text-[9px] tracking-widest mb-2 flex items-center gap-1.5"
                  style={{ color: 'var(--t-faint)' }}
                >
                  <span style={{ color: 'var(--t-gold)', opacity: 0.4 }}>✦</span>
                  Astrology Reading
                </div>
                <AiContent text={msg.content} streaming={loading && isLastMsg} />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* ── Input ── */}
      <div className="flex-shrink-0 px-3 pb-3 pt-2" style={{ borderTop: '1px solid var(--t-border)' }}>
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Ask a follow-up, e.g. is this a good year to change jobs?"
            disabled={loading}
            className="flex-1 rounded-lg px-3 py-2 text-[11px] focus:outline-none transition-colors"
            style={{
              background: 'var(--t-card)',
              border: '1px solid var(--t-border)',
              color: 'var(--t-text)',
            }}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-3 py-2 rounded-lg text-[11px] font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            style={{
              background: 'rgba(212,168,67,0.15)',
              border: '1px solid rgba(212,168,67,0.25)',
              color: 'var(--t-gold)',
            }}
          >
            {loading ? '…' : 'Ask'}
          </button>
        </div>
      </div>

    </div>
  );
}
