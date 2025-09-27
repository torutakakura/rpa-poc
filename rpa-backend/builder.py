import json
from typing import Dict, Any, List, Optional
from deepmcpagent import HTTPServerSpec, FastMCPMulti, MCPToolLoader
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import os

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
        """
        self.mcp_server_url = mcp_server_url
        self.model_name = model_name
        self.allowed_tool_names = list(dict.fromkeys(allowed_tool_names or []))

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
        agent = create_react_agent(
            model=self.llm,
            tools=selected_tools,
            state_modifier=instructions,
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
          - flags: {"checkboxed": boolean, "bookmarked": boolean}

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
                except Exception:
                    print("⚠️ JSON形式のワークフローが見つかりませんでした")
                    return default_workflow
                    
        except (json.JSONDecodeError, KeyError) as e:
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
