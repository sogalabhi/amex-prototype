const TYPE_LABELS = {
  order_receipt: "Receipt",
  delivery_confirmation: "Delivery",
  chat_log: "Chat Log",
  policy: "Policy",
  product_description: "Description",
  merchant_photos: "Photos",
};

function Chip({ children, variant = "neutral" }) {
  const styles = {
    neutral: "border-line bg-elevated text-muted",
    brand: "border-brand-accent/30 bg-brand/12 text-brand-accent",
  };
  return (
    <span
      className={`rounded border px-1.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-wide ${styles[variant]}`}
    >
      {children}
    </span>
  );
}

export default function EvidencePanel({ caseData }) {
  if (!caseData) {
    return (
      <section>
        <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
          Evidence
        </h2>
        <div className="rounded-lg border border-dashed border-line px-4 py-10 text-center text-xs text-muted">
          Select a case to view its evidence
        </div>
      </section>
    );
  }

  return (
    <section>
      <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
        Evidence
      </h2>

      <div className="space-y-2.5">
        {/* Cardmember claim — the only brand-tinted panel, it anchors the dispute */}
        <div className="rounded-lg border border-line bg-surface p-4">
          <div className="mb-2 flex items-center gap-2">
            <Chip variant="brand">Claim</Chip>
            <span className="text-[11px] text-muted">
              Filed {caseData.cardmember_claim.filed_date}
            </span>
          </div>
          <p className="text-[13px] leading-relaxed text-ink">
            {caseData.cardmember_claim.text}
          </p>
        </div>

        {/* Transaction */}
        <div className="rounded-lg border border-line bg-surface p-4">
          <div className="mb-2.5 flex items-center gap-2">
            <Chip>Transaction</Chip>
            <span className="font-mono text-[11px] text-muted">
              {caseData.transaction.txn_id}
            </span>
          </div>
          <dl className="space-y-1 text-[11px]">
            <Field label="Amount">
              {caseData.transaction.currency} {caseData.transaction.amount}
            </Field>
            <Field label="Date">{caseData.transaction.date}</Field>
            <Field label="Merchant">{caseData.transaction.merchant}</Field>
            <Field label="Descriptor">{caseData.transaction.descriptor}</Field>
            <Field label="Channel">{caseData.transaction.channel}</Field>
            {caseData.transaction.shipping_address_on_order && (
              <Field label="Ship to">
                {caseData.transaction.shipping_address_on_order}
              </Field>
            )}
          </dl>
        </div>

        {/* Merchant evidence */}
        <div className="pt-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
          Merchant Submission · {caseData.merchant_evidence.length} documents
        </div>

        {caseData.merchant_evidence.map((doc) => (
          <div
            key={doc.doc_id}
            className="rounded-lg border border-line bg-surface p-4"
          >
            <div className="mb-2.5 flex items-center gap-2">
              <Chip>{doc.doc_id}</Chip>
              <span className="text-[11px] font-medium text-ink">
                {TYPE_LABELS[doc.type] || doc.type}
              </span>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-[11px] leading-relaxed text-muted">
              {doc.content}
            </pre>
          </div>
        ))}
      </div>
    </section>
  );
}

function Field({ label, children }) {
  return (
    <div className="flex gap-2">
      <dt className="w-20 shrink-0 text-muted">{label}</dt>
      <dd className="min-w-0 flex-1 break-words font-mono text-ink">{children}</dd>
    </div>
  );
}
