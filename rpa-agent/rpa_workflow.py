"""
RPA Workflow Builder using MCP Tools and LangChain
MCPサーバーからツールを動的に取得し、LangChainエージェントを使用して
ユーザーストーリーに基づいたワークフローを生成します。
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from deepmcpagent import HTTPServerSpec, build_deep_agent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import os


class RPAWorkflowBuilder:
    """RPAワークフロービルダー - MCPツールを使用してワークフローを構築"""

    def __init__(
        self,
        mcp_server_url: str = "http://localhost:8080/mcp",
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None
    ):
        """
        初期化

        Args:
            mcp_server_url: MCPサーバーのURL
            model_name: 使用するLLMモデル名
            api_key: OpenAI APIキー（環境変数から取得する場合は不要）
        """
        self.mcp_server_url = mcp_server_url
        self.model_name = model_name

        # APIキーの設定
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        # LangChainモデルの初期化
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            max_tokens=4000  # gpt-4oの大きなコンテキストを活用
        )

        self.agent = None
        self.loader = None
        self.available_tools = []

    async def initialize_agent(self):
        """MCPサーバーに接続してエージェントを初期化"""

        # MCPサーバーの設定
        servers = {
            "rpa": HTTPServerSpec(
                url=self.mcp_server_url,
                transport="http",  # または "sse"
                # 必要に応じて認証ヘッダーを追加
                # headers={"Authorization": "Bearer <token>"},
            ),
        }

        # システムプロンプトの設定
        instructions = """あなたはRPAワークフロー設計の専門家です。
        ユーザーのストーリーや要求を分析し、適切なRPAツールを組み合わせて
        効率的なワークフローを構築してください。

        【重要】出力は必ず以下のJSON形式で行ってください：
        {
          "name": "ワークフロー名",
          "description": "ワークフローの説明",
          "version": "1.0.0",
          "steps": [
            {
              "id": "step-001",
              "category": "カテゴリ名",
              "operation": "操作名",
              "params": {},
              "description": "ステップの説明"
            }
          ]
        }

        【利用可能なカテゴリと主な操作】
        - A_アプリ・画面: アプリ起動、スクリーンショット
        - B_待機・終了・エラー: 待機、エラー処理
        - C_マウス: クリック、ダブルクリック、右クリック、マウス移動
        - D_キーボード: 文字入力、キー入力、ショートカット
        - E_記憶: 変数に保存、変数から読み込み
        - I_ファイル・フォルダ: フォルダ作成、ファイル書き込み、コピー、リネーム
        - J_Excel: Excel開く、セル書き込み、範囲書き込み、Excel保存、Excel閉じる
        - K_CSV: CSV読み込み、CSV書き込み、CSV追記
        - L_ウェブブラウザ: ブラウザ起動、要素入力、要素クリック
        
        【注意事項】
        1. ステップIDは必ず"step-001", "step-002"の形式で連番にする
        2. 各ステップには適切なカテゴリと操作を選択する
        3. paramsには具体的な値を設定する（例: file_path, cell, text等）
        4. 実行順序を考慮し、必要に応じて待機を入れる
        5. ユーザーストーリーに基づいて具体的なステップを生成する
        """

        # エージェントの構築
        self.agent, self.loader = await build_deep_agent(
            servers=servers,
            model=self.llm,
            instructions=instructions
        )

        # 利用可能なツールの取得
        self.available_tools = await self._get_available_tools()

        print(f"✅ エージェントが初期化されました。{len(self.available_tools)}個のツールが利用可能です。")

    async def _get_available_tools(self) -> List[Dict[str, Any]]:
        """MCPサーバーから利用可能なツールのリストを取得"""
        if self.loader:
            tools_info = await self.loader.list_tool_info()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema
                }
                for tool in tools_info
            ]
        return []

    def show_available_tools(self):
        """利用可能なツールを表示"""
        print("\n📋 利用可能なRPAツール:")
        print("-" * 50)
        for tool in self.available_tools:
            print(f"• {tool['name']}: {tool['description']}")
        print("-" * 50)

    async def build_workflow(self, user_story: str, workflow_name: str = None) -> Dict[str, Any]:
        """
        ユーザーストーリーからRPAワークフローを構築

        Args:
            user_story: ユーザーのストーリーや要求
            workflow_name: ワークフロー名（指定しない場合は自動生成）

        Returns:
            生成されたワークフロー（JSONインポート形式）
        """
        if not self.agent:
            await self.initialize_agent()

        # プロンプトの構築
        prompt = f"""
        以下のユーザーストーリーを分析し、RPAワークフローをJSON形式で生成してください。

        【ユーザーストーリー】
        {user_story}

        【出力形式】
        以下の形式で出力してください：
        ```json
        {{
          "name": "ワークフロー名",
          "description": "ワークフローの説明",
          "version": "1.0.0",
          "steps": [
            {{
              "id": "step-001",
              "category": "カテゴリ名",
              "operation": "操作名",
              "params": {{
                "パラメータ名": "値"
              }},
              "description": "ステップの説明"
            }}
          ]
        }}
        ```

        【カテゴリ一覧】
        - A_アプリ・画面: アプリケーション操作
        - B_待機・終了・エラー: 待機やエラー処理
        - C_マウス: マウス操作
        - D_キーボード: キーボード操作
        - E_記憶: 変数操作
        - I_ファイル・フォルダ: ファイル操作
        - J_Excel: Excel操作
        - K_CSV: CSV操作
        - L_ウェブブラウザ: ブラウザ操作

        【注意事項】
        1. ステップIDは"step-001", "step-002"のように連番にする
        2. 各ステップには適切なカテゴリを選択する
        3. パラメータは操作に必要なものを適切に設定する
        4. 実行順序を考慮してステップを配置する
        """

        # エージェントの実行
        result = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": prompt}]
        })

        # 結果の解析
        workflow = self._parse_workflow_response(result)
        
        # ワークフロー名が指定されていれば設定
        if workflow_name and "name" in workflow:
            workflow["name"] = workflow_name

        return workflow

    def _parse_workflow_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """エージェントの応答からワークフローを解析"""

        # 最後のメッセージを取得
        messages = response.get("messages", [])
        if not messages:
            return {
                "name": "エラー",
                "description": "応答が空です",
                "version": "1.0.0",
                "steps": []
            }

        last_message = messages[-1]

        # AIMessageオブジェクトから内容を取得
        if hasattr(last_message, 'content'):
            content = last_message.content
        elif isinstance(last_message, dict):
            content = last_message.get("content", "")
        else:
            content = str(last_message)

        # デフォルトのワークフロー構造
        default_workflow = {
            "name": "Generated RPA Workflow",
            "description": "ユーザーストーリーに基づいて生成されたワークフロー",
            "version": "1.0.0",
            "steps": []
        }

        # JSON部分を抽出して解析
        try:
            import re
            json_pattern = r'```json\s*(.*?)\s*```'
            json_matches = re.findall(json_pattern, content, re.DOTALL)

            if json_matches:
                # JSONをパース
                workflow_data = json.loads(json_matches[0])
                
                # 正しい形式のワークフローを返す
                return {
                    "name": workflow_data.get("name", default_workflow["name"]),
                    "description": workflow_data.get("description", default_workflow["description"]),
                    "version": workflow_data.get("version", "1.0.0"),
                    "steps": workflow_data.get("steps", [])
                }
            else:
                # JSONブロックが見つからない場合、content全体をJSONとして解析を試みる
                try:
                    workflow_data = json.loads(content)
                    return {
                        "name": workflow_data.get("name", default_workflow["name"]),
                        "description": workflow_data.get("description", default_workflow["description"]),
                        "version": workflow_data.get("version", "1.0.0"),
                        "steps": workflow_data.get("steps", [])
                    }
                except:
                    print("⚠️ JSON形式のワークフローが見つかりませんでした")
                    return default_workflow
                    
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ ワークフローの解析中にエラーが発生しました: {e}")
            return default_workflow


    async def interactive_workflow_builder(self):
        """対話的なワークフロービルダー"""
        print("\n🤖 RPA ワークフロービルダーへようこそ！")
        print("ユーザーストーリーを入力して、RPAワークフローを生成します。")
        print("'quit'または'exit'で終了します。\n")

        # エージェントの初期化
        await self.initialize_agent()
        self.show_available_tools()

        while True:
            user_story = input("\n📝 ユーザーストーリーを入力してください: ").strip()

            if user_story.lower() in ['quit', 'exit']:
                print("👋 ワークフロービルダーを終了します。")
                break

            if not user_story:
                continue

            # ワークフロー名の入力（オプション）
            workflow_name = input("📌 ワークフロー名（Enterでスキップ）: ").strip()
            
            print("\n⏳ ワークフローを生成中...")

            try:
                # ワークフローの生成
                workflow = await self.build_workflow(user_story, workflow_name or None)

                # 結果の表示
                print("\n✨ 生成されたワークフロー:")
                print("=" * 60)
                print(json.dumps(workflow, ensure_ascii=False, indent=2))
                print("=" * 60)

                # ファイル保存の確認
                save = input("\n💾 このワークフローをファイルに保存しますか？ (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("📁 ファイル名（.json拡張子は自動追加）: ").strip()
                    if not filename:
                        filename = workflow.get("name", "workflow").replace(" ", "_")
                    
                    if not filename.endswith('.json'):
                        filename += '.json'
                    
                    # ファイルに保存
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(workflow, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ ワークフローを {filename} に保存しました。")

            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")
    
    def save_workflow_to_file(self, workflow: Dict[str, Any], filename: str):
        """
        ワークフローをJSONファイルに保存
        
        Args:
            workflow: 保存するワークフロー
            filename: 保存先ファイル名
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, ensure_ascii=False, indent=2)
        
        print(f"✅ ワークフローを {filename} に保存しました。")


async def main():
    """メイン関数 - サンプル使用例"""

    # ワークフロービルダーの初期化
    builder = RPAWorkflowBuilder(
        mcp_server_url="http://localhost:8080/mcp",
        model_name="gpt-4o"  # または "gpt-3.5-turbo"
    )

    print("=" * 60)
    print("📌 RPA ワークフロー生成システム")
    print("=" * 60)
    print()
    
    # モード選択
    print("実行モードを選択してください:")
    print("1. サンプルワークフロー生成")
    print("2. 対話的ワークフロービルダー")
    print("3. 終了")
    
    mode = input("\n選択 (1-3): ").strip()
    
    if mode == "1":
        # サンプル: Excel処理ワークフロー生成
        print("\n" + "=" * 60)
        print("📌 サンプル: Excel処理ワークフロー")
        print("=" * 60)

        user_story = """
        毎朝9時にExcelファイルを開いて、
        売上データを集計し、
        結果をメールで送信したい
        """

        print(f"\nユーザーストーリー:\n{user_story}")
        print("\n⏳ ワークフローを生成中...")
        
        workflow = await builder.build_workflow(
            user_story, 
            workflow_name="売上データ自動処理"
        )
        
        # 生成されたワークフローを表示
        print("\n✨ 生成されたワークフロー:")
        print("=" * 60)
        print(json.dumps(workflow, ensure_ascii=False, indent=2))
        print("=" * 60)
        
        # ファイル保存
        save = input("\n💾 ワークフローをファイルに保存しますか？ (y/n): ").strip().lower()
        if save == 'y':
            builder.save_workflow_to_file(workflow, "generated_excel_workflow.json")
    
    elif mode == "2":
        # 対話的なワークフロービルダー
        await builder.interactive_workflow_builder()
    
    elif mode == "3":
        print("👋 システムを終了します。")
    else:
        print("❌ 無効な選択です。")


if __name__ == "__main__":
    # MCPサーバーが起動していることを確認
    print("⚠️ 注意: MCPサーバーが起動していることを確認してください")
    print("実行コマンド: cd rpa-mcp && python main.py --http")
    print("")

    # メイン処理の実行
    asyncio.run(main())