/**
 * RPA Agent Client
 * Python RPAエージェントとJSON-RPC over stdioで通信
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { spawn } from 'child_process';
import { EventEmitter } from 'events';
import * as path from 'path';
export class RPAClient extends EventEmitter {
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
    start() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.process) {
                throw new Error('Agent already started');
            }
            return new Promise((resolve, reject) => {
                var _a, _b;
                const args = [this.options.agentPath];
                if (this.options.debug) {
                    args.push('--debug');
                }
                this.process = spawn(this.options.pythonPath, args, {
                    stdio: ['pipe', 'pipe', 'pipe']
                });
                (_a = this.process.stdout) === null || _a === void 0 ? void 0 : _a.on('data', (data) => {
                    this.handleData(data.toString());
                });
                (_b = this.process.stderr) === null || _b === void 0 ? void 0 : _b.on('data', (data) => {
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
        });
    }
    /**
     * エージェントを停止
     */
    stop() {
        return __awaiter(this, void 0, void 0, function* () {
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
        });
    }
    /**
     * RPCメソッドを呼び出す
     */
    call(method, params) {
        return __awaiter(this, void 0, void 0, function* () {
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
                var _a;
                this.pendingRequests.set(id, { resolve, reject });
                const json = JSON.stringify(request);
                (_a = this.process.stdin) === null || _a === void 0 ? void 0 : _a.write(json + '\n');
                // タイムアウト設定
                setTimeout(() => {
                    if (this.pendingRequests.has(id)) {
                        this.pendingRequests.delete(id);
                        reject(new Error(`Request timeout: ${method}`));
                    }
                }, 30000);
            });
        });
    }
    /**
     * 通知を送信（レスポンスを期待しない）
     */
    notify(method, params) {
        var _a;
        if (!this.process) {
            throw new Error('Agent not started');
        }
        const notification = {
            jsonrpc: '2.0',
            method,
            params
        };
        const json = JSON.stringify(notification);
        (_a = this.process.stdin) === null || _a === void 0 ? void 0 : _a.write(json + '\n');
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
    ping() {
        return __awaiter(this, void 0, void 0, function* () {
            return this.call('ping');
        });
    }
    /**
     * 便利メソッド：機能取得
     */
    getCapabilities() {
        return __awaiter(this, void 0, void 0, function* () {
            return this.call('get_capabilities');
        });
    }
    /**
     * 便利メソッド：タスク実行
     */
    runTask(name, params) {
        return __awaiter(this, void 0, void 0, function* () {
            const result = yield this.call('run_task', { name, params });
            return result.task_id;
        });
    }
    /**
     * 便利メソッド：タスクキャンセル
     */
    cancelTask(taskId) {
        return __awaiter(this, void 0, void 0, function* () {
            return this.call('cancel_task', { task_id: taskId });
        });
    }
}
