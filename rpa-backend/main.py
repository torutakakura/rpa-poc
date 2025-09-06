from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Union, Optional, Annotated, Literal, Dict, Any, Type
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import base64
from pathlib import Path
from abc import ABC, abstractmethod
import os

try:
    import psycopg
except Exception:
    psycopg = None  # psycopg 未導入環境でもアプリ起動自体は可能にする


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    url: HttpUrl


@app.get("/healthz")
async def healthz():
    return {"ok": True}


# ========== Step Definitions (変更なし) ==========

class OpenBrowserStep(BaseModel):
    type: Literal["open_browser"]
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 800


class GotoStep(BaseModel):
    type: Literal["goto"]
    url: HttpUrl
    wait_until: Literal["load", "domcontentloaded", "networkidle"] = "load"
    timeout_ms: int = 30000


class ClickStep(BaseModel):
    type: Literal["click"]
    selector: str
    timeout_ms: int = 10000


class TypeStep(BaseModel):
    type: Literal["type"]
    selector: str
    text: str
    delay_ms: Optional[int] = None


class WaitForSelectorStep(BaseModel):
    type: Literal["wait_for_selector"]
    selector: str
    state: Literal["visible", "attached", "hidden", "detached"] = "visible"
    timeout_ms: int = 10000


class ScreenshotStep(BaseModel):
    type: Literal["screenshot"]
    full_page: bool = True


class EnsureStorageStateStep(BaseModel):
    type: Literal["ensure_storage_state"]
    profile_name: str
    storage_dir: Optional[str] = ".storage_states"


class SaveStorageStateStep(BaseModel):
    type: Literal["save_storage_state"]
    profile_name: str
    storage_dir: Optional[str] = ".storage_states"


class WaitForUrlStep(BaseModel):
    type: Literal["wait_for_url"]
    pattern: str
    timeout_ms: int = 30000


class PressStep(BaseModel):
    type: Literal["press"]
    key: str
    selector: Optional[str] = None


class TypeRichStep(BaseModel):
    type: Literal["type_rich"]
    selector: str
    text: str
    delay_ms: Optional[int] = None


class SetFilesStep(BaseModel):
    type: Literal["set_files"]
    selector: str
    files: List[str]


class AssertToastStep(BaseModel):
    type: Literal["assert_toast"]
    selector: Optional[str] = None
    text: Optional[str] = None
    timeout_ms: int = 15000


Step = Annotated[
    Union[
        OpenBrowserStep,
        GotoStep,
        ClickStep,
        TypeStep,
        WaitForSelectorStep,
        ScreenshotStep,
        EnsureStorageStateStep,
        SaveStorageStateStep,
        WaitForUrlStep,
        PressStep,
        TypeRichStep,
        SetFilesStep,
        AssertToastStep,
    ],
    Field(discriminator="type"),
]


class ScenarioRequest(BaseModel):
    steps: List[Step]


# ========== Step Executor Pattern ==========

class StepExecutor(ABC):
    """各ステップタイプの実行ロジックを定義する基底クラス"""
    
    @abstractmethod
    async def execute(
        self, 
        step: Any, 
        state: Dict[str, Any], 
        logs: List[str],
        p: Any
    ) -> Dict[str, Any]:
        """ステップを実行する"""
        pass
    
    async def ensure_browser(
        self, 
        page: Optional[Page], 
        p: Any, 
        state: Dict[str, Any]
    ) -> Page:
        """ブラウザが開いていることを確認（元の_ensure_browser関数と同じ）"""
        if page is not None:
            return page
        browser: Browser = await p.chromium.launch(headless=True)
        storage_state_path = state.get("storage_state_path")
        storage_kw = {}
        if storage_state_path and Path(storage_state_path).exists():
            storage_kw["storage_state"] = storage_state_path
        context: BrowserContext = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            **storage_kw,
        )
        new_page = await context.new_page()
        state["browser"] = browser
        state["context"] = context
        state["page"] = new_page
        return new_page


# ========== 各ステップの実行クラス ==========

class OpenBrowserExecutor(StepExecutor):
    async def execute(
        self, 
        step: OpenBrowserStep, 
        state: Dict[str, Any], 
        logs: List[str],
        p: Any
    ) -> Dict[str, Any]:
        logs.append("Opening browser")
        browser: Browser = await p.chromium.launch(headless=step.headless)
        storage_state_path = state.get("storage_state_path")
        storage_kw = {}
        if storage_state_path and Path(storage_state_path).exists():
            storage_kw["storage_state"] = storage_state_path
        context: BrowserContext = await browser.new_context(
            viewport={"width": step.viewport_width, "height": step.viewport_height},
            **storage_kw,
        )
        page: Page = await context.new_page()
        state["browser"] = browser
        state["context"] = context
        state["page"] = page
        return {}


class GotoExecutor(StepExecutor):
    async def execute(
        self, 
        step: GotoStep, 
        state: Dict[str, Any], 
        logs: List[str],
        p: Any
    ) -> Dict[str, Any]:
        page = await self.ensure_browser(state.get("page"), p, state)
        logs.append(f"Goto {step.url}")
        await state["page"].goto(
            str(step.url), 
            wait_until=step.wait_until, 
            timeout=step.timeout_ms
        )
        return {}


class ClickExecutor(StepExecutor):
    async def execute(
        self, 
        step: ClickStep, 
        state: Dict[str, Any], 
        logs: List[str],
        p: Any
    ) -> Dict[str, Any]:
        page = await self.ensure_browser(state.get("page"), p, state)
        logs.append(f"Click {step.selector}")
        await state["page"].click(step.selector, timeout=step.timeout_ms)
        return {}


class TypeExecutor(StepExecutor):
    async def execute(
        self, 
        step: TypeStep, 
        state: Dict[str, Any], 
        logs: List[str],
        p: Any
    ) -> Dict[str, Any]:
        page = await self.ensure_browser(state.get("page"), p, state)
        logs.append(f"Type into {step.selector}")
        locator = state["page"].locator(step.selector)
        await locator.fill("")
        if step.delay_ms is not None:
            await locator.type(step.text, delay=step.delay_ms)
        else:
            await locator.type(step.text)
        return {}


class WaitForSelectorExecutor(StepExecutor):
    async def execute(
        self, 
        step: WaitForSelectorStep, 
        state: Dict[str, Any], 
        logs: List[str],
        p: Any
    ) -> Dict[str, Any]:
        page = await self.ensure_browser(state.get("page"), p, state)
        logs.append(f"Wait for {step.selector} ({step.state})")
        await state["page"].wait_for_selector(
            step.selector, 
            state=step.state, 
            timeout=step.timeout_ms
        )
        return {}


class ScreenshotExecutor(StepExecutor):
    async def execute(
        self, 
        step: ScreenshotStep, 
        state: Dict[str, Any], 
        logs: List[str],
        p: Any
    ) -> Dict[str, Any]:
        page = await self.ensure_browser(state.get("page"), p, state)
        logs.append("Screenshot")
        img_bytes = await state["page"].screenshot(full_page=step.full_page)
        return {
            "image_base64": base64.b64encode(img_bytes).decode("utf-8")
        }


class EnsureStorageStateExecutor(StepExecutor):
    async def execute(self, step: EnsureStorageStateStep, state: Dict[str, Any], logs: List[str], p: Any) -> Dict[str, Any]:
        base = Path(step.storage_dir or ".storage_states")
        base.mkdir(parents=True, exist_ok=True)
        path = base / f"{step.profile_name}.json"
        state["storage_state_path"] = str(path)
        logs.append(f"Ensure storage state: {path}")
        return {}


class SaveStorageStateExecutor(StepExecutor):
    async def execute(self, step: SaveStorageStateStep, state: Dict[str, Any], logs: List[str], p: Any) -> Dict[str, Any]:
        await self.ensure_browser(state.get("page"), p, state)
        base = Path(step.storage_dir or ".storage_states")
        base.mkdir(parents=True, exist_ok=True)
        path = base / f"{step.profile_name}.json"
        await state["context"].storage_state(path=str(path))
        state["storage_state_path"] = str(path)
        logs.append(f"Saved storage state to: {path}")
        return {}


class WaitForUrlExecutor(StepExecutor):
    async def execute(self, step: WaitForUrlStep, state: Dict[str, Any], logs: List[str], p: Any) -> Dict[str, Any]:
        await self.ensure_browser(state.get("page"), p, state)
        logs.append(f"Wait for URL: {step.pattern}")
        await state["page"].wait_for_url(step.pattern, timeout=step.timeout_ms)
        return {}


class PressExecutor(StepExecutor):
    async def execute(self, step: PressStep, state: Dict[str, Any], logs: List[str], p: Any) -> Dict[str, Any]:
        await self.ensure_browser(state.get("page"), p, state)
        if step.selector:
            locator = state["page"].locator(step.selector)
            await locator.focus()
        logs.append(f"Press key: {step.key}")
        await state["page"].keyboard.press(step.key)
        return {}


class TypeRichExecutor(StepExecutor):
    async def execute(self, step: TypeRichStep, state: Dict[str, Any], logs: List[str], p: Any) -> Dict[str, Any]:
        await self.ensure_browser(state.get("page"), p, state)
        locator = state["page"].locator(step.selector)
        await locator.click()
        try:
            await locator.evaluate("el => { el.textContent = ''; }")
        except Exception:
            pass
        logs.append(f"Type rich into {step.selector}")
        if step.delay_ms is not None:
            await state["page"].keyboard.type(step.text, delay=step.delay_ms)
        else:
            await state["page"].keyboard.type(step.text)
        return {}


class SetFilesExecutor(StepExecutor):
    async def execute(self, step: SetFilesStep, state: Dict[str, Any], logs: List[str], p: Any) -> Dict[str, Any]:
        await self.ensure_browser(state.get("page"), p, state)
        locator = state["page"].locator(step.selector)
        paths = [str(Path(f)) for f in step.files]
        logs.append(f"Set files on {step.selector}: {paths}")
        await locator.set_input_files(paths)
        return {}


class AssertToastExecutor(StepExecutor):
    async def execute(self, step: AssertToastStep, state: Dict[str, Any], logs: List[str], p: Any) -> Dict[str, Any]:
        await self.ensure_browser(state.get("page"), p, state)
        if step.selector:
            locator = state["page"].locator(step.selector)
            await locator.wait_for(state="visible", timeout=step.timeout_ms)
            if step.text:
                content = await locator.inner_text()
                if step.text not in content:
                    raise Exception("Toast text not matched")
        elif step.text:
            locator = state["page"].get_by_text(step.text)
            await locator.wait_for(state="visible", timeout=step.timeout_ms)
        else:
            raise Exception("selector or text is required")
        logs.append("Assert toast OK")
        return {}


# ========== Executor Registry ==========

class ExecutorRegistry:
    """ステップタイプと実行クラスのマッピングを管理"""
    
    def __init__(self):
        self._executors: Dict[Type, StepExecutor] = {}
    
    def register(self, step_class: Type, executor: StepExecutor):
        """ステップクラスと実行クラスを登録"""
        self._executors[step_class] = executor
    
    def get_executor(self, step: Any) -> Optional[StepExecutor]:
        """ステップに対応する実行クラスを取得"""
        return self._executors.get(type(step))
    
    @classmethod
    def create_default(cls) -> 'ExecutorRegistry':
        """デフォルトの実行クラスを登録したレジストリを作成"""
        registry = cls()
        
        # すべてのステップタイプを登録
        registry.register(OpenBrowserStep, OpenBrowserExecutor())
        registry.register(GotoStep, GotoExecutor())
        registry.register(ClickStep, ClickExecutor())
        registry.register(TypeStep, TypeExecutor())
        registry.register(WaitForSelectorStep, WaitForSelectorExecutor())
        registry.register(ScreenshotStep, ScreenshotExecutor())
        registry.register(EnsureStorageStateStep, EnsureStorageStateExecutor())
        registry.register(SaveStorageStateStep, SaveStorageStateExecutor())
        registry.register(WaitForUrlStep, WaitForUrlExecutor())
        registry.register(PressStep, PressExecutor())
        registry.register(TypeRichStep, TypeRichExecutor())
        registry.register(SetFilesStep, SetFilesExecutor())
        registry.register(AssertToastStep, AssertToastExecutor())
        
        return registry


# ========== メインの実行エンジン ==========

class ScenarioExecutor:
    """シナリオ実行のメインエンジン"""
    
    def __init__(self, executor_registry: Optional[ExecutorRegistry] = None):
        self.registry = executor_registry or ExecutorRegistry.create_default()
    
    async def execute_scenario(self, steps: List[Step]) -> Dict[str, Any]:
        """元のexecute_scenario関数と同じインターフェースを提供"""
        logs: List[str] = []
        results: List[Dict[str, Any]] = []
        state: Dict[str, Any] = {"browser": None, "context": None, "page": None}
        
        async with async_playwright() as p:
            try:
                for idx, step in enumerate(steps):
                    result: Dict[str, Any] = {
                        "index": idx, 
                        "type": step.type, 
                        "ok": True
                    }
                    
                    # 対応するExecutorを取得して実行
                    executor = self.registry.get_executor(step)
                    
                    if executor is None:
                        # Unknown step typeの場合（元の実装と同じ）
                        result["ok"] = False
                        result["error"] = "Unknown step type"
                    else:
                        try:
                            # ステップを実行
                            execution_result = await executor.execute(
                                step, state, logs, p
                            )
                            # 結果をマージ
                            result.update(execution_result)
                        except Exception as e:
                            # エラーハンドリング（必要に応じて追加）
                            result["ok"] = False
                            result["error"] = str(e)
                            logs.append(f"Error in step {idx}: {e}")
                    
                    results.append(result)
                
                return {"ok": True, "results": results, "logs": logs}
                
            finally:
                # Cleanup if opened（元の実装と同じ）
                if state.get("context") is not None:
                    await state["context"].close()
                if state.get("browser") is not None:
                    await state["browser"].close()


# シングルトンインスタンスを作成
_scenario_executor = ScenarioExecutor()


# 元のexecute_scenario関数をラッパーとして保持（互換性のため）
async def execute_scenario(steps: List[Step]) -> Dict[str, Any]:
    """既存のコードとの互換性を保つためのラッパー関数"""
    return await _scenario_executor.execute_scenario(steps)


# ========== Step metadata for UI (変更) ==========

def _step_meta() -> List[Dict[str, Any]]:
    meta: List[Dict[str, Any]] = []
    registry: List[Dict[str, Any]] = [
        {
            "type": "open_browser",
            "title": "Open Browser",
            "description": "ヘッドレス/ビューポート指定でブラウザを開く",
            "schema": OpenBrowserStep.model_json_schema(),
            "example": {"type": "open_browser", "headless": True},
        },
        {
            "type": "goto",
            "title": "Goto URL",
            "description": "指定URLへ遷移",
            "schema": GotoStep.model_json_schema(),
            "example": {"type": "goto", "url": "https://example.com"},
        },
        {
            "type": "click",
            "title": "Click",
            "description": "セレクタ要素をクリック",
            "schema": ClickStep.model_json_schema(),
            "example": {"type": "click", "selector": "#submit"},
        },
        {
            "type": "type",
            "title": "Type",
            "description": "セレクタ要素に文字入力",
            "schema": TypeStep.model_json_schema(),
            "example": {"type": "type", "selector": "#q", "text": "hello"},
        },
        {
            "type": "wait_for_selector",
            "title": "Wait For Selector",
            "description": "要素の状態(表示/非表示など)を待機",
            "schema": WaitForSelectorStep.model_json_schema(),
            "example": {"type": "wait_for_selector", "selector": "#result"},
        },
        {
            "type": "screenshot",
            "title": "Screenshot",
            "description": "スクリーンショットを撮影",
            "schema": ScreenshotStep.model_json_schema(),
            "example": {"type": "screenshot", "full_page": True},
        },
        {
            "type": "ensure_storage_state",
            "title": "Ensure Storage State",
            "description": "プロファイルのストレージ状態ファイルを指定（次のコンテキスト作成で利用）",
            "schema": EnsureStorageStateStep.model_json_schema(),
            "example": {"type": "ensure_storage_state", "profile_name": "work"},
        },
        {
            "type": "save_storage_state",
            "title": "Save Storage State",
            "description": "現在のストレージ状態を保存（手動ログイン後に実行）",
            "schema": SaveStorageStateStep.model_json_schema(),
            "example": {"type": "save_storage_state", "profile_name": "work"},
        },
        {
            "type": "wait_for_url",
            "title": "Wait For URL",
            "description": "指定パターンのURLへ遷移するまで待機",
            "schema": WaitForUrlStep.model_json_schema(),
            "example": {"type": "wait_for_url", "pattern": "**/mail/**"},
        },
        {
            "type": "press",
            "title": "Press Key",
            "description": "キー入力（例: Control+Enter）",
            "schema": PressStep.model_json_schema(),
            "example": {"type": "press", "key": "Control+Enter"},
        },
        {
            "type": "type_rich",
            "title": "Type Rich",
            "description": "contenteditable の本文領域に入力",
            "schema": TypeRichStep.model_json_schema(),
            "example": {"type": "type_rich", "selector": "div[aria-label='メッセージ本文']", "text": "こんにちは"},
        },
        {
            "type": "set_files",
            "title": "Set Files",
            "description": "input[type=file] にファイルパスを設定（添付）",
            "schema": SetFilesStep.model_json_schema(),
            "example": {"type": "set_files", "selector": "input[type='file']", "files": ["/tmp/a.pdf"]},
        },
        {
            "type": "assert_toast",
            "title": "Assert Toast",
            "description": "トーストメッセージの表示やテキスト一致を検証",
            "schema": AssertToastStep.model_json_schema(),
            "example": {"type": "assert_toast", "text": "Message sent"},
        },
    ]
    meta.extend(registry)
    return meta


# ========== API Endpoints (変更なし) ==========

@app.get("/steps")
async def list_steps():
    return {"ok": True, "steps": _step_meta()}


@app.post("/run_scenario")
async def run_scenario(req: ScenarioRequest):
    result = await execute_scenario(req.steps)
    return result


# =============================
# DB: scenarios CRUD (name/description)
# =============================

def _db_conn():
    if psycopg is None:
        raise RuntimeError("psycopg is not installed. Please install 'psycopg[binary]'.")
    host = os.getenv("PGHOST", "127.0.0.1")
    port = int(os.getenv("PGPORT", "55432"))
    user = os.getenv("PGUSER", "rpa")
    password = os.getenv("PGPASSWORD", "rpa_password")
    dbname = os.getenv("PGDATABASE", "rpa")
    return psycopg.connect(host=host, port=port, user=user, password=password, dbname=dbname)


class ScenarioItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    updated_at: Optional[str] = None
    latest_version: Optional[int] = None


class ScenarioUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@app.get("/scenarios")
def list_scenarios() -> Dict[str, Any]:
    sql = """
    select s.id::text,
           s.name,
           s.description,
           s.updated_at,
           (select max(version) from scenario_versions sv where sv.scenario_id = s.id) as latest_version
    from scenarios s
    order by s.updated_at desc nulls last, s.created_at desc
    """
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    items = [
        {
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "updated_at": r[3].isoformat() if r[3] else None,
            "latest_version": r[4],
        }
        for r in rows
    ]
    return {"ok": True, "items": items}


@app.put("/scenarios/{scenario_id}")
def update_scenario(scenario_id: str, body: ScenarioUpdateRequest) -> Dict[str, Any]:
    sets = []
    params: List[Any] = []
    if body.name is not None:
        sets.append("name = %s")
        params.append(body.name)
    if body.description is not None:
        sets.append("description = %s")
        params.append(body.description)
    if not sets:
        return {"ok": True}
    sets.append("updated_at = now()")
    sql = f"update scenarios set {' , '.join(sets)} where id = %s"
    params.append(scenario_id)
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
    return {"ok": True}


@app.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: str) -> Dict[str, Any]:
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("delete from scenarios where id = %s", (scenario_id,))
            conn.commit()
    return {"ok": True}


class ScenarioCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


@app.post("/scenarios")
def create_scenario(body: ScenarioCreateRequest) -> Dict[str, Any]:
    """新しいシナリオを作成する"""
    sql = """
    insert into scenarios (name, description)
    values (%s, %s)
    returning id::text, name, description, created_at, updated_at
    """
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (body.name, body.description))
            row = cur.fetchone()
            conn.commit()
    
    scenario = {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "created_at": row[3].isoformat() if row[3] else None,
        "updated_at": row[4].isoformat() if row[4] else None,
        "latest_version": None  # 新規作成時はバージョンなし
    }
    
    return {"ok": True, "scenario": scenario}