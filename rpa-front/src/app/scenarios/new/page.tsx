"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function NewScenarioPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (!name.trim()) {
      setError("名前を入力してください");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/scenarios", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await router.push("/scenarios");
    } catch (e: any) {
      setError(e?.message ?? "作成に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 720, margin: "32px auto", padding: 16 }}>
      <h2>シナリオを新規作成</h2>

      {error && <div style={{ color: "#b00", marginTop: 8 }}>エラー: {error}</div>}

      <div style={{ display: "grid", gap: 12, marginTop: 12 }}>
        <div>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>名前</div>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="例: 毎朝のレポート作成"
            style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 6 }}
          />
        </div>
        <div>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>説明（任意）</div>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="シナリオの概要や目的を記載"
            style={{ width: "100%", minHeight: 120, padding: 8, border: "1px solid #ccc", borderRadius: 6 }}
          />
        </div>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button onClick={() => router.push("/scenarios")} style={{ padding: "8px 12px" }}>一覧へ戻る</button>
          <button onClick={submit} disabled={loading} style={{ padding: "8px 12px" }}>
            {loading ? "作成中..." : "作成する"}
          </button>
        </div>
      </div>

      <hr style={{ margin: "24px 0" }} />
      <div style={{ fontSize: 12, color: "#666" }}>
        デモのステップビルダーは <a href="/demo" style={{ textDecoration: "underline" }}>/demo</a> で確認できます。
      </div>
    </div>
  );
}


