"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface StepEditorModalProps {
  open: boolean;
  onClose: () => void;
  step: any;
  stepIndex: number;
  onSave: (updatedStep: any) => void;
}

export function StepEditorModal({
  open,
  onClose,
  step,
  stepIndex,
  onSave,
}: StepEditorModalProps) {
  const [editorText, setEditorText] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (step) {
      setEditorText(JSON.stringify(step, null, 2));
      setError(null);
    }
  }, [step]);

  const handleSave = () => {
    try {
      const updatedStep = JSON.parse(editorText);
      onSave(updatedStep);
      onClose();
      setError(null);
    } catch (e: any) {
      setError("JSONが不正です: " + (e?.message ?? ""));
    }
  };

  const handleReset = () => {
    setEditorText(JSON.stringify(step, null, 2));
    setError(null);
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>ステップ編集</DialogTitle>
          <DialogDescription>
            ステップ #{stepIndex + 1} のJSONを編集できます
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Textarea
            value={editorText}
            onChange={(e) => setEditorText(e.target.value)}
            className="font-mono text-xs min-h-[400px]"
            placeholder="JSON形式でステップを編集..."
          />

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
              {error}
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button onClick={handleReset} variant="outline">
              元に戻す
            </Button>
            <Button onClick={onClose} variant="outline">
              キャンセル
            </Button>
            <Button onClick={handleSave}>
              保存
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}