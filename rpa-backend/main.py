from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Union, Optional, Annotated, Literal, Dict, Any, Type
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import base64
from abc import ABC, abstractmethod


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


Step = Annotated[
    Union[
        OpenBrowserStep,
        GotoStep,
        ClickStep,
        TypeStep,
        WaitForSelectorStep,
        ScreenshotStep,
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
        context: BrowserContext = await browser.new_context(
            viewport={"width": 1280, "height": 800}
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
        context: BrowserContext = await browser.new_context(
            viewport={"width": step.viewport_width, "height": step.viewport_height}
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


# ========== Step metadata for UI (変更なし) ==========

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