export default function CaseSelector({ cases, selectedCase, onSelect, onResolve, isResolving }) {
  return (
    <section>
      <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
        Dispute Cases
      </h2>

      <div className="overflow-hidden rounded-lg border border-line bg-surface">
        {cases.map((c, i) => {
          const isSelected = selectedCase === c.case_name;
          return (
            <button
              key={c.case_id}
              onClick={() => onSelect(c.case_name)}
              className={`relative w-full cursor-pointer px-4 py-3.5 text-left transition-colors ${
                i > 0 ? "border-t border-line" : ""
              } ${isSelected ? "bg-brand/12" : "hover:bg-elevated"}`}
            >
              {isSelected && (
                <span className="absolute inset-y-0 left-0 w-[3px] bg-brand-accent" />
              )}

              <div className="mb-1.5 flex items-baseline justify-between gap-2">
                <span
                  className={`font-mono text-[11px] font-medium ${
                    isSelected ? "text-brand-accent" : "text-muted"
                  }`}
                >
                  {c.case_id}
                </span>
                <span className="text-[11px] text-muted">{c.date}</span>
              </div>

              <div className="mb-1 truncate text-sm font-semibold text-ink">
                {c.merchant}
              </div>

              <div className="flex items-baseline justify-between gap-2">
                <span className="text-[15px] font-semibold tabular-nums text-ink">
                  {c.currency} {c.amount.toLocaleString()}
                </span>
                <span className="text-[11px] text-muted">
                  {c.document_count} documents
                </span>
              </div>

              <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-muted">
                {c.claim_summary}
              </p>
            </button>
          );
        })}
      </div>

      {selectedCase && (
        <button
          onClick={onResolve}
          disabled={isResolving}
          className={`mt-3 w-full rounded-lg px-4 py-3 text-sm font-semibold text-white transition-colors ${
            isResolving
              ? "cursor-not-allowed bg-brand/40"
              : "cursor-pointer bg-brand hover:bg-brand-hover"
          }`}
        >
          {isResolving ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner />
              Adjudicating
            </span>
          ) : (
            "Resolve Dispute"
          )}
        </button>
      )}
    </section>
  );
}

function Spinner() {
  return (
    <svg className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" aria-hidden="true">
      <circle
        className="opacity-30"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
        fill="none"
      />
      <path
        fill="currentColor"
        d="M4 12a8 8 0 018-8V1C5.925 1 1 5.925 1 12h3z"
      />
    </svg>
  );
}
