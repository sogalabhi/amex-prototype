const TYPE_LABELS = {
  order_receipt: "Receipt",
  delivery_confirmation: "Delivery",
  chat_log: "Chat Log",
  policy: "Policy",
  product_description: "Description",
  merchant_photos: "Photos",
};

const TYPE_COLORS = {
  order_receipt: "bg-blue-500/20 text-blue-400",
  delivery_confirmation: "bg-emerald-500/20 text-emerald-400",
  chat_log: "bg-amber-500/20 text-amber-400",
  policy: "bg-purple-500/20 text-purple-400",
  product_description: "bg-cyan-500/20 text-cyan-400",
  merchant_photos: "bg-pink-500/20 text-pink-400",
};

export default function EvidencePanel({ caseData }) {
  if (!caseData) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-600 text-sm">
        Select a case to view evidence
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">
        Raw Evidence
      </h2>

      {/* Cardmember Claim */}
      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-400 font-mono">
            CLAIM
          </span>
          <span className="text-xs text-slate-500">
            Filed {caseData.cardmember_claim.filed_date}
          </span>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed">
          {caseData.cardmember_claim.text}
        </p>
      </div>

      {/* Transaction */}
      <div className="rounded-xl border border-white/5 bg-[#14141f] p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs px-2 py-0.5 rounded-md bg-white/10 text-slate-400 font-mono">
            TXN
          </span>
          <span className="text-xs text-slate-500">{caseData.transaction.txn_id}</span>
        </div>
        <div className="font-mono text-xs text-slate-400 space-y-1">
          <div>Amount: {caseData.transaction.currency} {caseData.transaction.amount}</div>
          <div>Date: {caseData.transaction.date}</div>
          <div>Merchant: {caseData.transaction.merchant}</div>
          <div>Descriptor: {caseData.transaction.descriptor}</div>
          <div>Channel: {caseData.transaction.channel}</div>
          {caseData.transaction.shipping_address_on_order && (
            <div>Ship to: {caseData.transaction.shipping_address_on_order}</div>
          )}
        </div>
      </div>

      {/* Merchant Evidence */}
      <div className="text-xs text-slate-500 uppercase tracking-wider mt-4 mb-2">
        Merchant Evidence ({caseData.merchant_evidence.length} documents)
      </div>
      {caseData.merchant_evidence.map((doc) => (
        <div
          key={doc.doc_id}
          className="rounded-xl border border-white/5 bg-[#14141f] p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs px-2 py-0.5 rounded-md bg-white/10 text-slate-300 font-mono">
              {doc.doc_id}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded-md ${
                TYPE_COLORS[doc.type] || "bg-white/10 text-slate-400"
              }`}
            >
              {TYPE_LABELS[doc.type] || doc.type}
            </span>
          </div>
          <pre className="text-xs text-slate-400 font-mono whitespace-pre-wrap leading-relaxed overflow-x-auto">
            {doc.content}
          </pre>
        </div>
      ))}
    </div>
  );
}
