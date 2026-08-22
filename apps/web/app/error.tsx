"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="page-centered">
      <div className="error-state">
        <h1>The product surface could not load</h1>
        <p>The clinical calculation service may be unavailable. No state-changing action has been recorded.</p>
        <button className="button primary" type="button" onClick={reset}>Try again</button>
      </div>
    </main>
  );
}
