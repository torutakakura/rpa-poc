"use client";

import { useEffect, useMemo, useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [imgB64, setImgB64] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<any[]>([]);
  const [scenarioJson, setScenarioJson] = useState<string>(
    JSON.stringify(
      {
        steps: [
          { type: "open_browser", headless: true },
          { type: "goto", url: "https://example.com" },
          { type: "screenshot", full_page: true },
        ],
      },
      null,
      2
    )
  );

  

  useEffect(() => {
    const fetchSteps = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/steps");
        const data = await res.json();
        setSteps(data.steps ?? []);
      } catch (e) {
        // noop
      }
    };
    fetchSteps();
  }, []);

  return (
    <div style={{ maxWidth: 1100, margin: "40px auto", padding: 16 }}>
      <h2>JSONシナリオ実行</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 16 }}>
        <textarea
          value={scenarioJson}
          onChange={(e) => setScenarioJson(e.target.value)}
          style={{ width: "100%", minHeight: 280, fontFamily: "monospace", fontSize: 13, padding: 8, border: "1px solid #ccc", borderRadius: 6 }}
        />
        <div>
          <button
            onClick={async () => {
              setLoading(true);
              setError(null);
              setImgB64(null);
              setLogs([]);
              try {
                const body = JSON.parse(scenarioJson);
                const res = await fetch("http://127.0.0.1:8000/run_scenario", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify(body),
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                if (data.ok) {
                  setLogs(data.logs ?? []);
                  const lastWithImage = (data.results ?? []).reverse().find((r: any) => r.image_base64);
                  if (lastWithImage) setImgB64(lastWithImage.image_base64);
                } else {
                  setError("シナリオ実行に失敗しました");
                }
              } catch (e: any) {
                setError(e?.message ?? "エラーが発生しました");
              } finally {
                setLoading(false);
              }
            }}
            disabled={loading}
            style={{ padding: "8px 16px" }}
          >
            {loading ? "実行中..." : "シナリオを実行"}
          </button>
          <div style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
            `/steps` にある例を組み合わせて自由に編集できます。
          </div>
        </div>
      </div>

      {error && (
        <div style={{ color: "red", marginTop: 12 }}>
          エラー: {error}
        </div>
      )}

      {logs.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h3>ログ</h3>
          <ul>
            {logs.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        </div>
      )}

      {imgB64 && (
        <div style={{ marginTop: 16 }}>
          <h3>スクリーンショット</h3>
          <img
            src={`data:image/png;base64,${imgB64}`}
            alt="screenshot"
            style={{ border: "1px solid #eee", maxWidth: "100%" }}
          />
        </div>
      )}

      <hr style={{ margin: "32px 0" }} />
      <h2>利用可能なステップ</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12 }}>
        {steps.map((s, i) => (
          <div key={i} style={{ border: "1px solid #eee", borderRadius: 8, padding: 12 }}>
            <div style={{ fontWeight: 600 }}>{s.title} <span style={{ color: "#666" }}>({s.type})</span></div>
            <div style={{ fontSize: 13, color: "#666", marginTop: 4 }}>{s.description}</div>
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 12, color: "#666" }}>例:</div>
              <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", background: "#f9f9f9", padding: 8, borderRadius: 6 }}>
                {JSON.stringify(s.example, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
