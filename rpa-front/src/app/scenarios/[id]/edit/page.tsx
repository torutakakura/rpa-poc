"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { 
  ArrowLeft, 
  ChevronUp, 
  ChevronDown, 
  Copy, 
  Trash2, 
  Plus, 
  Info,
  Save,
  Play,
  Edit2
} from "lucide-react";
import { ExecutionLogModal } from "@/components/execution-log-modal";
import { StepEditorModal } from "@/components/step-editor-modal";
import { AIChat } from "@/components/ai-chat";

export default function EditScenarioPage() {
  const router = useRouter();
  const params = useParams();
  const scenarioId = params.id as string;
  
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // ステップビルダー関連の状態
  const [availableSteps, setAvailableSteps] = useState<any[]>([]);
  const [filter, setFilter] = useState("");
  const [scenarioSteps, setScenarioSteps] = useState<any[]>([]);
  const [selectedStep, setSelectedStep] = useState<any | null>(null);
  const [showStepModal, setShowStepModal] = useState(false);
  
  // ステップ編集モーダル関連
  const [editingStepIndex, setEditingStepIndex] = useState<number | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  
  // 実行関連の状態
  const [executing, setExecuting] = useState(false);
  const [executionResults, setExecutionResults] = useState<any[]>([]);
  const [executionLogs, setExecutionLogs] = useState<string[]>([]);
  const [showExecutionLog, setShowExecutionLog] = useState(false);

  // 既存シナリオを取得
  useEffect(() => {
    const fetchScenario = async () => {
      try {
        setLoading(true);
        const res = await fetch(`http://127.0.0.1:8000/scenarios/${scenarioId}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setName(data.name ?? "");
        setDescription(data.description ?? "");
        setScenarioSteps(data.steps ?? []);
      } catch (e: any) {
        setError(e?.message ?? "シナリオの取得に失敗しました");
      } finally {
        setLoading(false);
      }
    };
    if (scenarioId) {
      fetchScenario();
    }
  }, [scenarioId]);

  // ステップ一覧を取得
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


  // ステップ操作関数
  const addStep = (meta: any) => {
    const example = meta?.example ?? { type: meta?.type };
    setScenarioSteps((prev) => [...prev, example]);
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
  };

  const removeStep = (index: number) => {
    setScenarioSteps((prev) => prev.filter((_, i) => i !== index));
  };

  const duplicateStep = (index: number) => {
    setScenarioSteps((prev) => {
      const copy = JSON.parse(JSON.stringify(prev[index]));
      const next = [...prev.slice(0, index + 1), copy, ...prev.slice(index + 1)];
      return next;
    });
  };

  const editStep = (index: number) => {
    setEditingStepIndex(index);
    setShowEditModal(true);
  };

  const saveEditedStep = (updatedStep: any) => {
    if (editingStepIndex !== null) {
      setScenarioSteps((prev) => 
        prev.map((s, i) => (i === editingStepIndex ? updatedStep : s))
      );
    }
  };

  const executeScenario = async () => {
    if (scenarioSteps.length === 0) {
      setError("実行するステップがありません");
      return;
    }
    
    setExecuting(true);
    setExecutionResults([]);
    setExecutionLogs([]);
    setShowExecutionLog(true);
    setError(null);
    
    try {
      const res = await fetch("http://127.0.0.1:8000/run_scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ steps: scenarioSteps }),
      });
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const data = await res.json();
      setExecutionResults(data.results ?? []);
      setExecutionLogs(data.logs ?? []);
      
      // エラーがあれば表示
      const failedSteps = data.results?.filter((r: any) => !r.ok) ?? [];
      if (failedSteps.length > 0) {
        setError(`${failedSteps.length}個のステップが失敗しました`);
      }
    } catch (e: any) {
      setError(e?.message ?? "実行に失敗しました");
    } finally {
      setExecuting(false);
    }
  };

  const submit = async () => {
    if (!name.trim()) {
      setError("名前を入力してください");
      return;
    }
    if (scenarioSteps.length === 0) {
      setError("少なくとも1つのステップを追加してください");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://127.0.0.1:8000/scenarios/${scenarioId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          name, 
          description,
          steps: scenarioSteps 
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await router.push("/scenarios");
    } catch (e: any) {
      setError(e?.message ?? "更新に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  if (loading && scenarioSteps.length === 0) {
    return (
      <div className="container mx-auto py-6 px-4">
        <div className="text-center text-slate-500">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 px-4 flex flex-col h-screen">
      <div className="mb-6">
        <Button
          onClick={() => router.push("/scenarios")}
          variant="ghost"
          size="sm"
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          一覧へ戻る
        </Button>
        <h1 className="text-3xl font-bold text-slate-900">シナリオを編集</h1>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
          エラー: {error}
        </div>
      )}

      {/* 基本情報 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>基本情報</CardTitle>
          <CardDescription>
            シナリオの名前と説明を編集してください
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                名前 <span className="text-red-500">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例: 毎朝のレポート作成"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">
                説明 <span className="text-slate-500 text-sm">（任意）</span>
              </Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="シナリオの概要"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ステップビルダー */}
      <div className="grid grid-cols-[300px_1fr_360px] gap-4 flex-1 overflow-hidden">
        {/* Left: ステップパレット */}
        <Card className="flex flex-col h-full overflow-hidden">
          <CardHeader className="pb-3 flex-shrink-0">
            <CardTitle className="text-lg">ステップ一覧</CardTitle>
            <div className="mt-2">
              <Input
                placeholder="ステップ検索"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full"
              />
            </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-4">
            <div className="flex flex-col gap-2">
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
                          <Plus className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
            </div>
          </CardContent>
        </Card>

        {/* Middle: シナリオステップ */}
        <Card className="flex flex-col h-full overflow-hidden">
          <CardHeader className="pb-3 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">シナリオステップ</CardTitle>
                <CardDescription className="text-xs mt-1">
                  {scenarioSteps.length === 0 ? "ステップを追加してください" : `${scenarioSteps.length} ステップ`}
                </CardDescription>
              </div>
              <Button
                onClick={executeScenario}
                disabled={executing || scenarioSteps.length === 0}
                size="sm"
                variant="outline"
              >
                <Play className="h-4 w-4 mr-1" />
                {executing ? "実行中..." : "テスト実行"}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {scenarioSteps.length === 0 ? (
                <div className="text-center text-slate-500 py-8">
                  左のパレットからステップを追加してください
                </div>
              ) : (
                scenarioSteps.map((s, i) => (
                  <div
                    key={i}
                    className="border rounded-lg p-3 transition-colors border-slate-200 bg-white hover:border-slate-400"
                  >
                    <div className="flex justify-between items-center gap-2">
                      <div className="flex-1">
                        <div className="font-semibold text-sm">#{i + 1} {s.type}</div>
                        <div className="text-xs text-slate-600 mt-1">
                          {Object.keys(s).filter((k) => k !== "type").slice(0, 3).map((k) => `${k}: ${String((s as any)[k])}`).join(", ")}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          onClick={() => editStep(i)}
                          size="sm"
                          variant="ghost"
                          className="h-8 w-8 p-0"
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          onClick={() => moveStep(i, -1)}
                          size="sm"
                          variant="ghost"
                          className="h-8 w-8 p-0"
                        >
                          <ChevronUp className="h-4 w-4" />
                        </Button>
                        <Button
                          onClick={() => moveStep(i, 1)}
                          size="sm"
                          variant="ghost"
                          className="h-8 w-8 p-0"
                        >
                          <ChevronDown className="h-4 w-4" />
                        </Button>
                        <Button
                          onClick={() => duplicateStep(i)}
                          size="sm"
                          variant="ghost"
                          className="h-8 w-8 p-0"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          onClick={() => removeStep(i)}
                          size="sm"
                          variant="ghost"
                          className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Right: AIチャット */}
        <div className="h-full">
          <AIChat 
            onSuggestSteps={(steps) => {
              // AIから提案されたステップを追加
              setScenarioSteps((prev) => [...prev, ...steps]);
            }}
          />
        </div>
      </div>

      {/* 保存ボタン */}
      <div className="flex justify-end gap-2 pt-4 pb-2 flex-shrink-0">
        <Button
          onClick={() => router.push("/scenarios")}
          variant="outline"
          size="lg"
        >
          キャンセル
        </Button>
        <Button
          onClick={submit}
          disabled={loading}
          size="lg"
        >
          <Save className="h-4 w-4 mr-2" />
          {loading ? "更新中..." : "変更を保存"}
        </Button>
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

      {/* 実行ログモーダル */}
      <ExecutionLogModal
        open={showExecutionLog}
        onClose={() => setShowExecutionLog(false)}
        loading={executing}
        results={executionResults}
        logs={executionLogs}
      />

      {/* ステップ編集モーダル */}
      <StepEditorModal
        open={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingStepIndex(null);
        }}
        step={editingStepIndex !== null ? scenarioSteps[editingStepIndex] : null}
        stepIndex={editingStepIndex ?? 0}
        onSave={saveEditedStep}
      />
    </div>
  );
}