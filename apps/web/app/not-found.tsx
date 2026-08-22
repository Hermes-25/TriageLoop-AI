import Link from "next/link";

export default function NotFound() {
  return (
    <main className="page-centered">
      <div className="error-state">
        <h1>That view is not available</h1>
        <p>Return to the live waiting-room board.</p>
        <Link className="button primary" href="/board">Open live board</Link>
      </div>
    </main>
  );
}
