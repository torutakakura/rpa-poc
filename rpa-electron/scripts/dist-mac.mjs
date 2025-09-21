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
  console.error(`\n[dist-mac] ${message}`);
  process.exit(1);
}

function run(command, args, options = {}) {
  console.log(`\n[dist-mac] ${command} ${args.join(" ")}`);
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: false,
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
  console.log(`\n[dist-mac] macOS向けビルドを開始します`);
  console.log(`[dist-mac] プラットフォーム: ${process.platform}`);
  console.log(`[dist-mac] アーキテクチャ: ${process.arch}`);

  if (!existsSync(agentDir)) {
    fail(`Python agentディレクトリが見つかりません: ${agentDir}`);
  }

  // Python3の確認
  console.log("\n[dist-mac] Pythonバージョンを確認中...");
  const pythonCmd = "python3";
  run(pythonCmd, ["--version"], { cwd: agentDir });

  // enum34パッケージの問題を事前に解決
  console.log("\n[dist-mac] PyInstaller非互換パッケージをチェック中...");
  try {
    // enum34がインストールされているか確認し、あれば削除
    const checkEnum34 = spawnSync(pythonCmd, ["-m", "pip", "show", "enum34"], {
      stdio: "pipe",
      cwd: agentDir,
    });
    
    if (checkEnum34.status === 0) {
      console.log("[dist-mac] enum34パッケージを削除中（PyInstallerとの互換性問題）...");
      run(pythonCmd, ["-m", "pip", "uninstall", "-y", "enum34"], { cwd: agentDir });
    }
  } catch (e) {
    // enum34が存在しない場合は何もしない
  }

  // 依存関係をインストール
  console.log("\n[dist-mac] Python依存関係をインストール中...");
  run(pythonCmd, ["-m", "pip", "install", "--upgrade", "pip"], { cwd: agentDir });
  run(pythonCmd, ["-m", "pip", "install", "-r", "requirements.txt"], { cwd: agentDir });

  // PyInstallerでエージェントをビルド
  console.log("\n[dist-mac] PyInstallerでPythonエージェントをビルド中...");
  run(
    pythonCmd,
    [
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

  // ビルド結果の確認
  const distDir = path.join(agentDir, "dist");
  const agentBinary = path.join(distDir, "rpa_agent");
  if (!existsSync(agentBinary)) {
    fail(`PyInstallerの出力が見つかりません: ${agentBinary}`);
  }

  console.log(`\n[dist-mac] Pythonエージェントのビルドが完了しました: ${agentBinary}`);

  // releaseディレクトリを作成
  mkdirSync(path.join(electronDir, "release"), { recursive: true });

  // Electronアプリをビルド
  console.log("\n[dist-mac] Electronアプリをビルド中...");
  run("pnpm", ["install"], { cwd: electronDir });
  run("pnpm", ["build"], { cwd: electronDir });

  // macOS向けインストーラーを作成
  console.log("\n[dist-mac] macOS向けインストーラーを作成中...");
  run("pnpm", ["exec", "electron-builder", "--mac"], { cwd: electronDir });

  console.log("\n[dist-mac] ✅ macOS向けビルドが完了しました！");
  console.log(`[dist-mac] 📦 出力先: ${path.join(electronDir, "release")}`);
} catch (error) {
  fail(error.message);
}
