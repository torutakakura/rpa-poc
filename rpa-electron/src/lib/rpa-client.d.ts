/**
 * RPA Agent Client
 * Python RPAエージェントとJSON-RPC over stdioで通信
 */
import { EventEmitter } from 'events';
export interface RPAClientOptions {
    pythonPath?: string;
    agentPath?: string;
    debug?: boolean;
}
export declare class RPAClient extends EventEmitter {
    private process;
    private requestId;
    private pendingRequests;
    private buffer;
    private options;
    constructor(options?: RPAClientOptions);
    /**
     * エージェントを起動
     */
    start(): Promise<void>;
    /**
     * エージェントを停止
     */
    stop(): Promise<void>;
    /**
     * RPCメソッドを呼び出す
     */
    call(method: string, params?: any): Promise<any>;
    /**
     * 通知を送信（レスポンスを期待しない）
     */
    notify(method: string, params?: any): void;
    /**
     * 標準出力からのデータを処理
     */
    private handleData;
    /**
     * JSON-RPCメッセージを処理
     */
    private handleMessage;
    /**
     * クリーンアップ
     */
    private cleanup;
    /**
     * 便利メソッド：ping
     */
    ping(): Promise<any>;
    /**
     * 便利メソッド：機能取得
     */
    getCapabilities(): Promise<any>;
    /**
     * 便利メソッド：タスク実行
     */
    runTask(name: string, params?: any): Promise<string>;
    /**
     * 便利メソッド：タスクキャンセル
     */
    cancelTask(taskId: string): Promise<any>;
    /**
     * 便利メソッド：Excel読み込み
     */
    excelRead(filePath: string, sheetName?: string): Promise<any>;
    /**
     * 便利メソッド：Excel書き込み
     */
    excelWrite(filePath: string, data: any[][], sheetName?: string): Promise<any>;
}
