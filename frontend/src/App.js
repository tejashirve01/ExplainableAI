import { useState } from "react";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0a0a0f;
    color: #e8e6f0;
    font-family: 'DM Mono', monospace;
    min-height: 100vh;
  }

  .app {
    max-width: 860px;
    margin: 0 auto;
    padding: 60px 32px;
  }

  .header { margin-bottom: 52px; }

  .header-label {
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #6b5fd6;
    margin-bottom: 12px;
    font-weight: 500;
  }

  h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(28px, 5vw, 44px);
    font-weight: 800;
    color: #f0eeff;
    line-height: 1.1;
    letter-spacing: -0.03em;
  }

  h1 span { color: #7c6de8; }

  .search-row {
    display: flex;
    gap: 12px;
    margin-bottom: 52px;
  }

  .input-wrap { flex: 1; position: relative; }

  .input-wrap::before {
    content: '>';
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #7c6de8;
    font-size: 14px;
    pointer-events: none;
  }

  input[type="text"] {
    width: 100%;
    padding: 14px 16px 14px 36px;
    background: #13121a;
    border: 1px solid #2a2838;
    border-radius: 8px;
    color: #e8e6f0;
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }

  input[type="text"]:focus { border-color: #7c6de8; }
  input[type="text"]::placeholder { color: #3d3a52; }

  .btn-primary {
    padding: 14px 28px;
    background: #7c6de8;
    border: none;
    border-radius: 8px;
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    white-space: nowrap;
  }

  .btn-primary:hover { background: #9183ef; }
  .btn-primary:active { transform: scale(0.98); }
  .btn-primary:disabled { background: #2a2838; color: #3d3a52; cursor: not-allowed; }

  .btn-outline {
    padding: 10px 20px;
    background: transparent;
    border: 1px solid #2a2838;
    border-radius: 8px;
    color: #a294f5;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.08em;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
    white-space: nowrap;
  }

  .btn-outline:hover { border-color: #7c6de8; background: #1c1a2e; }

  .btn-trace {
    padding: 10px 20px;
    background: transparent;
    border: 1px solid #2a3828;
    border-radius: 8px;
    color: #4ade80;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.08em;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
    white-space: nowrap;
  }

  .btn-trace:hover { border-color: #4ade80; background: #0d2e1a; }

  .btn-back {
    padding: 10px 20px;
    background: transparent;
    border: 1px solid #2a2838;
    border-radius: 8px;
    color: #9e9bb8;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    cursor: pointer;
    transition: border-color 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .btn-back:hover { border-color: #7c6de8; color: #a294f5; }

  .spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid #3d3a52;
    border-top-color: #7c6de8;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    vertical-align: middle;
    margin-right: 8px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .result {
    display: flex;
    flex-direction: column;
    gap: 20px;
    animation: fadeUp 0.4s ease both;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .card {
    background: #13121a;
    border: 1px solid #2a2838;
    border-radius: 12px;
    padding: 28px;
  }

  .card-label {
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #7c6de8;
    font-weight: 500;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .card-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #2a2838;
  }

  .answer-text {
    font-size: 15px;
    line-height: 1.8;
    color: #d4d0e8;
    font-weight: 300;
  }

  .meta-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .confidence-val {
    font-size: 28px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #f0eeff;
    margin-bottom: 10px;
  }

  .bar-track {
    height: 4px;
    background: #2a2838;
    border-radius: 4px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #6b5fd6, #a294f5);
    transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 10px;
  }

  .badge-high   { background: #0d2e1a; color: #4ade80; border: 1px solid #166534; }
  .badge-medium { background: #2e2100; color: #fbbf24; border: 1px solid #92400e; }
  .badge-low    { background: #2e0e0e; color: #f87171; border: 1px solid #991b1b; }

  .reasoning-text {
    font-size: 13px;
    line-height: 1.9;
    color: #9e9bb8;
    white-space: pre-wrap;
    font-weight: 300;
    font-family: 'DM Mono', monospace;
  }

  .keywords-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .keyword {
    padding: 5px 14px;
    background: #1c1a2e;
    border: 1px solid #2a2838;
    border-radius: 20px;
    font-size: 12px;
    color: #a294f5;
    letter-spacing: 0.05em;
  }

  .error-card {
    background: #1a0e0e;
    border: 1px solid #4a1414;
    border-radius: 12px;
    padding: 20px 24px;
    color: #f87171;
    font-size: 13px;
  }

  .footer-btns {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 4px;
  }

  /* ---- Sources Page ---- */
  .sources-page {
    max-width: 860px;
    margin: 0 auto;
    padding: 60px 32px;
    animation: fadeUp 0.4s ease both;
  }

  .sources-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 40px;
    gap: 20px;
    flex-wrap: wrap;
  }

  .sources-title {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #f0eeff;
    letter-spacing: -0.02em;
  }

  .sources-subtitle {
    font-size: 12px;
    color: #3d3a52;
    margin-top: 6px;
    font-weight: 300;
  }

  .chunk-card {
    background: #13121a;
    border: 1px solid #2a2838;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
    transition: border-color 0.2s;
  }

  .chunk-card:hover { border-color: #3d3a52; }

  .chunk-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .chunk-rank {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #7c6de8;
  }

  .chunk-meta {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .chunk-source {
    font-size: 11px;
    color: #3d3a52;
    background: #1c1a2e;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid #2a2838;
  }

  .chunk-score {
    font-size: 11px;
    color: #a294f5;
    font-weight: 500;
  }

  .chunk-text {
    font-size: 13px;
    line-height: 1.9;
    color: #9e9bb8;
    font-weight: 300;
    border-left: 2px solid #2a2838;
    padding-left: 16px;
  }

  .chunk-score-bar {
    margin-top: 18px;
    height: 2px;
    background: #2a2838;
    border-radius: 2px;
    overflow: hidden;
  }

  .chunk-score-fill {
    height: 100%;
    background: linear-gradient(90deg, #6b5fd6, #a294f5);
    border-radius: 2px;
  }

  /* ---- Trace Page ---- */
  .trace-page {
    max-width: 860px;
    margin: 0 auto;
    padding: 60px 32px;
    animation: fadeUp 0.4s ease both;
  }

  .trace-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 40px;
    gap: 20px;
    flex-wrap: wrap;
  }

  .trace-title {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #f0eeff;
    letter-spacing: -0.02em;
  }

  .trace-subtitle {
    font-size: 12px;
    color: #3d3a52;
    margin-top: 6px;
    font-weight: 300;
  }

  .trace-total {
    font-size: 11px;
    color: #4ade80;
    margin-top: 4px;
    letter-spacing: 0.05em;
  }

  .timeline {
    position: relative;
    padding-left: 40px;
  }

  .timeline::before {
    content: '';
    position: absolute;
    left: 14px;
    top: 0;
    bottom: 0;
    width: 1px;
    background: linear-gradient(to bottom, #2a2838, #2a2838 90%, transparent);
  }

  .trace-item {
    position: relative;
    margin-bottom: 28px;
    animation: fadeUp 0.4s ease both;
  }

  .trace-item:nth-child(1) { animation-delay: 0.05s; }
  .trace-item:nth-child(2) { animation-delay: 0.10s; }
  .trace-item:nth-child(3) { animation-delay: 0.15s; }
  .trace-item:nth-child(4) { animation-delay: 0.20s; }
  .trace-item:nth-child(5) { animation-delay: 0.25s; }
  .trace-item:nth-child(6) { animation-delay: 0.30s; }
  .trace-item:nth-child(7) { animation-delay: 0.35s; }
  .trace-item:nth-child(8) { animation-delay: 0.40s; }

  .trace-dot {
    position: absolute;
    left: -33px;
    top: 14px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #7c6de8;
    border: 2px solid #0a0a0f;
    box-shadow: 0 0 0 1px #7c6de8;
  }

  .trace-dot.last {
    background: #4ade80;
    box-shadow: 0 0 0 1px #4ade80;
  }

  .trace-card {
    background: #13121a;
    border: 1px solid #2a2838;
    border-radius: 10px;
    padding: 20px 24px;
    transition: border-color 0.2s;
  }

  .trace-card:hover { border-color: #3d3a52; }

  .trace-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .trace-step-label {
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #3d3a52;
    font-weight: 500;
  }

  .trace-step-title {
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #f0eeff;
    margin-bottom: 2px;
  }

  .trace-duration {
    font-size: 11px;
    color: #4ade80;
    background: #0d2e1a;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid #166534;
    white-space: nowrap;
  }

  .trace-detail {
    font-size: 12px;
    line-height: 1.8;
    color: #6b6880;
    white-space: pre-wrap;
    font-weight: 300;
    margin-top: 8px;
    border-left: 2px solid #1c1a2e;
    padding-left: 12px;
  }
`;

function SourcesPage({ chunks, question, onBack }) {
  return (
    <div className="sources-page">
      <div className="sources-header">
        <div>
          <div className="header-label">Retrieved Sources</div>
          <div className="sources-title">Top 3 Chunks</div>
          <div className="sources-subtitle">"{question}"</div>
        </div>
        <button className="btn-back" onClick={onBack}>← Back to answer</button>
      </div>

      {chunks.map((chunk, i) => (
        <div className="chunk-card" key={i}>
          <div className="chunk-top">
            <span className="chunk-rank">Chunk #{i + 1}</span>
            <div className="chunk-meta">
              <span className="chunk-source">{chunk.source}</span>
              <span className="chunk-score">score: {chunk.score.toFixed(4)}</span>
            </div>
          </div>
          <p className="chunk-text">{chunk.text}</p>
          <div className="chunk-score-bar">
            <div className="chunk-score-fill" style={{ width: `${Math.round(chunk.score * 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function TracePage({ traces, question, onBack }) {
  const totalMs = traces.length > 0 ? traces[traces.length - 1].duration_ms : 0;

  return (
    <div className="trace-page">
      <div className="trace-header">
        <div>
          <div className="header-label">Pipeline Trace</div>
          <div className="trace-title">Trace Viewer</div>
          <div className="sources-subtitle">"{question}"</div>
          <div className="trace-total">Total time: {totalMs}ms — {traces.length} steps</div>
        </div>
        <button className="btn-back" onClick={onBack}>← Back to answer</button>
      </div>

      <div className="timeline">
        {traces.map((trace, i) => (
          <div className="trace-item" key={i}>
            <div className={`trace-dot ${i === traces.length - 1 ? "last" : ""}`} />
            <div className="trace-card">
              <div className="trace-card-top">
                <div>
                  <div className="trace-step-label">Step {trace.step}</div>
                  <div className="trace-step-title">{trace.title}</div>
                </div>
                <span className="trace-duration">{trace.duration_ms}ms</span>
              </div>
              <div className="trace-detail">{trace.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState("main");

  const askQuestion = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setPage("main");

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") askQuestion();
  };

  const confidencePct = result ? Math.round(result.confidence * 100) : 0;
  const badgeClass =
    result?.confidence_level === "high" ? "badge-high" :
    result?.confidence_level === "low"  ? "badge-low"  : "badge-medium";

  if (page === "sources" && result?.chunks) {
    return (
      <>
        <style>{styles}</style>
        <SourcesPage chunks={result.chunks} question={question} onBack={() => setPage("main")} />
      </>
    );
  }

  if (page === "trace" && result?.traces) {
    return (
      <>
        <style>{styles}</style>
        <TracePage traces={result.traces} question={question} onBack={() => setPage("main")} />
      </>
    );
  }

  return (
    <>
      <style>{styles}</style>
      <div className="app">

        <div className="header">
          <div className="header-label">XAI System v1.0</div>
          <h1>Explainable <span>Research</span><br />Assistant</h1>
        </div>

        <div className="search-row">
          <div className="input-wrap">
            <input
              type="text"
              placeholder="Ask a question about your documents..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKey}
            />
          </div>
          <button className="btn-primary" onClick={askQuestion} disabled={loading || !question.trim()}>
            {loading ? <><span className="spinner" />Thinking</> : "Ask"}
          </button>
        </div>

        {error && <div className="error-card">Error: {error}</div>}

        {result && (
          <div className="result">

            <div className="card">
              <div className="card-label">Answer</div>
              <p className="answer-text">{result.answer}</p>
            </div>

            <div className="meta-row">
              <div className="card">
                <div className="card-label">Confidence score</div>
                <div className="confidence-val">{(result.confidence * 100).toFixed(1)}%</div>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${confidencePct}%` }} />
                </div>
              </div>

              <div className="card">
                <div className="card-label">Confidence level</div>
                <div className="confidence-val" style={{ fontSize: "20px", marginTop: "4px" }}>
                  {result.confidence_level
                    ? result.confidence_level.charAt(0).toUpperCase() + result.confidence_level.slice(1)
                    : "—"}
                </div>
                {result.confidence_level && (
                  <span className={`badge ${badgeClass}`}>{result.confidence_level}</span>
                )}
              </div>
            </div>

            {result.reasoning && (
              <div className="card">
                <div className="card-label">Reasoning</div>
                <pre className="reasoning-text">{result.reasoning}</pre>
              </div>
            )}

            {result.keywords?.length > 0 && (
              <div className="card">
                <div className="card-label">Keywords</div>
                <div className="keywords-wrap">
                  {result.keywords.map((k, i) => (
                    <span className="keyword" key={i}>{k}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="footer-btns">
              {result.chunks?.length > 0 && (
                <button className="btn-outline" onClick={() => setPage("sources")}>
                  View Top 3 Chunks →
                </button>
              )}
              {result.traces?.length > 0 && (
                <button className="btn-trace" onClick={() => setPage("trace")}>
                  Trace Viewer ⟩
                </button>
              )}
            </div>

          </div>
        )}
      </div>
    </>
  );
}