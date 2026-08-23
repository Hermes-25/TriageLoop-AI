export function TriageLoader() {
  return (
    <main className="triage-loader" role="status" aria-live="polite" aria-label="Loading the TriageLoop live action queue">
      <div className="triage-loader-instrument" aria-hidden="true">
        <span className="triage-loader-ring" />
        <span className="triage-loader-signal signal-one" />
        <span className="triage-loader-signal signal-two" />
        <span className="triage-loader-signal signal-three" />
        <span className="triage-loader-core" />
      </div>
      <div className="triage-loader-copy">
        <strong>Synchronising the live action queue</strong>
        <span>Loading 20 simulated patients, Action Windows and capacity state</span>
      </div>
      <div className="triage-loader-progress" aria-hidden="true"><span /></div>
    </main>
  );
}
