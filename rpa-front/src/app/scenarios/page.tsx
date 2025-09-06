"use client";

import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, Plus, Pencil, Trash2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

type ScenarioItem = {
  id: string;
  name: string;
  description?: string | null;
  updated_at?: string | null;
  latest_version?: number | null;
};

export default function ScenariosPage() {
  const [items, setItems] = useState<ScenarioItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editId, setEditId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const fetchList = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/scenarios");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setItems(data.items ?? []);
    } catch (e: any) {
      setError(e?.message ?? "取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchList();
  }, []);

  const openEdit = (it: ScenarioItem) => {
    setEditId(it.id);
    setEditName(it.name);
    setEditDesc(it.description ?? "");
  };

  const submitEdit = async () => {
    if (!editId) return;
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`http://127.0.0.1:8000/scenarios/${editId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: editName, description: editDesc }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setEditId(null);
      await fetchList();
    } catch (e: any) {
      setError(e?.message ?? "更新に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = (id: string) => {
    setConfirmDeleteId(id);
  };

  const submitDelete = async () => {
    if (!confirmDeleteId) return;
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`http://127.0.0.1:8000/scenarios/${confirmDeleteId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setConfirmDeleteId(null);
      await fetchList();
    } catch (e: any) {
      setError(e?.message ?? "削除に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="flex flex-row items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">シナリオ一覧</h1>
          <p className="text-gray-600 mt-2">
            RPAシナリオを管理・実行します
          </p>
        </div>
        <Button asChild>
          <a href="/scenarios/new">
            <Plus className="mr-2 h-4 w-4" />
            新規作成
          </a>
        </Button>
      </div>
      
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded-md mb-4">
          エラー: {error}
        </div>
      )}

      <div className="rounded-md border border-slate-200 bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[300px]">名前</TableHead>
              <TableHead>説明</TableHead>
              <TableHead className="w-[200px]">最終更新</TableHead>
              <TableHead className="w-[100px] text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.length === 0 && !loading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-slate-500 py-8">
                  データがありません
                </TableCell>
              </TableRow>
            ) : (
              items.map((it) => (
                <TableRow key={it.id}>
                  <TableCell className="font-medium text-slate-900">{it.name}</TableCell>
                  <TableCell className="text-slate-600">
                    {it.description || "-"}
                  </TableCell>
                  <TableCell className="text-sm text-slate-600">
                    {it.updated_at ? new Date(it.updated_at).toLocaleString("ja-JP") : "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">メニューを開く</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => openEdit(it)}>
                          <Pencil className="mr-2 h-4 w-4" />
                          編集
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          onClick={() => confirmDelete(it.id)}
                          className="text-red-600"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          削除
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {loading && (
        <div className="text-center py-4 text-slate-500">
          読み込み中...
        </div>
      )}

      {/* 編集ダイアログ */}
      <Dialog open={!!editId} onOpenChange={(open) => !open && setEditId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>シナリオを編集</DialogTitle>
            <DialogDescription>
              シナリオの名前と説明を編集します
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">名前</Label>
              <Input
                id="name"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="シナリオ名を入力"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">説明</Label>
              <Textarea
                id="description"
                value={editDesc}
                onChange={(e) => setEditDesc(e.target.value)}
                rows={4}
                placeholder="シナリオの説明を入力"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditId(null)}>
              キャンセル
            </Button>
            <Button onClick={submitEdit}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 削除確認ダイアログ */}
      <Dialog open={!!confirmDeleteId} onOpenChange={(open) => !open && setConfirmDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>削除の確認</DialogTitle>
            <DialogDescription>
              このシナリオを削除しますか？この操作は取り消せません。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmDeleteId(null)}>
              キャンセル
            </Button>
            <Button variant="destructive" onClick={submitDelete}>
              削除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}