import { useState, useEffect, useCallback } from "react";
import { fetchCases, fetchCase, resolveDispute } from "./api";
import CaseSelector from "./components/CaseSelector";
import EvidencePanel from "./components/EvidencePanel";
import PipelineStream from "./components/PipelineStream";
import DecisionMemo from "./components/DecisionMemo";
import LedgerTrail from "./components/LedgerTrail";
import Footer from "./components/Footer";

function App() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseData, setCaseData] = useState(null);
  const [isResolving, setIsResolving] = useState(false);
  const [events, setEvents] = useState({});
  const [totalElapsed, setTotalElapsed] = useState(null);

  // Load available cases on mount
  useEffect(() => {
    fetchCases()
      .then(setCases)
      .catch((err) => console.error("Failed to load cases:", err));
  }, []);

  // Load case data when selection changes. The cancelled flag keeps a slow response
  // for a previously selected case from overwriting a newer one.
  useEffect(() => {
    if (!selectedCase) return;

    let cancelled = false;
    fetchCase(selectedCase)
      .then((data) => {
        if (!cancelled) setCaseData(data);
      })
      .catch((err) => console.error("Failed to load case:", err));

    return () => {
      cancelled = true;
    };
  }, [selectedCase]);

  const handleSelect = useCallback((caseName) => {
    setSelectedCase(caseName);
    setCaseData(null);
    setEvents({});
    setTotalElapsed(null);
  }, []);

  const handleResolve = useCallback(() => {
    if (!selectedCase || isResolving) return;

    setIsResolving(true);
    setEvents({});
    setTotalElapsed(null);

    resolveDispute(
      selectedCase,
      (eventType, data) => {
        setEvents((prev) => ({ ...prev, [eventType]: data }));
      },
      (err) => {
        console.error("SSE error:", err);
        setIsResolving(false);
      },
      (doneData) => {
        setTotalElapsed(doneData.total_elapsed_ms);
        setIsResolving(false);
      }
    );
  }, [selectedCase, isResolving]);

  return (
    <div className="min-h-screen bg-canvas text-ink font-sans pb-16">
      <header className="sticky top-0 z-40 border-b border-line bg-canvas/90 backdrop-blur-sm">
        <div className="h-0.5 bg-brand" />
        <div className="mx-auto flex max-w-[1500px] items-center justify-between px-8 py-4">
          <div className="flex items-center gap-3.5">
            <div className="flex h-9 w-9 items-center justify-center rounded bg-brand text-[13px] font-bold tracking-tight text-white">
              VC
            </div>
            <div className="leading-tight">
              <h1 className="text-[15px] font-semibold tracking-tight text-ink">
                Verdict Chain
              </h1>
              <p className="text-xs text-muted">Dispute Resolution Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                isResolving ? "animate-pulse bg-brand-accent" : "bg-muted/50"
              }`}
            />
            <span className="text-xs font-medium text-muted">
              {isResolving ? "Adjudicating" : "Ready"}
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1500px] px-8 py-8">
        <div className="grid grid-cols-[360px_1fr] items-start gap-8">
          {/* Left column — case selection and raw evidence */}
          <div className="sticky top-24 max-h-[calc(100vh-8rem)] space-y-8 overflow-y-auto pr-1">
            <CaseSelector
              cases={cases}
              selectedCase={selectedCase}
              onSelect={handleSelect}
              onResolve={handleResolve}
              isResolving={isResolving}
            />
            <EvidencePanel caseData={caseData} />
          </div>

          {/* Right column — pipeline, memo, audit trail */}
          <div className="space-y-8">
            <PipelineStream
              events={events}
              isResolving={isResolving}
              totalElapsed={totalElapsed}
            />
            <DecisionMemo memoData={events.memo} />
            <LedgerTrail ledgerData={events.ledger} />
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
