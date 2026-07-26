import { useState, useEffect, useCallback } from "react";
import { fetchCases, fetchCase, resolveDispute } from "./api";
import CaseSelector from "./components/CaseSelector";
import EvidencePanel from "./components/EvidencePanel";
import PipelineStream from "./components/PipelineStream";
import DecisionMemo from "./components/DecisionMemo";
import LedgerTrail from "./components/LedgerTrail";
import Footer from "./components/Footer";
import "./App.css";

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

  // Load case data when selection changes
  useEffect(() => {
    if (!selectedCase) {
      setCaseData(null);
      return;
    }
    fetchCase(selectedCase)
      .then(setCaseData)
      .catch((err) => console.error("Failed to load case:", err));
  }, [selectedCase]);

  const handleSelect = useCallback((caseName) => {
    setSelectedCase(caseName);
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
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200 pb-12">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#006FCF] flex items-center justify-center text-white font-bold text-sm">
              V
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">Verdict Chain</h1>
              <p className="text-xs text-slate-500">AI-Powered Dispute Resolution</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs text-slate-600">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-1.5" />
              Pipeline Ready
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-6 py-6">
        <div className="grid grid-cols-[380px_1fr] gap-6 items-start">
          {/* Left Column - Case Selector + Evidence */}
          <div className="space-y-6 sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto pr-2">
            <CaseSelector
              cases={cases}
              selectedCase={selectedCase}
              onSelect={handleSelect}
              onResolve={handleResolve}
              isResolving={isResolving}
            />
            <EvidencePanel caseData={caseData} />
          </div>

          {/* Right Column - Pipeline + Memo + Ledger */}
          <div className="space-y-6">
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
