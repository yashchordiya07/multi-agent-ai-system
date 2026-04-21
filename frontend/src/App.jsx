import { useState, useRef, useCallback } from "react";
import {
  Search, BarChart2, Shield, Cpu, Send, Lightbulb,
  AlertTriangle, ChevronDown, Zap, Database,
} from "lucide-react";

import { submitQuery }        from "./api/client";
import AgentCard              from "./components/AgentCard";
import BulletList             from "./components/BulletList";
import FinalDecision          from "./components/FinalDecision";
import LoadingSkeleton        from "./components/LoadingSkeleton";
import PipelineBar            from "./components/PipelineBar";
import ObservabilityPanel     from "./components/ObservabilityPanel";
import ErrorAlert             from "./components/ErrorAlert";
import HistoryPanel           from "./components/HistoryPanel";
import ConfidenceBadge        from "./components/ConfidenceBadge";

/* ── Example queries ───────────────────────────────────────────────────── */
const EXAMPLES = [
  "Should a 5-person startup use microservices or a monolith?",
  "What are the trade-offs of PostgreSQL vs MongoDB for a social app?",
  "How should a remote team handle underperforming engineers?",
  "Is Python or Go better for a high-throughput API service?",
  "What are the risks of migrating to Kubernetes for a small team?",
];

/* ── Pipeline stage sequence for UX feedback ───────────────────────────── */
const STAGE_DELAYS = [
  [0,    "research"],
  [5000, "analyst"],
  [12000,"critic"],
];

export default function App() {
  const [query,        setQuery]        = useState("");
  const [context,      setContext]      = useState("");
  const [showCtx,      setShowCtx]      = useState(false);
  const [loading,      setLoading]      = useState(false);
  const [pipelineStage,setPipelineStage]= useState(null);
  const [result,       setResult]       = useState(null);
  const [error,        setError]        = useState(null);

  const textareaRef = useRef(null);
  const resultsRef  = useRef(null);
  const timersRef   = useRef([]);

  /* clear pending timers */
  const clearTimers = () => {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
  };

  const handleSubmit = useCallback(async (e) => {
    e?.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    clearTimers();

    /* advance pipeline indicator */
    STAGE_DELAYS.forEach(([delay, stage]) => {
      timersRef.current.push(
        setTimeout(() => setPipelineStage(stage), delay)
      );
    });

    try {
      const data = await submitQuery(query.trim(), context.trim());
      clearTimers();
      setPipelineStage("done");
      setResult(data);
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch (err) {
      clearTimers();
      setPipelineStage(null);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
      setTimeout(() => setPipelineStage(null), 1800);
    }
  }, [query, context, loading]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
  };

  const handleReplay = (q) => {
    setQuery(q);
    window.scrollTo({ top: 0, behavior: "smooth" });
    textareaRef.current?.focus();
  };

  /* ── Timings helpers ─────────────────────────────────────────────────── */
  const meta     = result?._meta || {};
  const timings  = meta.timings_ms || {};

  return (
    <div className="min-h-screen bg-surface text-slate-200">

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header className="border-b border-surface-border bg-surface-card/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="p-1.5 bg-brand/20 rounded-xl">
              <Cpu size={17} className="text-violet-400" />
            </span>
            <div>
              <h1 className="text-sm font-semibold text-white leading-tight">
                Multi-Agent Decision Engine
              </h1>
              <p className="text-[11px] text-slate-500 leading-tight">
                llama3:8b · Research → Analyst → Critic
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge badge-violet hidden sm:inline-flex">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse-slow" />
              Ollama local
            </span>
          </div>
        </div>
      </header>

      {/* ── Main grid ──────────────────────────────────────────────────── */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* ── LEFT: Input + sidebar ─────────────────────────────────── */}
          <aside className="lg:col-span-1 space-y-4">

            {/* Query input card */}
            <div className="card border border-surface-border space-y-4">
              <div>
                <label className="label">Your query</label>
                <textarea
                  ref={textareaRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a technical, strategic, or business question…"
                  rows={5}
                  disabled={loading}
                  className="w-full bg-surface border border-surface-border rounded-xl px-3 py-2.5
                    text-sm text-slate-100 placeholder-slate-700 resize-none
                    focus:border-brand/60 transition-all"
                />
              </div>

              {/* Optional context */}
              <div>
                <button
                  type="button"
                  onClick={() => setShowCtx((v) => !v)}
                  className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <ChevronDown size={12} className={`transition-transform ${showCtx ? "rotate-180" : ""}`} />
                  {showCtx ? "Hide" : "Add"} context
                </button>
                {showCtx && (
                  <textarea
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="Optional background info…"
                    rows={3}
                    disabled={loading}
                    className="mt-2 w-full bg-surface border border-surface-border rounded-xl px-3 py-2
                      text-sm text-slate-100 placeholder-slate-700 resize-none
                      focus:border-blue-500/40 transition-all"
                  />
                )}
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[11px] text-slate-700">⌘ Enter to run</span>
                <button
                  onClick={handleSubmit}
                  disabled={loading || !query.trim()}
                  className="flex items-center gap-2 px-4 py-2
                    bg-violet-600 hover:bg-violet-500
                    disabled:bg-surface-raised disabled:text-slate-600
                    text-white text-sm font-medium rounded-xl
                    transition-all focus:ring-2 focus:ring-brand/40"
                >
                  {loading
                    ? <><div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />Processing…</>
                    : <><Send size={13} />Run pipeline</>
                  }
                </button>
              </div>
            </div>

            {/* Examples */}
            <div className="card border border-surface-border space-y-1">
              <span className="label">Example queries</span>
              {EXAMPLES.map((q, i) => (
                <button
                  key={i}
                  onClick={() => { setQuery(q); textareaRef.current?.focus(); }}
                  className="w-full text-left text-xs text-slate-500 hover:text-slate-200
                    hover:bg-surface-raised px-2 py-1.5 rounded-lg transition-all"
                >
                  {q}
                </button>
              ))}
            </div>

            {/* History */}
            <HistoryPanel onReplay={handleReplay} />
          </aside>

          {/* ── RIGHT: Results ────────────────────────────────────────── */}
          <section className="lg:col-span-2 space-y-4" ref={resultsRef}>

            {/* Pipeline progress bar */}
            {(loading || pipelineStage === "done") && (
              <PipelineBar stage={pipelineStage} />
            )}

            {/* Error */}
            {error && (
              <ErrorAlert message={error} onDismiss={() => setError(null)} />
            )}

            {/* Skeleton while loading */}
            {loading && <LoadingSkeleton />}

            {/* Results */}
            {result && !loading && (
              <div className="space-y-4">

                {/* ─ Final Decision ─────────────────────────────────── */}
                <FinalDecision
                  decision={result.decision}
                  confidence={result.confidence}
                  keyReasons={result.key_reasons}
                  recommendedAction={result.recommended_action}
                />

                {/* ─ Research Agent ─────────────────────────────────── */}
                <AgentCard
                  title="Research Agent"
                  icon={Search}
                  iconBg="bg-blue-500/15"  iconColor="text-blue-400"
                  border="border-blue-500/20"
                  latencyMs={timings.research_ms}
                  badge={
                    <span className="badge badge-blue">
                      {result.research_output?.data_points?.length ?? 0} points
                    </span>
                  }
                >
                  <div>
                    <span className="label">Context summary</span>
                    <p className="text-sm text-slate-300 leading-relaxed">
                      {result.research_output?.context_summary}
                    </p>
                  </div>
                  <div>
                    <span className="label">Data points</span>
                    <BulletList items={result.research_output?.data_points} dotClass="bg-blue-400" />
                  </div>
                </AgentCard>

                {/* ─ Analyst Agent ──────────────────────────────────── */}
                <AgentCard
                  title="Analyst Agent"
                  icon={BarChart2}
                  iconBg="bg-violet-500/15"  iconColor="text-violet-400"
                  border="border-violet-500/20"
                  latencyMs={timings.analyst_iter1_ms}
                  badge={
                    <span className="badge badge-violet">
                      {result.analyst_output?.insights?.length ?? 0} insights
                    </span>
                  }
                >
                  <div>
                    <span className="label flex items-center gap-1.5"><Lightbulb size={10} />Insights</span>
                    <BulletList items={result.analyst_output?.insights} dotClass="bg-violet-400" />
                  </div>
                  <div>
                    <span className="label flex items-center gap-1.5"><AlertTriangle size={10} />Risks</span>
                    <BulletList items={result.analyst_output?.risks} dotClass="bg-amber-400" empty="No risks identified" />
                  </div>
                  <div className="p-3 bg-violet-500/10 border border-violet-500/20 rounded-xl">
                    <span className="text-[10px] font-semibold uppercase tracking-widest text-violet-400 block mb-1">
                      Recommendation
                    </span>
                    <p className="text-sm text-slate-200">{result.analyst_output?.recommendation}</p>
                  </div>
                </AgentCard>

                {/* ─ Critic Agent ───────────────────────────────────── */}
                <AgentCard
                  title="Critic Agent"
                  icon={Shield}
                  iconBg="bg-amber-500/15"  iconColor="text-amber-400"
                  border="border-amber-500/20"
                  latencyMs={timings.critic_iter1_ms}
                  badge={<ConfidenceBadge level={result.critic_output?.confidence_adjustment} />}
                >
                  {result.critic_output?.issues_identified?.length > 0 ? (
                    <div>
                      <span className="label flex items-center gap-1.5"><AlertTriangle size={10} />Issues identified</span>
                      <BulletList items={result.critic_output.issues_identified} dotClass="bg-red-400" />
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-sm text-emerald-400 p-3
                      bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                      <Shield size={14} />
                      No issues — analysis passed critic review
                    </div>
                  )}

                  <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                    <span className="text-[10px] font-semibold uppercase tracking-widest text-amber-400 block mb-1">
                      Final decision
                    </span>
                    <p className="text-sm text-slate-200 leading-relaxed">
                      {result.critic_output?.final_decision}
                    </p>
                  </div>

                  {meta.refinement_triggered && (
                    <div className="flex items-center gap-2 text-xs text-amber-500/80
                      bg-amber-500/5 border border-amber-500/15 rounded-xl px-3 py-2">
                      <Zap size={12} />
                      Refinement loop triggered — analyst ran {meta.iterations} iteration(s)
                    </div>
                  )}
                </AgentCard>

                {/* ─ Observability ──────────────────────────────────── */}
                <ObservabilityPanel meta={meta} />
              </div>
            )}

            {/* Empty state */}
            {!result && !loading && !error && (
              <div className="flex flex-col items-center justify-center py-24 text-center space-y-4">
                <div className="p-5 bg-surface-card rounded-2xl border border-surface-border">
                  <Cpu size={30} className="text-slate-700" />
                </div>
                <div>
                  <p className="text-slate-500 font-medium">Pipeline ready</p>
                  <p className="text-sm text-slate-700 mt-1">
                    Enter a query and click <em>Run pipeline</em>
                  </p>
                </div>
                <div className="flex items-center gap-5 pt-2">
                  {[
                    { Icon: Search,   label: "Research", color: "text-blue-500"   },
                    { Icon: BarChart2, label: "Analyst",  color: "text-violet-500" },
                    { Icon: Shield,   label: "Critic",   color: "text-amber-500"  },
                  ].map(({ Icon, label, color }) => (
                    <div key={label} className="flex items-center gap-1.5 text-xs text-slate-700">
                      <Icon size={12} className={color} />{label}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
