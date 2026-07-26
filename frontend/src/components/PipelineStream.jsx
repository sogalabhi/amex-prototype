const STAGE_CONFIG = {
  classified: { label: "Classification", icon: "🏷️" },
  facts_extracted: { label: "Evidence Analysis", icon: "🔍" },
  rules_fired: { label: "Rules Engine", icon: "⚖️" },
  verdict: { label: "Verdict", icon: "📋" },
  memo: { label: "Decision Memo", icon: "📝" },
  ledger: { label: "Audit Trail", icon: "🔗" },
};

const VERDICT_STYLES = {
  CARDMEMBER: {
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    text: "text-emerald-400",
    label: "CARDMEMBER WINS",
    glow: "shadow-[0_0_30px_rgba(34,197,94,0.2)]",
  },
  MERCHANT: {
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    text: "text-amber-400",
    label: "MERCHANT WINS",
    glow: "shadow-[0_0_30px_rgba(245,158,11,0.2)]",
  },
  ESCALATE_HUMAN_REVIEW: {
    bg: "bg-purple-500/10",
    border: "border-purple-500/30",
    text: "text-purple-400",
    label: "ESCALATED TO HUMAN REVIEW",
    glow: "shadow-[0_0_30px_rgba(168,85,247,0.2)]",
  },
};

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4 text-[#006FCF]" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

function StageHeader({ stage, isActive, isComplete, elapsedMs }) {
  const config = STAGE_CONFIG[stage] || { label: stage, icon: "⚙️" };
  return (
    <div className="flex items-center gap-3 mb-3">
      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs transition-all duration-500 ${
        isComplete ? "bg-emerald-500/20 text-emerald-400" : isActive ? "bg-[#006FCF]/20" : "bg-white/5 text-slate-600"
      }`}>
        {isComplete ? "✓" : isActive ? <Spinner /> : config.icon}
      </div>
      <span className={`text-sm font-medium ${isComplete || isActive ? "text-slate-200" : "text-slate-600"}`}>
        {config.label}
      </span>
      {elapsedMs !== undefined && (
        <span className="text-xs text-slate-600 ml-auto font-mono">{(elapsedMs / 1000).toFixed(1)}s</span>
      )}
    </div>
  );
}

function ConfidenceBar({ confidence, verdict }) {
  const style = VERDICT_STYLES[verdict] || VERDICT_STYLES.ESCALATE_HUMAN_REVIEW;
  const pct = Math.round(confidence * 100);
  return (
    <div className="mt-3">
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-500">Confidence</span>
        <span className={style.text}>{pct}%</span>
      </div>
      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-1000 ease-out ${
            verdict === "CARDMEMBER" ? "bg-emerald-500" :
            verdict === "MERCHANT" ? "bg-amber-500" : "bg-purple-500"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function PipelineStream({ events, isResolving, totalElapsed }) {
  if (!isResolving && Object.keys(events).length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-slate-600 text-sm">
        Click "Resolve Dispute" to start the pipeline
      </div>
    );
  }

  const stages = ["classified", "facts_extracted", "rules_fired", "verdict", "memo", "ledger"];
  const completedStages = new Set(Object.keys(events));
  const currentStageIdx = stages.findIndex((s) => !completedStages.has(s));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Resolution Pipeline
        </h2>
        {totalElapsed && (
          <span className="text-xs px-3 py-1 rounded-full bg-[#006FCF]/10 text-[#006FCF] font-semibold">
            Resolved in {(totalElapsed / 1000).toFixed(1)}s
          </span>
        )}
      </div>

      {/* Classification */}
      <div className={`rounded-xl border p-4 transition-all duration-500 ${
        events.classified ? "border-white/10 bg-[#14141f]" : "border-white/5 bg-[#14141f]/50"
      }`}>
        <StageHeader
          stage="classified"
          isActive={isResolving && currentStageIdx === 0}
          isComplete={!!events.classified}
          elapsedMs={events.classified?.elapsed_ms}
        />
        {events.classified && (
          <div className="ml-9 animate-in fade-in">
            <div className="flex items-center gap-2">
              <span className="text-xs px-2 py-1 rounded-md bg-[#006FCF]/20 text-[#006FCF] font-mono font-bold">
                {events.classified.reason_code}
              </span>
              <span className="text-sm text-slate-300">{events.classified.justification}</span>
            </div>
          </div>
        )}
      </div>

      {/* Facts Extracted */}
      <div className={`rounded-xl border p-4 transition-all duration-500 ${
        events.facts_extracted ? "border-white/10 bg-[#14141f]" : "border-white/5 bg-[#14141f]/50"
      }`}>
        <StageHeader
          stage="facts_extracted"
          isActive={isResolving && currentStageIdx === 1}
          isComplete={!!events.facts_extracted}
          elapsedMs={events.facts_extracted?.elapsed_ms}
        />
        {events.facts_extracted && (
          <div className="ml-9 space-y-2 animate-in fade-in">
            <div className="text-xs text-slate-500 mb-2">
              {events.facts_extracted.atomic_facts?.length || 0} atomic +{" "}
              {events.facts_extracted.derived_facts?.length || 0} derived facts
            </div>
            <div className="grid gap-1.5 max-h-48 overflow-y-auto pr-2">
              {events.facts_extracted.atomic_facts?.map((f, i) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <span className="px-1.5 py-0.5 rounded bg-white/5 text-slate-500 font-mono shrink-0">
                    {f.source_doc}
                  </span>
                  <span className="text-slate-400">{f.fact_type}:</span>
                  <span className="text-slate-200 truncate">{JSON.stringify(f.value)}</span>
                </div>
              ))}
              {events.facts_extracted.derived_facts?.map((f, i) => (
                <div key={`d-${i}`} className="flex items-start gap-2 text-xs">
                  <span className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-mono shrink-0">
                    DERIVED
                  </span>
                  <span className="text-slate-400">{f.fact_type}:</span>
                  <span className="text-slate-200 truncate">{JSON.stringify(f.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Rules Fired */}
      <div className={`rounded-xl border p-4 transition-all duration-500 ${
        events.rules_fired ? "border-white/10 bg-[#14141f]" : "border-white/5 bg-[#14141f]/50"
      }`}>
        <StageHeader
          stage="rules_fired"
          isActive={isResolving && currentStageIdx === 2}
          isComplete={!!events.rules_fired}
          elapsedMs={events.rules_fired?.elapsed_ms}
        />
        {events.rules_fired && (
          <div className="ml-9 space-y-2 animate-in fade-in">
            {events.rules_fired.fired_rules?.map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="font-mono text-slate-300 w-20">{r.rule_id}</span>
                <span className={`font-mono font-bold w-14 text-right ${
                  r.weight < 0 ? "text-amber-400" : "text-emerald-400"
                }`}>
                  {r.weight > 0 ? "+" : ""}{r.weight.toFixed(2)}
                </span>
                <span className="text-slate-500 truncate">{r.rulebook_text?.slice(0, 60)}</span>
              </div>
            ))}
            {events.rules_fired.defeated_rules?.map((r, i) => (
              <div key={`def-${i}`} className="flex items-center gap-2 text-xs opacity-60">
                <span className="font-mono text-red-400 w-20 line-through">{r.rule_id}</span>
                <span className="font-mono text-red-400/60 w-14 text-right line-through">
                  {r.original_weight > 0 ? "+" : ""}{r.original_weight.toFixed(2)}
                </span>
                <span className="text-red-400/60 text-xs">DEFEATED</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Verdict */}
      {events.verdict && (() => {
        const style = VERDICT_STYLES[events.verdict.verdict] || VERDICT_STYLES.ESCALATE_HUMAN_REVIEW;
        return (
          <div className={`rounded-xl border p-6 transition-all duration-700 ${style.border} ${style.bg} ${style.glow}`}>
            <div className="text-center">
              <div className={`text-2xl font-bold mb-1 ${style.text}`}>
                {style.label}
              </div>
              <div className="text-xs text-slate-500">
                Reason Code {events.verdict.reason_code}
              </div>
              <ConfidenceBar
                confidence={events.verdict.confidence}
                verdict={events.verdict.verdict}
              />
            </div>
          </div>
        );
      })()}
    </div>
  );
}
