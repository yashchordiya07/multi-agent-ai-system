import { AlertCircle, X } from "lucide-react";

export default function ErrorAlert({ message, onDismiss }) {
  return (
    <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/25 rounded-2xl animate-fade-in">
      <AlertCircle size={15} className="text-red-400 flex-shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-red-300">Request failed</p>
        <p className="text-xs text-red-400/80 mt-1 break-words">{message}</p>
        {message?.toLowerCase().includes("ollama") && (
          <p className="text-xs text-slate-500 mt-2">
            Make sure Ollama is running:{" "}
            <code className="font-mono bg-surface-raised px-1.5 py-0.5 rounded">ollama serve</code>
            {" "}and the model is pulled:{" "}
            <code className="font-mono bg-surface-raised px-1.5 py-0.5 rounded">ollama pull llama3:8b</code>
          </p>
        )}
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-600 hover:text-red-400 transition-colors flex-shrink-0">
          <X size={14} />
        </button>
      )}
    </div>
  );
}
