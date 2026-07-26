const API_BASE = "http://localhost:8000/api";

export async function fetchCases() {
  const res = await fetch(`${API_BASE}/cases`);
  if (!res.ok) throw new Error(`Failed to fetch cases: ${res.status}`);
  const data = await res.json();
  return data.cases;
}

export async function fetchCase(caseName) {
  const res = await fetch(`${API_BASE}/cases/${caseName}`);
  if (!res.ok) throw new Error(`Failed to fetch case: ${res.status}`);
  return res.json();
}

export function resolveDispute(caseName, onEvent, onError, onDone) {
  const url = `${API_BASE}/disputes/${caseName}/resolve`;
  const eventSource = new EventSource(url);

  eventSource.addEventListener("classified", (e) => {
    onEvent("classified", JSON.parse(e.data));
  });

  eventSource.addEventListener("facts_extracted", (e) => {
    onEvent("facts_extracted", JSON.parse(e.data));
  });

  eventSource.addEventListener("rules_fired", (e) => {
    onEvent("rules_fired", JSON.parse(e.data));
  });

  eventSource.addEventListener("verdict", (e) => {
    onEvent("verdict", JSON.parse(e.data));
  });

  eventSource.addEventListener("memo", (e) => {
    onEvent("memo", JSON.parse(e.data));
  });

  eventSource.addEventListener("ledger", (e) => {
    onEvent("ledger", JSON.parse(e.data));
  });

  eventSource.addEventListener("done", (e) => {
    const data = JSON.parse(e.data);
    eventSource.close();
    if (onDone) onDone(data);
  });

  eventSource.onerror = (err) => {
    eventSource.close();
    if (onError) onError(err);
  };

  return eventSource;
}

export async function fetchLedger(caseName) {
  const res = await fetch(`${API_BASE}/disputes/${caseName}/ledger`);
  if (!res.ok) throw new Error(`Failed to fetch ledger: ${res.status}`);
  return res.json();
}
