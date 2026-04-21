import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

export default function AgentCard({
  title, icon: Icon, iconBg, iconColor,
  border, badge, latencyMs, children, defaultOpen = true,
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`card border ${border} animate-slide-up`}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-3 group"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className={`p-2 rounded-xl ${iconBg} flex-shrink-0`}>
            <Icon size={15} className={iconColor} />
          </span>
          <span className="font-semibold text-slate-100 text-sm">{title}</span>
          {badge}
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          {latencyMs != null && (
            <span className="mono text-slate-600 hidden sm:block">{latencyMs}ms</span>
          )}
          {open
            ? <ChevronDown  size={14} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
            : <ChevronRight size={14} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
          }
        </div>
      </button>

      {open && <div className="mt-4 space-y-4">{children}</div>}
    </div>
  );
}
