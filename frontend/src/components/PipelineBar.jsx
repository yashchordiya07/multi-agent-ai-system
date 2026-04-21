import { Search, BarChart2, Shield, CheckCircle2, Loader2 } from "lucide-react";

const STAGES = [
  { key: "research", label: "Research", Icon: Search    },
  { key: "analyst",  label: "Analyst",  Icon: BarChart2 },
  { key: "critic",   label: "Critic",   Icon: Shield    },
  { key: "done",     label: "Done",     Icon: CheckCircle2 },
];

export default function PipelineBar({ stage }) {
  if (!stage) return null;
  const idx = STAGES.findIndex((s) => s.key === stage);

  return (
    <div className="card border border-surface-border py-4 animate-fade-in">
      <div className="flex items-center relative">
        {/* connector line */}
        <div className="absolute left-[10%] right-[10%] top-4 h-px bg-surface-border z-0" />

        {STAGES.map((s, i) => {
          const done   = i < idx;
          const active = i === idx;
          return (
            <div key={s.key} className="flex-1 flex flex-col items-center gap-1.5 z-10">
              <div className={[
                "w-8 h-8 rounded-full border flex items-center justify-center transition-all duration-300",
                done   ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-400" : "",
                active ? "bg-brand/20 border-brand/60 text-violet-300 shadow-lg shadow-brand/20" : "",
                !done && !active ? "bg-surface-card border-surface-border text-slate-700" : "",
              ].join(" ")}>
                {active
                  ? <Loader2 size={14} className="animate-spin" />
                  : <s.Icon size={14} />
                }
              </div>
              <span className={`text-[11px] font-medium transition-colors ${
                active ? "text-violet-300" : done ? "text-emerald-400" : "text-slate-700"
              }`}>
                {s.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
