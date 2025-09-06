"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ChevronUp, ChevronDown, Copy, Trash2, Plus, Play, FileJson, Info } from "lucide-react";

export default function DemoBuilderPage() {
  const [loading, setLoading] = useState(false);
  const [imgB64, setImgB64] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [availableSteps, setAvailableSteps] = useState<any[]>([]);
  const [filter, setFilter] = useState("");
  const [scenarioSteps, setScenarioSteps] = useState<any[]>([
    { type: "open_browser", headless: true },
    { type: "goto", url: "https://example.com" },
    { type: "screenshot", full_page: true },
  ]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [editorText, setEditorText] = useState<string>("");
  const [showJsonIO, setShowJsonIO] = useState<boolean>(false);
  const [jsonImportText, setJsonImportText] = useState<string>("");
  const [selectedStep, setSelectedStep] = useState<any | null>(null);
  const [showStepModal, setShowStepModal] = useState(false);

  // サンプルシナリオ
  const samples: Array<{ id: string; title: string; description: string; steps: any[] }> = [
    {
      id: "simple-screenshot",
      title: "シンプル: スクリーンショット",
      description: "example.com を開いて全画面スクリーンショットを撮影します。",
      steps: [
        { type: "open_browser", headless: true },
        { type: "goto", url: "https://example.com" },
        { type: "screenshot", full_page: true }
      ],
    },
    {
      id: "wikipedia-search",
      title: "Wikipedia 検索",
      description: "Wikipedia トップで検索 → 記事表示を待機 → スクショ",
      steps: [
        { type: "open_browser", headless: true },
        { type: "goto", url: "https://www.wikipedia.org" },
        { type: "wait_for_selector", selector: "#searchInput", state: "visible" },
        { type: "type", selector: "#searchInput", text: "FastAPI" },
        { type: "press", key: "Enter" },
        { type: "wait_for_selector", selector: "#firstHeading", state: "visible" },
        { type: "screenshot", full_page: true }
      ],
    },
  ];

  useEffect(() => {
    const fetchSteps = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/steps");
        const data = await res.json();
        setAvailableSteps(data.steps ?? []);
      } catch {}
    };
    fetchSteps();
  }, []);

  useEffect(() => {
    if (selectedIndex === null) {
      setEditorText("");
    } else {
      setEditorText(JSON.stringify(scenarioSteps[selectedIndex], null, 2));
    }
  }, [selectedIndex, scenarioSteps]);

  const addStep = (meta: any) => {
    const example = meta?.example ?? { type: meta?.type };
    setScenarioSteps((prev) => [...prev, example]);
    setSelectedIndex(scenarioSteps.length);
  };

  const openStepDetails = (step: any) => {
    setSelectedStep(step);
    setShowStepModal(true);
  };

  const moveStep = (index: number, dir: -1 | 1) => {
    setScenarioSteps((prev) => {
      const next = [...prev];
      const target = index + dir;
      if (target < 0 || target >= next.length) return prev;
      const tmp = next[index];
      next[index] = next[target];
      next[target] = tmp;
      return next;
    });
    setSelectedIndex((i) => (i === null ? null : Math.max(0, Math.min((i as number) + dir, scenarioSteps.length - 1))));
  };

  const removeStep = (index: number) => {
    setScenarioSteps((prev) => prev.filter((_, i) => i !== index));
    setSelectedIndex(null);
  };

  const duplicateStep = (index: number) => {
    setScenarioSteps((prev) => {
      const copy = JSON.parse(JSON.stringify(prev[index]));
      const next = [...prev.slice(0, index + 1), copy, ...prev.slice(index + 1)];
      return next;
    });
    setSelectedIndex(index + 1);
  };

  const applyEditor = () => {
    if (selectedIndex === null) return;
    try {
      const obj = JSON.parse(editorText);
      setScenarioSteps((prev) => prev.map((s, i) => (i === selectedIndex ? obj : s)));
      setError(null);
    } catch (e: any) {
      setError("ステップJSONが不正です: " + (e?.message ?? ""));
    }
  };

  const runScenario = async () => {
    setLoading(true);
    setError(null);
    setImgB64(null);
    setLogs([]);
    try {
      const res = await fetch("http://127.0.0.1:8000/run_scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ steps: scenarioSteps }),
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
  };

  return (
    <div className="container mx-auto py-6 px-4">
      <h1 className="text-3xl font-bold mb-6 text-slate-900">シナリオビルダー（デモ）</h1>
      <div className="grid grid-cols-[300px_1fr_360px] gap-4 items-start">
        {/* Left: Palette */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">ステップ一覧</CardTitle>
            <div className="mt-2">
              <Input
                placeholder="ステップ検索 (タイトル/タイプ)"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full"
              />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2 max-h-[480px] overflow-auto">
            {availableSteps
              .filter((s) => {
                const key = `${s.title} ${s.type}`.toLowerCase();
                return key.includes(filter.toLowerCase());
              })
              .map((s, i) => (
                <Card key={i} className="shadow-none">
                  <CardContent className="p-3">
                    <div className="flex justify-between gap-2">
                      <div className="flex-1">
                        <div 
                          className="font-semibold text-sm cursor-pointer hover:text-slate-700 hover:underline flex items-center gap-1"
                          onClick={() => openStepDetails(s)}
                        >
                          {s.title}
                          <Info className="h-3 w-3 text-slate-400" />
                        </div>
                        <div className="text-xs text-slate-600">({s.type})</div>
                        <div className="text-xs text-slate-600 mt-1">{s.description}</div>
                      </div>
                      <Button 
                        onClick={() => addStep(s)} 
                        size="sm"
                        className="h-7 flex-shrink-0"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        追加
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Middle: Canvas */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">シナリオステップ</CardTitle>
            <div className="flex gap-2 mt-2">
              <Button 
                onClick={() => runScenario()} 
                disabled={loading}
                variant={loading ? "secondary" : "default"}
              >
                <Play className="h-4 w-4 mr-2" />
                {loading ? "実行中..." : "シナリオを実行"}
              </Button>
              <Button
                onClick={() => {
                  setShowJsonIO((v) => !v);
                  setJsonImportText(JSON.stringify({ steps: scenarioSteps }, null, 2));
                }}
                variant="outline"
              >
                <FileJson className="h-4 w-4 mr-2" />
                {showJsonIO ? "JSONを閉じる" : "JSON"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>

            {showJsonIO && (
              <div className="grid grid-cols-[1fr_200px] gap-2 mb-4 p-3 bg-slate-50 rounded-lg">
                <Textarea
                  value={jsonImportText}
                  onChange={(e) => setJsonImportText(e.target.value)}
                  className="font-mono text-xs min-h-[160px]"
                />
                <div className="space-y-2">
                  <Button
                    onClick={() => {
                      try {
                        const obj = JSON.parse(jsonImportText);
                        if (!obj || !Array.isArray(obj.steps)) throw new Error("steps が配列ではありません");
                        setScenarioSteps(obj.steps);
                        setSelectedIndex(null);
                        setError(null);
                      } catch (e: any) {
                        setError("JSONインポート失敗: " + (e?.message ?? ""));
                      }
                    }}
                    className="w-full"
                    size="sm"
                  >
                    インポート
                  </Button>
                  <Button
                    onClick={() => {
                      setJsonImportText(JSON.stringify({ steps: scenarioSteps }, null, 2));
                    }}
                    className="w-full"
                    variant="outline"
                    size="sm"
                  >
                    書き出し
                  </Button>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {scenarioSteps.map((s, i) => (
                <div
                  key={i}
                  onClick={() => setSelectedIndex(i)}
                  className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                    selectedIndex === i 
                      ? 'border-slate-700 bg-slate-50' 
                      : 'border-slate-200 bg-white hover:border-slate-400'
                  }`}
                >
                  <div className="flex justify-between items-center gap-2">
                    <div>
                      <div className="font-semibold text-sm">#{i + 1} {s.type}</div>
                      <div className="text-xs text-slate-600 mt-1">
                        {Object.keys(s).filter((k) => k !== "type").slice(0, 3).map((k) => `${k}: ${String((s as any)[k])}`).join(", ")}
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        onClick={(e) => { e.stopPropagation(); moveStep(i, -1); }}
                        size="sm"
                        variant="ghost"
                        className="h-8 w-8 p-0"
                      >
                        <ChevronUp className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={(e) => { e.stopPropagation(); moveStep(i, 1); }}
                        size="sm"
                        variant="ghost"
                        className="h-8 w-8 p-0"
                      >
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={(e) => { e.stopPropagation(); duplicateStep(i); }}
                        size="sm"
                        variant="ghost"
                        className="h-8 w-8 p-0"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={(e) => { e.stopPropagation(); removeStep(i); }}
                        size="sm"
                        variant="ghost"
                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Right: Inspector */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">ステップ編集</CardTitle>
            {selectedIndex !== null && (
              <CardDescription>選択中: ステップ #{selectedIndex + 1}</CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {selectedIndex === null ? (
              <p className="text-sm text-slate-600">編集するステップを選択してください。</p>
            ) : (
              <>
                <Textarea
                  value={editorText}
                  onChange={(e) => setEditorText(e.target.value)}
                  className="font-mono text-xs min-h-[320px] mb-3"
                />
                <div className="flex gap-2">
                  <Button onClick={applyEditor} size="sm">
                    反映
                  </Button>
                  <Button
                    onClick={() => setEditorText(JSON.stringify(scenarioSteps[selectedIndex], null, 2))}
                    size="sm"
                    variant="outline"
                  >
                    元に戻す
                  </Button>
                </div>
              </>
            )}
            
            {error && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                エラー: {error}
              </div>
            )}
            
            {logs.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold text-sm mb-2">ログ</h4>
                <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                  {logs.map((l, i) => (
                    <li key={i}>{l}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {imgB64 && (
              <div className="mt-4">
                <h4 className="font-semibold text-sm mb-2">スクリーンショット</h4>
                <img 
                  src={`data:image/png;base64,${imgB64}`} 
                  alt="screenshot" 
                  className="border border-slate-200 max-w-full rounded" 
                />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4 text-slate-900">サンプルシナリオ</h2>
        <div className="grid grid-cols-3 gap-4">
          {samples.map((s) => (
            <Card key={s.id}>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">{s.title}</CardTitle>
                <CardDescription className="text-xs">{s.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => {
                    setScenarioSteps(s.steps);
                    setSelectedIndex(null);
                    setError(null);
                    setImgB64(null);
                    setLogs([]);
                  }}
                  className="w-full"
                  size="sm"
                >
                  適用
                </Button>
                <details className="mt-3">
                  <summary className="cursor-pointer text-xs text-slate-700">JSONを見る</summary>
                  <pre className="whitespace-pre-wrap bg-slate-50 p-2 rounded text-xs mt-2">
{JSON.stringify({ steps: s.steps }, null, 2)}
                  </pre>
                </details>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* ステップ詳細モーダル */}
      <Dialog open={showStepModal} onOpenChange={setShowStepModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedStep?.title}</DialogTitle>
            <DialogDescription>
              タイプ: {selectedStep?.type}
            </DialogDescription>
          </DialogHeader>
          
          {selectedStep && (
            <div className="space-y-4 mt-4">
              <div>
                <h4 className="font-semibold text-sm mb-2">説明</h4>
                <p className="text-sm text-slate-600">{selectedStep.description}</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-sm mb-2">使用例</h4>
                <pre className="bg-slate-50 p-3 rounded-lg text-xs overflow-x-auto">
{JSON.stringify(selectedStep.example, null, 2)}
                </pre>
              </div>
              
              <div>
                <h4 className="font-semibold text-sm mb-2">スキーマ</h4>
                <pre className="bg-slate-50 p-3 rounded-lg text-xs overflow-x-auto">
{JSON.stringify(selectedStep.schema, null, 2)}
                </pre>
              </div>
              
              <div className="flex justify-end gap-2 pt-4">
                <Button
                  onClick={() => {
                    addStep(selectedStep);
                    setShowStepModal(false);
                  }}
                  size="sm"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  このステップを追加
                </Button>
                <Button
                  onClick={() => setShowStepModal(false)}
                  variant="outline"
                  size="sm"
                >
                  閉じる
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}


