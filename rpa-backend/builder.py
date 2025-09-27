import json
from typing import Dict, Any, List, Optional
from deepmcpagent import HTTPServerSpec, FastMCPMulti, MCPToolLoader
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import os
from tool_mapping import convert_cmd_list_to_tool_names

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

        # プロンプトの構築（ヒアリング内容ベース + sequence出力指定）
        prompt = f"""
        次のヒアリング内容に基づき、実行可能なRPAワークフローを設計してください。
        出力は必ずJSONのみで、以下のスキーマに厳密に従ってください。

        【ヒアリング内容】
        {hearing_text}

        【出力スキーマ】
        - name: ワークフロー名（20〜50文字程度）
        - description: ワークフローの説明（1〜2文）
        - sequence: 実行シーケンス（配列）。各要素は以下の構造：
          - cmd: コマンドID（例: "run-executable"）
          - cmd-nickname: 表示名（例: "アプリ起動"）
          - cmd-type: 種別（"basic"|"branching" など）
          - version: 数値バージョン（例: 3）
          - uuid: ステップUUID（ランダムで良い）
          - memo: メモ文字列（空でも可）
          - description: ステップ説明（1文程度）
          - tags: 文字列配列（例: ["アプリ", "起動", "基本"]）
          - parameters: パラメータオブジェクト。コマンドに必要なキーのみ含める
          - flags: {{"checkboxed": boolean, "bookmarked": boolean}}

        【重要】
        - JSON以外の文章は出力しない
        - 不要なキーは含めない
        - parametersやtagsは、選定したコマンドに合わせて妥当な初期値を設定

        【出力例】（例示。コンテンツはヒアリングに合わせて調整）
        ```json
        {{
          "name": "サンプルワークフロー",
          "description": "サンプルワークフローの説明",
          "sequence": [
            {{
              "cmd": "run-executable",
              "cmd-nickname": "アプリ起動",
              "cmd-type": "basic",
              "version": 3,
              "uuid": "308e70dd-c638-4af0-8269-ec3d95a02b4f",
              "memo": "",
              "description": "指定したアプリケーションやファイルを起動します。パスや引数、ウィンドウ表示状態を設定できます。",
              "tags": ["アプリ", "起動", "基本"],
              "parameters": {{
                "path": "",
                "arguments": "",
                "interval": 3,
                "maximized": true
              }},
              "flags": {{
                "checkboxed": false,
                "bookmarked": false
              }}
            }}
          ]
        }}
        ```
        """

        # step2.log: デバッグ情報を出力
        import json as json_module
        with open("step2.log", "w", encoding="utf-8") as f:
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

        # エージェントの実行
        try:
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })
        except Exception as e:
            # エラーログを記録
            with open("step2.log", "a", encoding="utf-8") as f:
                f.write(f"\n⚠️ エージェント実行エラー: {str(e)}\n")
                f.write(f"エラータイプ: {type(e)}\n")
            raise

        # 結果の解析
        workflow = self._parse_workflow_response(result)

        # step2.log: 実行結果を追記
        with open("step2.log", "a", encoding="utf-8") as f:
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
        with open("step2.log", "a", encoding="utf-8") as f:
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
        with open("step2.log", "a", encoding="utf-8") as f:
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
            with open("step2.log", "a", encoding="utf-8") as f:
                f.write(f"JSON検索結果: {len(json_matches)} 個のJSONブロック発見\n")
                if json_matches:
                    f.write(f"最初のJSONブロック (最初の500文字):\n{json_matches[0][:500]}\n\n")

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
                with open("step2.log", "a", encoding="utf-8") as f:
                    f.write("JSONブロックが見つからないため、content全体をJSON解析試行\n")
                try:
                    workflow_data = json.loads(content)
                    with open("step2.log", "a", encoding="utf-8") as f:
                        f.write(f"✅ content全体のJSON解析成功\n")
                        f.write(f"steps キーの存在: {'steps' in workflow_data}\n")
                        f.write(f"steps の内容: {workflow_data.get('steps', [])[:3] if 'steps' in workflow_data else 'No steps key'}\n")
                    return {
                        "name": workflow_data.get("name", default_workflow["name"]),
                        "description": workflow_data.get("description", default_workflow["description"]),
                        "version": workflow_data.get("version", "1.0.0"),
                        "steps": workflow_data.get("steps", [])
                    }
                except Exception as parse_error:
                    with open("step2.log", "a", encoding="utf-8") as f:
                        f.write(f"❌ content全体のJSON解析失敗: {str(parse_error)}\n")
                    print("⚠️ JSON形式のワークフローが見つかりませんでした")
                    return default_workflow
                    
        except (json.JSONDecodeError, KeyError) as e:
            with open("step2.log", "a", encoding="utf-8") as f:
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

