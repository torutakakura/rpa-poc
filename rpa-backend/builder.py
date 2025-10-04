import json
from typing import Dict, Any, List, Optional
from deepmcpagent import HTTPServerSpec, FastMCPMulti, MCPToolLoader
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import os
from tool_mapping import convert_cmd_list_to_tool_names
from config import STEP2_LOG_PATH

class RPAWorkflowBuilder:
    """RPAワークフロービルダー - MCPツールを使用してワークフローを構築"""

    def __init__(
        self,
        mcp_server_url: str = "http://localhost:8080/mcp",
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        allowed_tool_names: Optional[List[str]] = None
    ):
        """
        初期化

        Args:
            mcp_server_url: MCPサーバーのURL
            model_name: 使用するLLMモデル名
            api_key: OpenAI APIキー（環境変数から取得する場合は不要）
            allowed_tool_names: 許可するツール名のリスト（cmdフォーマット）
        """
        self.mcp_server_url = mcp_server_url
        self.model_name = model_name
        # cmdフォーマットをMCPツール名に変換
        if allowed_tool_names:
            self.allowed_tool_names = convert_cmd_list_to_tool_names(
                list(dict.fromkeys(allowed_tool_names))
            )
            print(f"📋 Converted {len(allowed_tool_names)} cmd names to {len(self.allowed_tool_names)} MCP tool names")
        else:
            self.allowed_tool_names = None

        # APIキーの設定
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        # LangChainモデルの初期化
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.0,
            max_tokens=4000  # gpt-4oの大きなコンテキストを活用
        )

        self.agent = None
        self.loader = None
        self.available_tools = []

    async def initialize_agent(self):
        """MCPサーバーに接続してエージェントを初期化（allowed_tool_namesでフィルタ適用）"""

        # MCPサーバーの設定
        servers = {
            "rpa": HTTPServerSpec(
                url=self.mcp_server_url,
                transport="http",
            ),
        }

        # システムプロンプトの設定
        instructions = """あなたはRPAワークフロー設計の専門家です。
        ユーザーのストーリーや要求を分析し、適切なRPAツールを組み合わせて
        効率的なワークフローを構築してください。

        【重要】利用可能なMCPツールを呼び出して、実際のステップ定義を取得してください。
        各ツールは正しいcmd形式（スネークケース）とパラメータ構造を返します。

        ワークフロー作成手順：
        1. ヒアリング内容を分析
        2. 必要なMCPツールを選択して実行
        3. ツールの出力をそのまま使用してワークフローを構成
        4. 最終的なワークフローをJSON形式で出力

        出力形式：
        {
          "name": "ワークフロー名",
          "description": "説明",
          "steps": [ツールから取得したステップ定義の配列]
        }
        """

        # ツール発見
        loader = MCPToolLoader(FastMCPMulti(servers))
        discovered_tools = await loader.get_all_tools()
        tool_map = {tool.name: tool for tool in discovered_tools}

        # 許可されたツールのみを選択（未指定なら全て）
        if self.allowed_tool_names:
            unique_names: List[str] = []
            seen: set[str] = set()
            for name in self.allowed_tool_names:
                if name and name not in seen:
                    seen.add(name)
                    unique_names.append(name)
            selected_tools = [tool_map[name] for name in unique_names if name in tool_map]
        else:
            selected_tools = list(tool_map.values())

        if not selected_tools:
            raise RuntimeError("No matching MCP tools available for allowed_tool_names")

        # エージェントの構築（フィルタ済みツールのみ）
        # promptパラメータを使用（SystemMessageまたは文字列）
        agent = create_react_agent(
            model=self.llm,
            tools=selected_tools,
            prompt=instructions,
        )

        self.agent = agent
        self.loader = loader
        self.available_tools = await self._get_available_tools()

        print(f"✅ エージェントが初期化されました。{len(selected_tools)}個のツールで動作します。")

    async def _get_available_tools(self) -> List[Dict[str, Any]]:
        """MCPサーバーから利用可能なツールのリストを取得（allowed_tool_namesでフィルタ）"""
        if not self.loader:
            return []
        tools_info = await self.loader.list_tool_info()
        items = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for tool in tools_info
        ]
        if self.allowed_tool_names:
            allowed = set(self.allowed_tool_names)
            items = [t for t in items if t["name"] in allowed]
        return items

    def show_available_tools(self):
        """利用可能なツールを表示"""
        print("\n📋 利用可能なRPAツール:")
        print("-" * 50)
        for tool in self.available_tools:
            print(f"• {tool['name']}: {tool['description']}")
        print("-" * 50)

    async def build(self, hearing_text: str, workflow_name: str = None) -> Dict[str, Any]:
        """
        ヒアリング内容からRPAワークフローを構築

        Args:
            hearing_text: ヒアリングで得られた要件の全文
            workflow_name: ワークフロー名（指定しない場合は自動生成）

        Returns:
            生成されたワークフロー（name/description/sequence）
        """
        if not self.agent:
            await self.initialize_agent()

        # generated_step_list.jsonから直接ステップ定義を取得
        import json as json_module
        from pathlib import Path

        step_list_path = Path(__file__).parent.parent / "rpa-mcp" / "generated_step_list.json"
        if not step_list_path.exists():
            step_list_path = Path(__file__).parent / "generated_step_list.json"

        available_step_definitions = []
        if step_list_path.exists():
            with open(step_list_path, 'r', encoding='utf-8') as f:
                step_data = json_module.load(f)
                sequence = step_data.get('sequence', [])

                # 許可されたツールに対応するステップ定義を取得
                if self.allowed_tool_names:
                    from tool_mapping import get_cmd_to_tool_mapping
                    tool_to_cmd = {v: k for k, v in get_cmd_to_tool_mapping().items()}

                    for tool_name in self.allowed_tool_names[:10]:  # 最初の10個の例
                        cmd_key = tool_to_cmd.get(tool_name)
                        if cmd_key:
                            for step in sequence:
                                if step.get('cmd') == cmd_key:
                                    available_step_definitions.append(step)
                                    break

        # ステップ定義の例をプロンプトに含める
        step_examples = ""
        if available_step_definitions:
            step_examples = "\n【利用可能なステップ定義の例（これらの形式を厳守してください）】\n"
            for i, step_def in enumerate(available_step_definitions[:5], 1):
                step_examples += f"\n例{i}:\n{json_module.dumps(step_def, ensure_ascii=False, indent=2)}\n"

        # プロンプトの構築（ヒアリング内容ベース + sequence出力指定）
        prompt = f"""
        次のヒアリング内容に基づき、実行可能なRPAワークフローを設計してください。
        出力は必ずJSONのみで、以下のスキーマに厳密に従ってください。

        【ヒアリング内容】
        {hearing_text}

        {step_examples}

        【重要な指示】
        1. 上記の利用可能なステップ定義の形式に厳密に従ってください
        2. stepsには上記の例から適切なものを選んでコピーし、配列に含めてください
        3. 各ステップは上記の例の完全なコピーとし、parametersの値のみ変更可能です
        4. cmd, cmd-nickname, cmd-type, version, description, tags, flagsは絶対に変更しないでください
        5. 新しいcmdや形式を勝手に作成しないでください
        6. cmdは必ずスネークケース（run_executable）を維持してください

        【最終出力形式】
        最後にJSON形式でワークフローを出力してください：
        ```json
        {{
          "name": "ワークフロー名（20〜50文字程度）",
          "description": "ワークフローの説明（1〜2文）",
          "steps": [
            // 利用可能なステップ定義の形式に従ったステップの配列
            // parametersの値のみ調整可能
          ]
        }}
        ```
        """

        # step2.log: デバッグ情報を出力
        import json as json_module
        with open(STEP2_LOG_PATH, "w", encoding="utf-8") as f:
            f.write("=== RPAワークフロービルダー デバッグ情報 ===\n\n")
            f.write(f"モデル名: {self.model_name}\n")
            f.write(f"MCPサーバーURL: {self.mcp_server_url}\n")
            f.write(f"許可ツール数: {len(self.allowed_tool_names) if self.allowed_tool_names else 'All'}\n\n")

            # システムプロンプトを出力
            f.write("=== システムプロンプト ===\n")
            f.write("""あなたはRPAワークフロー設計の専門家です。
        ユーザーのストーリーや要求を分析し、適切なRPAツールを組み合わせて
        効率的なワークフローを構築してください。

        【重要】出力は必ず以下のJSON形式で行ってください：
        {
          "steps": [
            {
                "cmd": "run-executable",
                "cmd-nickname": "アプリ起動",
                "cmd-type": "basic",
                "version": 3,
                "uuid": "308e70dd-c638-4af0-8269-ec3d95a02b4f",
                "memo": "",
                "description": "指定したアプリケーションやファイルを起動します。パスや引数、ウィンドウ表示状態を設定できます。",
                "tags": ["アプリ", "起動", "基本"],
                "parameters": {"path": "", "arguments": "", "interval": 3, "maximized": true},
                "flags": {"checkboxed": false, "bookmarked": false}
            }
          ]
        }\n\n""")

            # ユーザープロンプトを出力
            f.write("=== ユーザープロンプト ===\n")
            f.write(prompt)
            f.write("\n\n")

            # 利用可能なツールを出力
            f.write("=== 利用可能なツール ===\n")
            if self.available_tools:
                for i, tool in enumerate(self.available_tools, 1):
                    f.write(f"{i}. {tool['name']}: {tool['description']}\n")
            else:
                f.write("ツール情報が取得できていません\n")
            f.write(f"\n合計: {len(self.available_tools) if self.available_tools else 0} ツール\n\n")

            # 許可されたツール名を出力
            if self.allowed_tool_names:
                f.write("=== 許可されたツール名 (MCP形式) ===\n")
                for i, name in enumerate(self.allowed_tool_names, 1):
                    f.write(f"{i}. {name}\n")
                f.write(f"\n合計: {len(self.allowed_tool_names)} ツール\n\n")

        # エージェントの実行（設定オプション付き）
        try:
            result = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config={"recursion_limit": 50}  # 実行時の設定として再帰制限を指定
            )
        except Exception as e:
            # エラーログを記録
            with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"\n⚠️ エージェント実行エラー: {str(e)}\n")
                f.write(f"エラータイプ: {type(e)}\n")
            raise

        # 結果の解析
        workflow = self._parse_workflow_response(result)

        # step2.log: 実行結果を追記
        with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("=== エージェント実行結果 ===\n")
            f.write(f"結果のタイプ: {type(result)}\n")
            if result and "messages" in result:
                f.write(f"メッセージ数: {len(result.get('messages', []))}\n")
                if result["messages"]:
                    last_msg = result["messages"][-1]
                    f.write(f"最終メッセージタイプ: {type(last_msg)}\n")
                    if hasattr(last_msg, 'content'):
                        f.write(f"最終メッセージ内容（最初の500文字）:\n{str(last_msg.content)[:500]}...\n\n")

            f.write("=== パース後のワークフロー ===\n")
            f.write(json_module.dumps(workflow, ensure_ascii=False, indent=2))
            f.write("\n\n")

            # ステップが空の場合の診断情報
            if not workflow.get("steps"):
                f.write("⚠️ ワークフローのstepsが空です！\n")
                f.write("考えられる原因:\n")
                f.write("1. エージェントが正しいJSON形式で応答していない\n")
                f.write("2. 許可されたツールとエージェントの出力が一致していない\n")
                f.write("3. プロンプトの指示が正しく理解されていない\n")
                f.write("4. MCPツールが正しく初期化されていない\n")

        # ワークフロー名が指定されていれば設定
        if workflow_name and "name" in workflow:
            workflow["name"] = workflow_name

        return workflow

    def _parse_workflow_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """エージェントの応答からワークフローを解析"""

        # デバッグ用ログ
        with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("\n=== _parse_workflow_response 開始 ===\n")
            f.write(f"response タイプ: {type(response)}\n")
            f.write(f"response キー: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}\n")

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

        # デバッグ：内容を記録
        with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\nlast_message タイプ: {type(last_message)}\n")
            f.write(f"content 長さ: {len(content) if content else 0}\n")
            f.write(f"content 最初の500文字:\n{content[:500] if content else 'Empty'}\n\n")

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

            # デバッグ：JSON検索結果
            with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"JSON検索結果: {len(json_matches)} 個のJSONブロック発見\n")
                if json_matches:
                    f.write(f"最初のJSONブロック (最初の500文字):\n{json_matches[0][:500]}\n\n")

            if json_matches:
                # JSONをパース
                workflow_data = json.loads(json_matches[0])

                # sequenceキーをstepsキーに変換
                # エージェントは"sequence"を返すが、APIは"steps"を期待している
                steps = workflow_data.get("sequence", workflow_data.get("steps", []))

                # 正しい形式のワークフローを返す
                return {
                    "name": workflow_data.get("name", default_workflow["name"]),
                    "description": workflow_data.get("description", default_workflow["description"]),
                    "version": workflow_data.get("version", "1.0.0"),
                    "steps": steps
                }
            else:
                # JSONブロックが見つからない場合、content全体をJSONとして解析を試みる
                with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
                    f.write("JSONブロックが見つからないため、content全体をJSON解析試行\n")
                try:
                    workflow_data = json.loads(content)
                    with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
                        f.write(f"✅ content全体のJSON解析成功\n")
                        f.write(f"steps キーの存在: {'steps' in workflow_data}\n")
                        f.write(f"sequence キーの存在: {'sequence' in workflow_data}\n")
                        steps = workflow_data.get("sequence", workflow_data.get("steps", []))
                        f.write(f"取得したステップ数: {len(steps)}\n")
                        if steps:
                            f.write(f"最初のステップ: {steps[0].get('cmd', 'No cmd key')}\n")
                    # sequenceキーをstepsキーに変換
                    steps = workflow_data.get("sequence", workflow_data.get("steps", []))
                    return {
                        "name": workflow_data.get("name", default_workflow["name"]),
                        "description": workflow_data.get("description", default_workflow["description"]),
                        "version": workflow_data.get("version", "1.0.0"),
                        "steps": steps
                    }
                except Exception as parse_error:
                    with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
                        f.write(f"❌ content全体のJSON解析失敗: {str(parse_error)}\n")
                    print("⚠️ JSON形式のワークフローが見つかりませんでした")
                    return default_workflow
                    
        except (json.JSONDecodeError, KeyError) as e:
            with open(STEP2_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"❌ ワークフロー解析エラー: {str(e)}\n")
                f.write(f"エラータイプ: {type(e)}\n")
            print(f"⚠️ ワークフローの解析中にエラーが発生しました: {e}")
            return default_workflow

    async def workflow_builder(self, hearing_text: str, workflow_name: str = None, show_tools: bool = False) -> Dict[str, Any]:
        """API用ワークフロービルダー

        ヒアリング内容（hearing_text）をユーザーストーリーとして利用し、
        対話なしでワークフローを生成して返します。

        Args:
            hearing_text: ヒアリングで得られた要件の全文
            workflow_name: 任意のワークフロー名
            show_tools: 初期化後に利用可能ツール一覧を表示するか

        Returns:
            生成されたワークフロー（dict）
        """

        if not hearing_text or not hearing_text.strip():
            raise ValueError("hearing_text is required")

        # ヒアリング内容をユーザーストーリーとしてそのまま使用
        workflow = await self.build(hearing_text.strip(), workflow_name or None)
        if show_tools:
            self.show_available_tools()
        return workflow
    
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

