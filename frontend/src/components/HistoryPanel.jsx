import { useState, useEffect } from "react";
import { History, Trash2, RefreshCw, ChevronRight } from "lucide-react";
import { fetchMemory, clearMemory } from "../api/client";
import ConfidenceBadge from "./ConfidenceBadge";

export default function HistoryPanel({ onReplay }) {
  const [entries, setEntries] = useState([]);
  const [open,    setOpen]    = useState(false);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const d = await fetchMemory();
      setEntries((d.entries || []).slice(0, 20));
    } catch { setEntries([]); }
    finally  { setLoading(false); }
  };

  const handleClear = async () => { await clearMemory(); setEntries([]); };

  useEffect(() => { if (open) load(); }, [open]);

  return (
    <div className="card border border-surface-border">
      <button onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between group">
        <span className="flex items-center gap-2 text-sm text-slate-400 group-hover:text-slate-200 transition-colors">
          <History size={14} /> Query history
        </span>
        <div className="flex items-center gap-2">
          {entries.length > 0 && <span className="badge badge-slate">{entries.length}</span>}
          <ChevronRight size={13} className={`text-slate-600 transition-transform ${open ? "rotate-90" : ""}`} />
        </div>
      </button>

      {open && (
        <div className="mt-4 space-y-3 animate-fade-in">
          <div className="flex items-center justify-between">
            <button onClick={load} disabled={loading}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors">
              <RefreshCw size={11} className={loading ? "animate-spin" : ""} /> Refresh
            </button>
            {entries.length > 0 && (
              <button onClick={handleClear}
                className="flex items-center gap-1.5 text-xs text-red-600 hover:text-red-400 transition-colors">
                <Trash2 size={11} /> Clear all
              </button>
            )}
          </div>

          {entries.length === 0
            ? <p className="text-xs text-slate-700 italic text-center py-3">No history yet</p>
            : (
              <ul className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                {entries.map((e, i) => (
                  <li key={i} onClick={() => onReplay?.(e.query)}
                    className="p-3 rounded-xl bg-surface hover:bg-surface-raised border border-transparent hover:border-surface-border transition-all cursor-pointer">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed flex-1">{e.query}</p>
                      <ConfidenceBadge level={e.confidence} />
                    </div>
                    <div className="flex gap-3 mt-1.5">
                      <span className="text-[10px] text-slate-600">{e.timestamp?.slice(0, 16).replace("T", " ")}</span>
                      {e.refinement_triggered && <span className="text-[10px] text-amber-600">refined</span>}
                      {e.pipeline_ms > 0 && <span className="text-[10px] mono text-slate-700">{e.pipeline_ms}ms</span>}
                    </div>
                  </li>
                ))}
              </ul>
            )
          }
        </div>
      )}
    </div>
  );
}
