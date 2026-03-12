import { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);

  const askQuestion = async () => {
    const response = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question }),
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Explainable AI Research Assistant</h1>

      <input
        type="text"
        placeholder="Ask a question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "400px", padding: "10px" }}
      />

      <button onClick={askQuestion} style={{ marginLeft: "10px" }}>
        Ask
      </button>

      {result && (
        <div style={{ marginTop: "30px" }}>
          <h3>Answer</h3>
          <p>{result.answer}</p>

          <h4>Confidence</h4>
          <p>{result.confidence}</p>

          <h4>Evidence Sentence</h4>
          <p>{result.evidence_sentence}</p>

          <h4>Keywords</h4>
          <ul>
            {result.keywords.map((k, i) => (
              <li key={i}>{k}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;