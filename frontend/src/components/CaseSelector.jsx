export default function CaseSelector({ cases, selectedCase, onSelect, onResolve, isResolving }) {
  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">
        Dispute Cases
      </h2>
      {cases.map((c) => {
        const isSelected = selectedCase === c.case_name;
        return (
          <button
            key={c.case_id}
            onClick={() => onSelect(c.case_name)}
            className={`w-full text-left rounded-xl p-4 transition-all duration-200 border cursor-pointer ${
              isSelected
                ? "border-[#006FCF] bg-[#006FCF]/10 shadow-[0_0_20px_rgba(0,111,207,0.15)]"
                : "border-white/5 bg-[#14141f] hover:border-white/10 hover:bg-[#1e1e2e]"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-mono text-[#006FCF]">{c.case_id}</span>
              <span className="text-xs text-slate-500">{c.date}</span>
            </div>
            <div className="text-sm font-medium text-slate-200 mb-1">{c.merchant}</div>
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold text-white">
                {c.currency} {c.amount.toLocaleString()}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-md bg-white/5 text-slate-400">
                {c.document_count} docs
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-2 line-clamp-2">{c.claim_summary}</p>
          </button>
        );
      })}

      {selectedCase && (
        <button
          onClick={onResolve}
          disabled={isResolving}
          className={`w-full mt-4 py-3 px-4 rounded-xl font-semibold text-sm transition-all duration-200 cursor-pointer ${
            isResolving
              ? "bg-[#006FCF]/30 text-[#006FCF]/60 cursor-not-allowed"
              : "bg-[#006FCF] text-white hover:bg-[#0082ff] shadow-[0_0_20px_rgba(0,111,207,0.3)]"
          }`}
        >
          {isResolving ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Resolving...
            </span>
          ) : (
            "⚡ Resolve Dispute"
          )}
        </button>
      )}
    </div>
  );
}
