const STAGES = ["classified", "facts_extracted", "rules_fired", "verdict", "memo", "ledger"];

const STAGE_LABELS = {
  classified: "Reason Code Classification",
  facts_extracted: "Evidence Analysis",
  rules_fired: "Rulebook Engine",
  verdict: "Verdict",
  memo: "Decision Memo",
  ledger: "Audit Trail",
};

// Outcome is encoded by fill weight rather than hue: the cardmember result carries
// solid Amex blue, the merchant result a deep navy, and an escalation stays unfilled.
const VERDICT_STYLES = {
  CARDMEMBER: {
    label: "Resolved in Favor of Cardmember",
    panel: "border-brand bg-brand text-white",
    sub: "text-white/70",
    track: "bg-white/25",
    fill: "bg-white",
  },
  MERCHANT: {
    label: "Resolved in Favor of Merchant",
    panel: "border-brand/40 bg-navy text-ink",
    sub: "text-brand-accent/80",
    track: "bg-white/12",
    fill: "bg-brand-accent",
  },
  ESCALATE_HUMAN_REVIEW: {
    label: "Escalated for Human Review",
    panel: "border-line bg-surface text-ink",
    sub: "text-muted",
    track: "bg-elevated",
    fill: "bg-muted",
  },
};

function Spinner() {
  return (
    <svg
      className="h-3.5 w-3.5 animate-spin text-brand-accent"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
        fill="none"
      />
      <path fill="currentColor" d="M4 12a8 8 0 018-8V1C5.925 1 1 5.925 1 12h3z" />
    </svg>
  );
}

function StageHeader({ stage, index, isActive, isComplete, elapsedMs }) {
  return (
    <div className="flex items-center gap-3">
      <span
        className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[10px] font-semibold tabular-nums transition-colors ${
          isComplete
            ? "border-brand bg-brand text-white"
            : isActive
              ? "border-brand-accent bg-surface"
              : "border-line bg-surface text-muted"
        }`}
      >
        {isComplete ? <Check /> : isActive ? <Spinner /> : String(index + 1).padStart(2, "0")}
      </span>

      <span
        className={`text-[13px] font-semibold ${
          isComplete || isActive ? "text-ink" : "text-muted"
        }`}
      >
        {STAGE_LABELS[stage]}
      </span>

      {elapsedMs !== undefined && (
        <span className="ml-auto font-mono text-[11px] tabular-nums text-muted">
          {(elapsedMs / 1000).toFixed(1)}s
        </span>
      )}
    </div>
  );
}

function Check() {
  return (
    <svg className="h-3 w-3" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path
        d="M2.5 6.2l2.3 2.3L9.5 3.8"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function StageCard({ stage, index, isActive, isComplete, elapsedMs, children }) {
  return (
    <div
      className={`rounded-lg border bg-surface p-4 transition-colors ${
        isComplete || isActive ? "border-line" : "border-line/50"
      }`}
    >
      <StageHeader
        stage={stage}
        index={index}
        isActive={isActive}
        isComplete={isComplete}
        elapsedMs={elapsedMs}
      />
      {children && <div className="animate-in mt-3 pl-9">{children}</div>}
    </div>
  );
}

function ConfidenceBar({ confidence, style }) {
  const pct = Math.round(confidence * 100);
  return (
    <div className="mt-4">
      <div className="mb-1.5 flex items-baseline justify-between text-[11px]">
        <span className={`uppercase tracking-[0.12em] ${style.sub}`}>Confidence</span>
        <span className="font-mono font-semibold tabular-nums">{pct}%</span>
      </div>
      <div className={`h-1 overflow-hidden rounded-full ${style.track}`}>
        <div
          className={`h-full rounded-full transition-all duration-1000 ease-out ${style.fill}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function PipelineStream({ events, isResolving, totalElapsed }) {
  if (!isResolving && Object.keys(events).length === 0) {
    return (
      <section>
        <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
          Resolution Pipeline
        </h2>
        <div className="rounded-lg border border-dashed border-line px-6 py-16 text-center">
          <p className="text-[13px] font-medium text-ink">No active adjudication</p>
          <p className="mt-1 text-xs text-muted">
            Select a dispute case and choose Resolve Dispute to begin.
          </p>
        </div>
      </section>
    );
  }

  const completed = new Set(Object.keys(events));
  const currentIdx = STAGES.findIndex((s) => !completed.has(s));
  const verdictStyle =
    VERDICT_STYLES[events.verdict?.verdict] || VERDICT_STYLES.ESCALATE_HUMAN_REVIEW;

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
          Resolution Pipeline
        </h2>
        {totalElapsed && (
          <span className="font-mono text-[11px] font-medium tabular-nums text-brand-accent">
            Completed in {(totalElapsed / 1000).toFixed(1)}s
          </span>
        )}
      </div>

      <div className="space-y-2.5">
        {/* 01 — Classification */}
        <StageCard
          stage="classified"
          index={0}
          isActive={isResolving && currentIdx === 0}
          isComplete={!!events.classified}
          elapsedMs={events.classified?.elapsed_ms}
        >
          {events.classified && (
            <div className="flex items-start gap-2.5">
              <span className="shrink-0 rounded border border-brand-accent/30 bg-brand/12 px-1.5 py-0.5 font-mono text-[11px] font-semibold text-brand-accent">
                {events.classified.reason_code}
              </span>
              <span className="text-[13px] leading-relaxed text-ink">
                {events.classified.justification}
              </span>
            </div>
          )}
        </StageCard>

        {/* 02 — Evidence analysis */}
        <StageCard
          stage="facts_extracted"
          index={1}
          isActive={isResolving && currentIdx === 1}
          isComplete={!!events.facts_extracted}
          elapsedMs={events.facts_extracted?.elapsed_ms}
        >
          {events.facts_extracted && (
            <>
              <div className="mb-2 text-[11px] text-muted">
                {events.facts_extracted.atomic_facts?.length || 0} atomic ·{" "}
                {events.facts_extracted.derived_facts?.length || 0} derived
              </div>
              <div className="max-h-52 space-y-1 overflow-y-auto pr-2">
                {events.facts_extracted.atomic_facts?.map((f, i) => (
                  <FactRow key={i} source={f.source_doc} type={f.fact_type} value={f.value} />
                ))}
                {events.facts_extracted.derived_facts?.map((f, i) => (
                  <FactRow
                    key={`d-${i}`}
                    source="DERIVED"
                    type={f.fact_type}
                    value={f.value}
                    emphasis
                  />
                ))}
              </div>
            </>
          )}
        </StageCard>

        {/* 03 — Rulebook */}
        <StageCard
          stage="rules_fired"
          index={2}
          isActive={isResolving && currentIdx === 2}
          isComplete={!!events.rules_fired}
          elapsedMs={events.rules_fired?.elapsed_ms}
        >
          {events.rules_fired && (
            <div className="space-y-1">
              {events.rules_fired.fired_rules?.map((r, i) => (
                <div key={i} className="flex items-baseline gap-3 text-[11px]">
                  <span className="w-20 shrink-0 font-mono font-medium text-ink">
                    {r.rule_id}
                  </span>
                  <span
                    className={`w-12 shrink-0 text-right font-mono font-semibold tabular-nums ${
                      r.weight < 0 ? "text-negative" : "text-brand-accent"
                    }`}
                  >
                    {r.weight > 0 ? "+" : ""}
                    {r.weight.toFixed(2)}
                  </span>
                  <span className="truncate text-muted">{r.rulebook_text}</span>
                </div>
              ))}

              {events.rules_fired.defeated_rules?.map((r, i) => (
                <div key={`def-${i}`} className="flex items-baseline gap-3 text-[11px]">
                  <span className="w-20 shrink-0 font-mono font-medium text-muted line-through">
                    {r.rule_id}
                  </span>
                  <span className="w-12 shrink-0 text-right font-mono tabular-nums text-muted line-through">
                    {r.original_weight > 0 ? "+" : ""}
                    {r.original_weight.toFixed(2)}
                  </span>
                  <span className="font-medium uppercase tracking-wide text-negative">
                    Defeated
                  </span>
                </div>
              ))}
            </div>
          )}
        </StageCard>

        {/* 04 — Verdict */}
        {events.verdict && (
          <div
            className={`animate-in rounded-lg border p-6 transition-colors ${verdictStyle.panel}`}
          >
            <div className={`text-[11px] uppercase tracking-[0.12em] ${verdictStyle.sub}`}>
              Reason Code {events.verdict.reason_code}
            </div>
            <div className="mt-1.5 text-xl font-semibold tracking-tight">
              {verdictStyle.label}
            </div>
            <ConfidenceBar confidence={events.verdict.confidence} style={verdictStyle} />
          </div>
        )}
      </div>
    </section>
  );
}

function FactRow({ source, type, value, emphasis }) {
  return (
    <div className="flex items-baseline gap-2 text-[11px]">
      <span
        className={`shrink-0 rounded border px-1.5 py-px font-mono text-[10px] ${
          emphasis
            ? "border-brand-accent/30 bg-brand/12 font-semibold text-brand-accent"
            : "border-line bg-elevated text-muted"
        }`}
      >
        {source}
      </span>
      <span className="shrink-0 text-muted">{type}</span>
      <span className="truncate font-mono text-ink">{JSON.stringify(value)}</span>
    </div>
  );
}
