/**
 * RPA Operations List Component
 * カテゴリごとに操作一覧をアコーディオンで表示
 */

import { useState } from 'react'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Card, CardContent } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  AppWindow,
  Clock,
  Mouse,
  Keyboard,
  HardDrive,
  Type,
  GitBranch,
  Mail,
  Folder,
  FileSpreadsheet,
  FileText,
  Globe,
  Info,
  ChevronRight,
} from 'lucide-react'

// カテゴリアイコンのマッピング
const categoryIcons: Record<string, React.ReactNode> = {
  'A_アプリ・画面': <AppWindow className="h-4 w-4" />,
  'B_待機・終了・エラー': <Clock className="h-4 w-4" />,
  'C_マウス': <Mouse className="h-4 w-4" />,
  'D_キーボード': <Keyboard className="h-4 w-4" />,
  'E_記憶': <HardDrive className="h-4 w-4" />,
  'F_文字抽出': <Type className="h-4 w-4" />,
  'G_分岐': <GitBranch className="h-4 w-4" />,
  'H_メール': <Mail className="h-4 w-4" />,
  'I_ファイル・フォルダ': <Folder className="h-4 w-4" />,
  'J_Excel': <FileSpreadsheet className="h-4 w-4" />,
  'K_CSV': <FileText className="h-4 w-4" />,
  'L_ウェブブラウザ': <Globe className="h-4 w-4" />,
}

// パラメータ情報の型定義
interface OperationParam {
  name: string
  type: string
  required: boolean
  description: string
  default?: any
}

// 操作パラメータの定義（サンプル）
const operationParams: Record<string, OperationParam[]> = {
  'アプリ/起動': [
    { name: 'app_path', type: 'string', required: true, description: 'アプリケーションのパス' },
    { name: 'args', type: 'string', required: false, description: '起動引数', default: '' },
    { name: 'wait', type: 'boolean', required: false, description: '起動を待つ', default: false },
  ],
  '画面/最前画面を覚える': [
    { name: 'storage_key', type: 'string', required: true, description: '記憶するキー名' },
  ],
  '秒': [
    { name: 'seconds', type: 'number', required: true, description: '待機時間（秒）' },
  ],
  '移動/座標': [
    { name: 'x', type: 'number', required: true, description: 'X座標' },
    { name: 'y', type: 'number', required: true, description: 'Y座標' },
  ],
  '入力/文字': [
    { name: 'text', type: 'string', required: true, description: '入力するテキスト' },
    { name: 'clear_before', type: 'boolean', required: false, description: '入力前にクリア', default: false },
  ],
  '環境情報': [
    { name: 'storage_key', type: 'string', required: true, description: '記憶するキー名' },
    { name: 'info_type', type: 'string', required: true, description: '情報タイプ（computer_name, user_name, os_version, ip_address）' },
  ],
  'ファイル・フォルダ名の変更': [
    { name: 'target_path', type: 'string', required: true, description: '対象パス' },
    { name: 'new_name', type: 'string', required: true, description: '新しい名前または移動先パス' },
    { name: 'keep_extension', type: 'boolean', required: false, description: '拡張子を保持', default: false },
  ],
}

interface OperationsListProps {
  operations: Record<string, string[]>
  onOperationSelect?: (category: string, operation: string) => void
}

export function OperationsList({ operations, onOperationSelect }: OperationsListProps) {
  const [selectedOperation, setSelectedOperation] = useState<{
    category: string
    operation: string
  } | null>(null)

  const handleOperationClick = (category: string, operation: string) => {
    setSelectedOperation({ category, operation })
    onOperationSelect?.(category, operation)
  }

  const getOperationParams = (operation: string): OperationParam[] => {
    // 操作名から基本形を抽出（例: "アプリ/起動" → "アプリ/起動"）
    const baseOperation = operation.split('（')[0]
    return operationParams[baseOperation] || []
  }

  return (
    <>
      <ScrollArea className="h-[500px] pr-4">
        <Accordion type="multiple" className="w-full">
          {Object.entries(operations).map(([category, ops]) => {
            // 空のカテゴリはスキップ
            if (!ops || ops.length === 0) return null

            return (
              <AccordionItem key={category} value={category}>
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-2">
                    {categoryIcons[category]}
                    <span className="font-medium">{category.substring(2)}</span>
                    <Badge variant="secondary" className="ml-2">
                      {ops.length}
                    </Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="grid gap-2 pl-6">
                    {ops.map((operation) => (
                      <Button
                        key={operation}
                        variant="ghost"
                        className="justify-start h-auto py-2 px-3 hover:bg-accent"
                        onClick={() => handleOperationClick(category, operation)}
                      >
                        <ChevronRight className="h-3 w-3 mr-2" />
                        <span className="text-sm">{operation}</span>
                        <Info className="h-3 w-3 ml-auto opacity-50" />
                      </Button>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            )
          })}
        </Accordion>
      </ScrollArea>

      {/* パラメータ表示モーダル */}
      <Dialog open={!!selectedOperation} onOpenChange={() => setSelectedOperation(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {selectedOperation?.operation}
            </DialogTitle>
            <DialogDescription>
              カテゴリ: {selectedOperation?.category.substring(2)}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <h3 className="text-sm font-medium">必要なパラメータ</h3>

            {selectedOperation && (
              <div className="space-y-3">
                {getOperationParams(selectedOperation.operation).length > 0 ? (
                  getOperationParams(selectedOperation.operation).map((param) => (
                    <Card key={param.name}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <code className="text-sm font-mono bg-muted px-2 py-0.5 rounded">
                                {param.name}
                              </code>
                              {param.required && (
                                <Badge variant="destructive" className="text-xs">
                                  必須
                                </Badge>
                              )}
                              <Badge variant="outline" className="text-xs">
                                {param.type}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {param.description}
                            </p>
                            {param.default !== undefined && (
                              <p className="text-xs text-muted-foreground">
                                デフォルト値: <code className="bg-muted px-1 rounded">{JSON.stringify(param.default)}</code>
                              </p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Card>
                    <CardContent className="p-4">
                      <p className="text-sm text-muted-foreground">
                        この操作のパラメータ情報はまだ定義されていません。
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            <div className="pt-2">
              <h3 className="text-sm font-medium mb-2">実行例</h3>
              <Card>
                <CardContent className="p-4">
                  <pre className="text-xs font-mono bg-muted p-3 rounded overflow-x-auto">
{`{
  "category": "${selectedOperation?.category}",
  "operation": "${selectedOperation?.operation}",
  "params": ${JSON.stringify(
    getOperationParams(selectedOperation?.operation || '').reduce((acc, param) => {
      acc[param.name] = param.default !== undefined ? param.default : `<${param.type}>`
      return acc
    }, {} as Record<string, any>),
    null,
    2
  )}
}`}
                  </pre>
                </CardContent>
              </Card>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}