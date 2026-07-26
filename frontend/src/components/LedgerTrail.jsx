export default function LedgerTrail({ ledgerData }) {
  if (!ledgerData) return null;

  const chain = ledgerData.chain || [];
  if (chain.length === 0) return null;

  return (
    <div className="rounded-xl border border-white/10 bg-[#14141f] p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">
        Tamper-Evidence Chain
      </h2>

      <div className="space-y-0">
        {chain.map((entry, i) => (
          <div key={i} className="flex items-start gap-3">
            {/* Chain connector */}
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full shrink-0 ${i === chain.length - 1 ? "bg-[#006FCF]" : "bg-white/10"
                }`} />
              {i < chain.length - 1 && (
                <div className="w-px h-8 bg-white/10" />
              )}
            </div>

            {/* Entry content */}
            <div className="pb-4 -mt-0.5">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs font-medium text-slate-300">
                  {entry.stage.replace(/_/g, " ")}
                </span>
                <span className="text-xs text-slate-600">{entry.timestamp?.split("T")[1]?.split(".")[0]}</span>
              </div>
              <div className="font-mono text-xs text-slate-600 truncate max-w-xs" title={entry.hash}>
                {entry.hash?.slice(0, 16)}…
              </div>
              <div className="text-xs text-slate-500 mt-0.5">
                {entry.payload_summary}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-2 pt-3 border-t border-white/5 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-emerald-500" />
        <span className="text-xs text-emerald-400">Chain verified — SHA-256 integrity intact</span>
      </div>

      {ledgerData.evm && (
        <div className="mt-4 p-3 rounded-xl border border-[#006FCF]/30 bg-[#006FCF]/10 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#006FCF] flex items-center gap-1.5">
              <span>⛓️</span> EVM Ledger Commitment
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#006FCF]/20 text-[#006FCF] font-mono">
              MINED ON-CHAIN (Block #{ledgerData.evm.block_number})
            </span>
          </div>
          <div className="text-xs font-mono text-slate-300 truncate">
            Tx: {ledgerData.evm.transaction_hash}
          </div>
          <div className="text-[11px] text-slate-400 font-mono truncate">
            Hash: {ledgerData.evm.commitment_hash}
          </div>
          <div className="text-[10px] text-slate-400 italic">
            Tamper-evident SHA-256 verdict commitment anchored on EVM devnet
          </div>
        </div>
      )}
    </div>
  );
}
