import { useState } from "react";

const VIEWS = [
  { id: "merchant", label: "Merchant" },
  { id: "cardmember", label: "Cardmember" },
];

export default function DecisionMemo({ memoData }) {
  const [view, setView] = useState("merchant");

  if (!memoData) return null;

  const memo = view === "merchant" ? memoData.merchant_memo : memoData.cardmember_memo;

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
          Decision Memo
        </h2>

        {/* Segmented control */}
        <div className="flex overflow-hidden rounded-md border border-line bg-surface">
          {VIEWS.map((v, i) => (
            <button
              key={v.id}
              onClick={() => setView(v.id)}
              aria-pressed={view === v.id}
              className={`cursor-pointer px-3 py-1.5 text-[11px] font-semibold transition-colors ${
                i > 0 ? "border-l border-line" : ""
              } ${
                view === v.id
                  ? "bg-brand text-white"
                  : "text-muted hover:bg-elevated hover:text-ink"
              }`}
            >
              {v.label}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-line bg-surface p-6">
        <div className="text-[13px] leading-[1.75] text-muted">
          {memo ? renderMemo(memo) : <span>Generating memo…</span>}
        </div>

        <p className="mt-5 border-t border-line pt-4 text-[11px] leading-relaxed text-muted">
          Both views state identical facts and cite the same rules — only the framing
          differs. This is the platform's transparency guarantee.
        </p>
      </div>
    </section>
  );
}

// Renders the memo's light markdown: `## headings` become section labels and
// `**bold**` spans are emphasised against the body text.
function renderMemo(rawText) {
  const text = typeof rawText === "string" ? rawText : (rawText ? JSON.stringify(rawText, null, 2) : "");
  return text
    .split(/\n{2,}/)
    .filter((block) => block.trim())
    .map((block, i) => {
      const heading = block.match(/^#{1,3}\s+(.*)$/m);
      if (heading && block.trim().startsWith("#")) {
        return (
          <h3
            key={i}
            className="mt-5 mb-1.5 text-[11px] font-semibold uppercase tracking-[0.12em] text-brand-accent first:mt-0"
          >
            {heading[1]}
          </h3>
        );
      }
      return (
        <p key={i} className="mt-3 whitespace-pre-wrap first:mt-0">
          {renderInline(block.replace(/^#{1,3}\s+/gm, ""))}
        </p>
      );
    });
}

function renderInline(rawText) {
  const text = typeof rawText === "string" ? rawText : (rawText ? String(rawText) : "");
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i} className="font-semibold text-ink">
        {part.slice(2, -2)}
      </strong>
    ) : (
      part
    )
  );
}
