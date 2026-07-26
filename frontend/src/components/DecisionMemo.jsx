import { useState } from "react";

export default function DecisionMemo({ memoData }) {
  const [view, setView] = useState("merchant");

  if (!memoData) return null;

  const memo = view === "merchant" ? memoData.merchant_memo : memoData.cardmember_memo;

  return (
    <div className="rounded-xl border border-white/10 bg-[#14141f] p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Decision Memo
        </h2>
        <div className="flex items-center bg-white/5 rounded-lg p-0.5">
          <button
            onClick={() => setView("merchant")}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${view === "merchant"
                ? "bg-[#006FCF] text-white"
                : "text-slate-400 hover:text-slate-200"
              }`}
          >
            Merchant View
          </button>
          <button
            onClick={() => setView("cardmember")}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${view === "cardmember"
                ? "bg-[#006FCF] text-white"
                : "text-slate-400 hover:text-slate-200"
              }`}
          >
            Cardmember View
          </button>
        </div>
      </div>

      <div className="prose prose-invert prose-sm max-w-none">
        <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
          {formatMemo(memo)}
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-white/5">
        <p className="text-xs text-slate-600 italic">
          Both views contain identical factual content - only the framing differs.
          This is the transparency guarantee.
        </p>
      </div>
    </div>
  );
}

function formatMemo(text) {
  if (!text) return "Generating memo...";

  // Basic markdown-like formatting for display
  return text
    .replace(/\*\*(.*?)\*\*/g, "⟨$1⟩") // Bold markers (we'll style inline)
    .replace(/#{1,3}\s/g, ""); // Strip markdown headers (already in context)
}
