#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const electronDir = path.resolve(__dirname, "..");
const repoRoot = path.resolve(electronDir, "..");
const agentDir = path.resolve(repoRoot, "rpa-agent");

function fail(message) {
  console.error(`\n[dist-win] ${message}`);
  process.exit(1);
}

if (process.platform !== "win32") {
  fail("Windows 向けインストーラーは Windows 環境でのみビルドできます。");
}

if (!existsSync(agentDir)) {
  fail(`Python agent ディレクトリが見つかりません: ${agentDir}`);
}

function resolvePython() {
  // Python 3.12を優先的に使用
  const candidates = [["python"]];

  for (const candidate of candidates) {
    const [cmd, ...args] = Array.isArray(candidate) ? candidate : [candidate];
    const result = spawnSync(cmd, [...args, "--version"], { stdio: "ignore" });
    if (result.status === 0) {
      return Array.isArray(candidate) ? candidate : [candidate];
    }
  }
  return null;
}

function run(command, args, options = {}) {
  console.log(`\n[dist-win] ${command} ${args.join(" ")}`);
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
    ...options,
  });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`${command} exited with code ${result.status}`);
  }
}

try {
  const pythonCmd = resolvePython();
  if (!pythonCmd) {
    fail(
      "Python が見つかりませんでした。Windows に Python 3.12 以上をインストールしてください。"
    );
  }

  console.log(`\n[dist-win] Using Python: ${pythonCmd.join(" ")}`);

  // 依存関係をインストール
  run(
    pythonCmd[0],
    [...pythonCmd.slice(1), "-m", "pip", "install", "--upgrade", "pip"],
    { cwd: agentDir }
  );
  run(
    pythonCmd[0],
    [...pythonCmd.slice(1), "-m", "pip", "install", "-r", "requirements.txt"],
    { cwd: agentDir }
  );

  // PyInstaller でエージェントをビルド
  run(
    pythonCmd[0],
    [
      ...pythonCmd.slice(1),
      "-m",
      "PyInstaller",
      "--onefile",
      "--noconfirm",
      "--name",
      "rpa_agent",
      "rpa_agent.py",
    ],
    { cwd: agentDir }
  );

  const distDir = path.join(agentDir, "dist");
  const agentBinary = path.join(distDir, "rpa_agent.exe");
  if (!existsSync(agentBinary)) {
    fail(`PyInstaller の出力が見つかりません: ${agentBinary}`);
  }

  // release ディレクトリを確実に作成
  mkdirSync(path.join(electronDir, "release"), { recursive: true });

  const pnpmCmd = process.platform === "win32" ? "pnpm.cmd" : "pnpm";
  // 依存関係をインストール
  run(pnpmCmd, ["install"], { cwd: electronDir });
  run(pnpmCmd, ["run", "dist:electron-only"], { cwd: electronDir });

  console.log("\n[dist-win] Windows インストーラーの作成が完了しました。");
} catch (error) {
  fail(error.message);
}
