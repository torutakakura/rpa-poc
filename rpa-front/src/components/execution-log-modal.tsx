"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Download, CheckCircle, XCircle, Clock, FileDown } from "lucide-react";

interface ExecutionResult {
  index: number;
  type: string;
  ok: boolean;
  error?: string;
  image_base64?: string;
  file_data?: any;
}

interface ExecutionLogModalProps {
  open: boolean;
  onClose: () => void;
  loading: boolean;
  results: ExecutionResult[];
  logs: string[];
}

export function ExecutionLogModal({
  open,
  onClose,
  loading,
  results,
  logs,
}: ExecutionLogModalProps) {
  const downloadFile = (result: ExecutionResult) => {
    if (result.image_base64) {
      // スクリーンショットをダウンロード
      const link = document.createElement("a");
      link.href = `data:image/png;base64,${result.image_base64}`;
      link.download = `screenshot_step_${result.index + 1}.png`;
      link.click();
    } else if (result.file_data) {
      // その他のファイルをダウンロード
      // TODO: ファイルタイプに応じた処理
      console.log("Download file:", result.file_data);
    }
  };

  const hasDownloadableContent = (result: ExecutionResult) => {
    return result.image_base64 || result.file_data;
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>実行ログ</DialogTitle>
          <DialogDescription>
            シナリオの実行結果とログを確認できます
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Clock className="h-6 w-6 mr-2 animate-spin text-slate-500" />
              <span className="text-slate-600">実行中...</span>
            </div>
          ) : (
            <>
              {/* 実行結果サマリー */}
              {results.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-slate-700">実行結果</h3>
                  <div className="space-y-2">
                    {results.map((result, idx) => (
                      <Card key={idx} className="shadow-none">
                        <CardContent className="p-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              {result.ok ? (
                                <CheckCircle className="h-5 w-5 text-green-600" />
                              ) : (
                                <XCircle className="h-5 w-5 text-red-600" />
                              )}
                              <div>
                                <div className="font-medium text-sm">
                                  Step {result.index + 1}: {result.type}
                                </div>
                                {result.error && (
                                  <div className="text-xs text-red-600 mt-1">
                                    エラー: {result.error}
                                  </div>
                                )}
                              </div>
                            </div>
                            {hasDownloadableContent(result) && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => downloadFile(result)}
                                className="h-8"
                              >
                                <Download className="h-3 w-3 mr-1" />
                                ダウンロード
                              </Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* 詳細ログ */}
              {logs.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-slate-700">詳細ログ</h3>
                  <Card className="shadow-none">
                    <CardContent className="p-3">
                      <pre className="text-xs font-mono text-slate-600 whitespace-pre-wrap">
                        {logs.join("\n")}
                      </pre>
                    </CardContent>
                  </Card>
                </div>
              )}

              {results.length === 0 && logs.length === 0 && (
                <div className="text-center py-8 text-slate-500">
                  実行結果がありません
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button onClick={onClose} variant="outline">
            閉じる
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}