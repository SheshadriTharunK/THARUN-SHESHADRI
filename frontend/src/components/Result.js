import React from "react";

function Result({ result }) {
  if (!result) return null;

  if (result === "loading") return <p>🔍 Analyzing...</p>;

  const uf = result.user_friendly;

  return (
    <div style={{
      marginTop: "20px",
      padding: "15px",
      borderRadius: "10px",
      background: "#f9fafb",
      textAlign: "left"
    }}>

      {/* STATUS */}
      <h3 style={{
        color:
          uf?.confidence_level === "high"
            ? "green"
            : uf?.confidence_level === "medium"
            ? "orange"
            : "red"
      }}>
        {uf?.status}
      </h3>

      {/* CONFIDENCE */}
      <p><b>Confidence Score:</b> {uf?.confidence_score}</p>
      <p><b>Confidence Level:</b> {uf?.confidence_level}</p>

      <hr />

      {/* SUMMARY */}
      <p><b>Summary:</b><br /> {uf?.summary}</p>

      <hr />

      {/* KEY CLAIM */}
      <p><b>Key Claim:</b><br /> {uf?.key_claim}</p>

      <p><b>Claim Verdict:</b> {uf?.key_claim_verdict}</p>

      <p><b>Reason:</b><br /> {uf?.key_claim_reason}</p>

      <hr />

      {/* RECOMMENDATION */}
      <p><b>Recommendation:</b><br /> {result.recommendation}</p>

      <hr />

      {/* NOTE */}
      <p style={{ fontSize: "12px", color: "gray" }}>
        {uf?.note}
      </p>

    </div>
  );
}

export default Result;