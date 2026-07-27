export default function LedgerTrail({ ledgerData }) {
  if (!ledgerData) return null;

  const chain = ledgerData.chain || [];
  if (chain.length === 0) return null;

  return (
    <section>
      <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
        Tamper-Evidence Chain
      </h2>

      <div className="rounded-lg border border-line bg-surface p-6">
        <ol>
          {chain.map((entry, i) => {
            const isLast = i === chain.length - 1;
            return (
              <li key={i} className="flex gap-3.5">
                {/* Chain connector */}
                <div className="flex flex-col items-center pt-1">
                  <span
                    className={`h-2 w-2 shrink-0 rounded-full ${
                      isLast ? "bg-brand-accent" : "border border-line bg-elevated"
                    }`}
                  />
                  {!isLast && <span className="w-px flex-1 bg-line" />}
                </div>

                <div className={isLast ? "" : "pb-5"}>
                  <div className="flex items-baseline gap-2">
                    <span className="text-[12px] font-semibold capitalize text-ink">
                      {entry.stage.replace(/_/g, " ")}
                    </span>
                    <span className="font-mono text-[10px] tabular-nums text-muted">
                      {entry.timestamp?.split("T")[1]?.split(".")[0]}
                    </span>
                  </div>

                  <div className="mt-0.5 text-[11px] leading-relaxed text-muted">
                    {entry.payload_summary}
                  </div>

                  <div
                    className="mt-1 truncate font-mono text-[10px] text-muted/60"
                    title={entry.hash}
                  >
                    {entry.hash?.slice(0, 32)}…
                  </div>
                </div>
              </li>
            );
          })}
        </ol>

        <div className="mt-1 flex items-center gap-2 border-t border-line pt-4">
          <svg
            className="h-3.5 w-3.5 text-brand-accent"
            viewBox="0 0 14 14"
            fill="none"
            aria-hidden="true"
          >
            <circle cx="7" cy="7" r="6.25" stroke="currentColor" strokeWidth="1.2" />
            <path
              d="M4.4 7.2l1.8 1.8L9.8 5.4"
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span className="text-[11px] font-medium text-ink">
            Chain verified — SHA-256 integrity intact across {chain.length} entries
          </span>
        </div>

        {ledgerData.evm && (
          <div className="mt-4 rounded-md border border-line bg-elevated p-4">
            <div className="mb-2 flex items-baseline justify-between gap-3">
              <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink">
                On-Chain Commitment
              </span>
              <span className="shrink-0 font-mono text-[10px] font-medium text-brand-accent">
                Block #{ledgerData.evm.block_number}
              </span>
            </div>
            <dl className="space-y-1 text-[10px]">
              <Row label="Tx">{ledgerData.evm.transaction_hash}</Row>
              <Row label="Commitment">{ledgerData.evm.commitment_hash}</Row>
            </dl>
          </div>
        )}
      </div>
    </section>
  );
}

function Row({ label, children }) {
  return (
    <div className="flex gap-2">
      <dt className="w-20 shrink-0 text-muted">{label}</dt>
      <dd className="min-w-0 flex-1 truncate font-mono text-ink" title={children}>
        {children}
      </dd>
    </div>
  );
}
