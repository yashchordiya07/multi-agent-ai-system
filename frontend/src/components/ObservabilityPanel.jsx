import { Activity, GitBranch, Clock, Zap } from "lucide-react";

function Row({ icon: Icon, label, value, valueClass = "text-slate-300" }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-surface-border last:border-0">
      <span className="flex items-center gap-2 text-xs text-slate-500">
        <Icon size={11} />{label}
      </span>
      <span className={`mono ${valueClass}`}>{value}</span>
    </div>
  );
}

export default function ObservabilityPanel({ meta }) {
  if (!meta) return null;

  const timings    = meta.timings_ms || {};
  const totalAgent = Object.values(timings).reduce((a, b) => a + b, 0);

  return (
    <div className="card border border-surface-border animate-slide-up">
      <span className="label flex items-center gap-1.5"><Activity size={10} />Observability</span>

      <div>
        <Row icon={Clock}    label="Pipeline total"       value={`${meta.pipeline_ms ?? "—"}ms`} valueClass="text-violet-300 mono" />
        <Row icon={Clock}    label="Agent work time"      value={`${totalAgent.toFixed(0)}ms`} />
        <Row icon={GitBranch} label="Iterations"          value={meta.iterations ?? 1}
             valueClass={meta.refinement_triggered ? "text-amber-300 mono" : "text-slate-300 mono"} />
        <Row icon={Zap}      label="Refinement triggered" value={meta.refinement_triggered ? "Yes" : "No"}
             valueClass={meta.refinement_triggered ? "text-amber-300" : "text-emerald-400"} />
        <Row icon={Zap}      label="Result source"        value={meta.cached ? "Cache hit" : "Live"}
             valueClass={meta.cached ? "text-blue-300" : "text-slate-400"} />
        <Row icon={GitBranch} label="Request ID"          value={meta.request_id || "—"} />
      </div>

      {/* per-agent timing bars */}
      <div className="mt-4 pt-3 border-t border-surface-border space-y-2">
        <span className="label">Per-agent latency</span>
        {Object.entries(timings).map(([k, v]) => (
          <div key={k} className="flex items-center gap-2">
            <span className="text-xs text-slate-600 w-36 truncate">{k.replace(/_/g, " ")}</span>
            <div className="flex-1 h-1.5 bg-surface rounded-full overflow-hidden">
              <div
                className="h-full bg-violet-500/50 rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, (v / (meta.pipeline_ms || 1)) * 100)}%` }}
              />
            </div>
            <span className="mono text-slate-400 w-16 text-right">{v}ms</span>
          </div>
        ))}
      </div>

      {meta.delta && (
        <div className="mt-3 pt-3 border-t border-surface-border">
          <span className="label">Analyst → Critic delta</span>
          <p className="text-xs text-slate-400 leading-relaxed">{meta.delta}</p>
        </div>
      )}
    </div>
  );
}
