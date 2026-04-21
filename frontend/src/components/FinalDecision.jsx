import { Sparkles, ArrowRight } from "lucide-react";
import ConfidenceBadge from "./ConfidenceBadge";

export default function FinalDecision({ decision, confidence, keyReasons = [], recommendedAction }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-violet-500/30 bg-gradient-to-br from-[#14102a] via-surface-card to-surface-card p-6 animate-fade-in">
      {/* top accent line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/60 to-transparent" />

      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex items-center gap-2.5">
          <span className="p-2 rounded-xl bg-violet-500/15">
            <Sparkles size={15} className="text-violet-400" />
          </span>
          <span className="font-semibold text-white text-sm">Final Decision</span>
        </div>
        <ConfidenceBadge level={confidence} />
      </div>

      <p className="text-slate-200 text-sm leading-relaxed mb-5">{decision}</p>

      {keyReasons.length > 0 && (
        <div className="mb-5">
          <span className="label">Key reasons</span>
          <ul className="space-y-2">
            {keyReasons.map((r, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
                <span className="dot mt-[7px] bg-violet-400" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {recommendedAction && (
        <div className="flex items-start gap-3 p-3 bg-emerald-500/10 border border-emerald-500/25 rounded-xl">
          <ArrowRight size={14} className="text-emerald-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-emerald-500 mb-1">
              Recommended Action
            </p>
            <p className="text-sm text-emerald-200">{recommendedAction}</p>
          </div>
        </div>
      )}
    </div>
  );
}
