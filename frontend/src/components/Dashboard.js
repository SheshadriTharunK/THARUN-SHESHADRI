import React, { useState } from "react";
import { analyzeText } from "../api";
import Result from "./Result";

function Dashboard({ token, logout }) {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);

  // helper delay
  const delay = (ms) => new Promise((res) => setTimeout(res, ms));

  const detect = async () => {
    // ✅ validation
    if (!text || text.trim() === "") {
      alert("⚠️ Please enter some text to analyze");
      return;
    }

    setLoading(true);
    setResult(null);
    setStep(0);

    // 🔥 simulate pipeline
    setStep(1);
    await delay(500);

    setStep(2);
    await delay(500);

    setStep(3);
    await delay(500);

    setStep(4);

    try {
      const data = await analyzeText(text, token);
      setResult(data);
    } catch (error) {
      setResult({ error: "Something went wrong" });
    }

    setLoading(false);
  };

  return (
    <>
      <h3>🧠 Multi-Agent AI System for Fact Verification</h3>

      <textarea
        rows="4"
        placeholder="Paste news here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button onClick={detect} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      <button onClick={logout}>Logout</button>

      {/* 🔥 PIPELINE UI */}
      {loading && (
        <div style={{ marginTop: "15px", textAlign: "left" }}>
          <p style={{ opacity: step >= 1 ? 1 : 0.3 }}>
            🔍 Extracting claims...
          </p>
          <p style={{ opacity: step >= 2 ? 1 : 0.3 }}>
            🌐 Gathering evidence...
          </p>
          <p style={{ opacity: step >= 3 ? 1 : 0.3 }}>
            🧠 Fact-checking...
          </p>
          <p style={{ opacity: step >= 4 ? 1 : 0.3 }}>
            📊 Generating verdict...
          </p>
        </div>
      )}

      {/* RESULT */}
      <Result result={result} />
    </>
  );
}

export default Dashboard;