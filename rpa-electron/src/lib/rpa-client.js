"use strict";
/**
 * RPA Agent Client
 * Python RPAエージェントとJSON-RPC over stdioで通信
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.RPAClient = void 0;
const child_process_1 = require("child_process");
const events_1 = require("events");
const path = __importStar(require("path"));
class RPAClient extends events_1.EventEmitter {
    constructor(options = {}) {
        super();
        this.process = null;
        this.requestId = 0;
        this.pendingRequests = new Map();
        this.buffer = '';
        this.options = {
            pythonPath: options.pythonPath || 'python3',
            agentPath: options.agentPath || path.join(__dirname, '../../rpa-agent/rpa_agent.py'),
            debug: options.debug || false
        };
    }
    /**
     * エージェントを起動
     */
    async start() {
        if (this.process) {
            throw new Error('Agent already started');
        }
        return new Promise((resolve, reject) => {
            const args = [this.options.agentPath];
            if (this.options.debug) {
                args.push('--debug');
            }
            this.process = (0, child_process_1.spawn)(this.options.pythonPath, args, {
                stdio: ['pipe', 'pipe', 'pipe']
            });
            this.process.stdout?.on('data', (data) => {
                this.handleData(data.toString());
            });
            this.process.stderr?.on('data', (data) => {
                console.error('Agent stderr:', data.toString());
            });
            this.process.on('error', (error) => {
                this.emit('error', error);
                reject(error);
            });
            this.process.on('exit', (code, signal) => {
                this.emit('exit', { code, signal });
                this.cleanup();
            });
            // agent_ready 通知を待つ
            const readyHandler = () => {
                this.off('agent_ready', readyHandler);
                resolve();
            };
            this.once('agent_ready', readyHandler);
            // タイムアウト設定
            setTimeout(() => {
                this.off('agent_ready', readyHandler);
                reject(new Error('Agent startup timeout'));
            }, 5000);
        });
    }
    /**
     * エージェントを停止
     */
    async stop() {
        if (!this.process) {
            return;
        }
        return new Promise((resolve) => {
            const exitHandler = () => {
                resolve();
            };
            this.once('exit', exitHandler);
            this.process.kill('SIGTERM');
            // 強制終了タイムアウト
            setTimeout(() => {
                this.off('exit', exitHandler);
                if (this.process) {
                    this.process.kill('SIGKILL');
                }
                resolve();
            }, 3000);
        });
    }
    /**
     * RPCメソッドを呼び出す
     */
    async call(method, params) {
        if (!this.process) {
            throw new Error('Agent not started');
        }
        const id = ++this.requestId;
        const request = {
            jsonrpc: '2.0',
            method,
            params,
            id
        };
        return new Promise((resolve, reject) => {
            this.pendingRequests.set(id, { resolve, reject });
            const json = JSON.stringify(request);
            this.process.stdin?.write(json + '\n');
            // タイムアウト設定
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error(`Request timeout: ${method}`));
                }
            }, 30000);
        });
    }
    /**
     * 通知を送信（レスポンスを期待しない）
     */
    notify(method, params) {
        if (!this.process) {
            throw new Error('Agent not started');
        }
        const notification = {
            jsonrpc: '2.0',
            method,
            params
        };
        const json = JSON.stringify(notification);
        this.process.stdin?.write(json + '\n');
    }
    /**
     * 標準出力からのデータを処理
     */
    handleData(data) {
        this.buffer += data;
        const lines = this.buffer.split('\n');
        // 最後の不完全な行を保持
        this.buffer = lines.pop() || '';
        for (const line of lines) {
            if (line.trim()) {
                try {
                    const message = JSON.parse(line);
                    this.handleMessage(message);
                }
                catch (error) {
                    console.error('Failed to parse JSON-RPC message:', line, error);
                }
            }
        }
    }
    /**
     * JSON-RPCメッセージを処理
     */
    handleMessage(message) {
        // レスポンス
        if ('id' in message && ('result' in message || 'error' in message)) {
            const response = message;
            const pending = this.pendingRequests.get(response.id);
            if (pending) {
                this.pendingRequests.delete(response.id);
                if (response.error) {
                    pending.reject(new Error(response.error.message));
                }
                else {
                    pending.resolve(response.result);
                }
            }
        }
        // 通知
        else if ('method' in message && !('id' in message)) {
            const notification = message;
            this.emit(notification.method, notification.params);
        }
    }
    /**
     * クリーンアップ
     */
    cleanup() {
        this.process = null;
        this.buffer = '';
        // 未処理のリクエストをエラーで終了
        for (const [, pending] of this.pendingRequests) {
            pending.reject(new Error('Agent disconnected'));
        }
        this.pendingRequests.clear();
    }
    /**
     * 便利メソッド：ping
     */
    async ping() {
        return this.call('ping');
    }
    /**
     * 便利メソッド：機能取得
     */
    async getCapabilities() {
        return this.call('get_capabilities');
    }
    /**
     * 便利メソッド：タスク実行
     */
    async runTask(name, params) {
        const result = await this.call('run_task', { name, params });
        return result.task_id;
    }
    /**
     * 便利メソッド：タスクキャンセル
     */
    async cancelTask(taskId) {
        return this.call('cancel_task', { task_id: taskId });
    }
}
exports.RPAClient = RPAClient;