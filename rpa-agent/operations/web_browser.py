"""
L_ウェブブラウザ カテゴリの操作
"""

from typing import Any, Dict

from .base import BaseOperation, OperationResult

# Selenium WebDriverをオプショナルでインポート
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.select import Select
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class WebBrowserOpenOperation(BaseOperation):
    """ブラウザを開く"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        url = params.get("url", "")
        browser_type = params.get("browser_type", "chrome")
        headless = params.get("headless", False)
        window_size = params.get("window_size", {"width": 1280, "height": 720})
        reference_id = params.get("reference_id", "")

        error = self.validate_params(params, ["url"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        if not SELENIUM_AVAILABLE:
            return OperationResult(
                status="failure",
                data={},
                error="Web browser support not available. Install selenium.",
            )

        try:
            # ブラウザドライバーを初期化
            if browser_type == "chrome":
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                options.add_argument(
                    f'--window-size={window_size["width"]},{window_size["height"]}'
                )
                driver = webdriver.Chrome(options=options)
            elif browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                driver = webdriver.Firefox(options=options)
                driver.set_window_size(window_size["width"], window_size["height"])
            else:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Unsupported browser type: {browser_type}",
                )

            # URLを開く
            driver.get(url)

            # 参照IDでブラウザインスタンスを保存
            if reference_id:
                self.set_storage(f"browser_{reference_id}", driver)
                self.log(f"Browser saved with reference ID: {reference_id}")

            self.log(f"Opened {url} in {browser_type}")

            return OperationResult(
                status="success",
                data={
                    "url": url,
                    "browser_type": browser_type,
                    "reference_id": reference_id,
                    "title": driver.title,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to open browser: {str(e)}"
            )


class WebBrowserCloseOperation(BaseOperation):
    """ブラウザを閉じる"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")

        error = self.validate_params(params, ["reference_id"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # 参照IDからブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # ブラウザを閉じる
            driver.quit()

            # ストレージから削除
            self.delete_storage(f"browser_{reference_id}")

            self.log(f"Closed browser with reference ID: {reference_id}")

            return OperationResult(
                status="success", data={"reference_id": reference_id}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to close browser: {str(e)}"
            )


class WebBrowserNavigateOperation(BaseOperation):
    """ページ遷移"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        url = params.get("url", "")
        wait_for_load = params.get("wait_for_load", True)

        error = self.validate_params(params, ["reference_id", "url"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # URLに遷移
            driver.get(url)

            # ページ読み込み待機
            if wait_for_load:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )

            self.log(f"Navigated to {url}")

            return OperationResult(
                status="success",
                data={
                    "url": url,
                    "title": driver.title,
                    "current_url": driver.current_url,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to navigate: {str(e)}"
            )


class WebBrowserClickOperation(BaseOperation):
    """要素をクリック"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        selector = params.get("selector", "")
        selector_type = params.get(
            "selector_type", "css"
        )  # css, xpath, id, name, class
        wait_time = params.get("wait_time", 10)

        error = self.validate_params(params, ["reference_id", "selector"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # セレクタタイプに応じてBy設定
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "link_text": By.LINK_TEXT,
                "partial_link_text": By.PARTIAL_LINK_TEXT,
            }.get(selector_type, By.CSS_SELECTOR)

            # 要素を待機して取得
            wait = WebDriverWait(driver, wait_time)
            element = wait.until(EC.element_to_be_clickable((by_type, selector)))

            # クリック
            element.click()

            self.log(f"Clicked element: {selector}")

            return OperationResult(
                status="success",
                data={"selector": selector, "selector_type": selector_type},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to click element: {str(e)}"
            )


class WebBrowserInputTextOperation(BaseOperation):
    """テキスト入力"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        selector = params.get("selector", "")
        selector_type = params.get("selector_type", "css")
        text = params.get("text", "")
        clear_before = params.get("clear_before", True)
        wait_time = params.get("wait_time", 10)

        error = self.validate_params(params, ["reference_id", "selector", "text"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # セレクタタイプに応じてBy設定
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
            }.get(selector_type, By.CSS_SELECTOR)

            # 要素を待機して取得
            wait = WebDriverWait(driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by_type, selector)))

            # 既存のテキストをクリア
            if clear_before:
                element.clear()

            # テキストを入力
            element.send_keys(text)

            self.log(f"Input text to element: {selector}")

            return OperationResult(
                status="success", data={"selector": selector, "text_length": len(text)}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to input text: {str(e)}"
            )


class WebBrowserSelectDropdownOperation(BaseOperation):
    """ドロップダウン選択"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        selector = params.get("selector", "")
        selector_type = params.get("selector_type", "css")
        select_by = params.get("select_by", "value")  # value, text, index
        select_value = params.get("select_value", "")
        wait_time = params.get("wait_time", 10)

        error = self.validate_params(
            params, ["reference_id", "selector", "select_value"]
        )
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # セレクタタイプに応じてBy設定
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
            }.get(selector_type, By.CSS_SELECTOR)

            # 要素を待機して取得
            wait = WebDriverWait(driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by_type, selector)))

            # Select要素として操作
            select = Select(element)

            # 選択方法に応じて選択
            if select_by == "value":
                select.select_by_value(select_value)
            elif select_by == "text":
                select.select_by_visible_text(select_value)
            elif select_by == "index":
                select.select_by_index(int(select_value))

            self.log(f"Selected dropdown option: {select_value}")

            return OperationResult(
                status="success",
                data={
                    "selector": selector,
                    "select_by": select_by,
                    "select_value": select_value,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to select dropdown: {str(e)}"
            )


class WebBrowserGetTextOperation(BaseOperation):
    """テキスト取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        selector = params.get("selector", "")
        selector_type = params.get("selector_type", "css")
        storage_key = params.get("storage_key", "")
        wait_time = params.get("wait_time", 10)

        error = self.validate_params(params, ["reference_id", "selector"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # セレクタタイプに応じてBy設定
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
            }.get(selector_type, By.CSS_SELECTOR)

            # 要素を待機して取得
            wait = WebDriverWait(driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by_type, selector)))

            # テキストを取得
            text = element.text

            # ストレージに保存
            if storage_key:
                self.set_storage(storage_key, text)
                self.log(f"Stored text as '{storage_key}'")

            self.log(f"Got text from element: {selector}")

            return OperationResult(
                status="success",
                data={"selector": selector, "text": text, "text_length": len(text)},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to get text: {str(e)}"
            )


class WebBrowserWaitForElementOperation(BaseOperation):
    """要素待機"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        selector = params.get("selector", "")
        selector_type = params.get("selector_type", "css")
        wait_condition = params.get(
            "wait_condition", "presence"
        )  # presence, visible, clickable
        wait_time = params.get("wait_time", 30)

        error = self.validate_params(params, ["reference_id", "selector"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # セレクタタイプに応じてBy設定
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
            }.get(selector_type, By.CSS_SELECTOR)

            # 待機条件を設定
            wait = WebDriverWait(driver, wait_time)
            if wait_condition == "presence":
                wait.until(
                    EC.presence_of_element_located((by_type, selector))
                )
            elif wait_condition == "visible":
                wait.until(
                    EC.visibility_of_element_located((by_type, selector))
                )
            elif wait_condition == "clickable":
                wait.until(EC.element_to_be_clickable((by_type, selector)))
            else:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Unknown wait condition: {wait_condition}",
                )

            self.log(f"Element found: {selector}")

            return OperationResult(
                status="success",
                data={
                    "selector": selector,
                    "wait_condition": wait_condition,
                    "element_found": True,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Element not found within {wait_time} seconds: {str(e)}",
            )


class WebBrowserScrollOperation(BaseOperation):
    """スクロール"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        scroll_type = params.get("scroll_type", "pixels")  # pixels, element, bottom
        scroll_amount = params.get("scroll_amount", 300)
        selector = params.get("selector", "")
        selector_type = params.get("selector_type", "css")

        error = self.validate_params(params, ["reference_id"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            if scroll_type == "pixels":
                # ピクセル単位でスクロール
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                self.log(f"Scrolled {scroll_amount} pixels")

            elif scroll_type == "element" and selector:
                # 特定の要素までスクロール
                by_type = {
                    "css": By.CSS_SELECTOR,
                    "xpath": By.XPATH,
                    "id": By.ID,
                    "name": By.NAME,
                    "class": By.CLASS_NAME,
                    "tag": By.TAG_NAME,
                }.get(selector_type, By.CSS_SELECTOR)

                element = driver.find_element(by_type, selector)
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                self.log(f"Scrolled to element: {selector}")

            elif scroll_type == "bottom":
                # ページ最下部までスクロール
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.log("Scrolled to bottom of page")

            return OperationResult(
                status="success",
                data={
                    "scroll_type": scroll_type,
                    "scroll_amount": scroll_amount if scroll_type == "pixels" else None,
                    "selector": selector if scroll_type == "element" else None,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to scroll: {str(e)}"
            )


class WebBrowserTakeScreenshotOperation(BaseOperation):
    """スクリーンショット取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        save_path = params.get("save_path", "")
        full_page = params.get("full_page", False)

        error = self.validate_params(params, ["reference_id", "save_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            import os

            save_path = os.path.expanduser(save_path)

            # ディレクトリを作成
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)

            if full_page:
                # フルページスクリーンショット（Chrome/Firefoxで対応）
                original_size = driver.get_window_size()
                required_width = driver.execute_script(
                    "return document.body.parentNode.scrollWidth"
                )
                required_height = driver.execute_script(
                    "return document.body.parentNode.scrollHeight"
                )
                driver.set_window_size(required_width, required_height)
                driver.save_screenshot(save_path)
                driver.set_window_size(original_size["width"], original_size["height"])
            else:
                # 通常のスクリーンショット
                driver.save_screenshot(save_path)

            self.log(f"Screenshot saved to {save_path}")

            return OperationResult(
                status="success", data={"save_path": save_path, "full_page": full_page}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to take screenshot: {str(e)}"
            )


class WebBrowserExecuteJavaScriptOperation(BaseOperation):
    """JavaScript実行"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        script = params.get("script", "")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["reference_id", "script"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # JavaScriptを実行
            result = driver.execute_script(script)

            # 結果をストレージに保存
            if storage_key and result is not None:
                self.set_storage(storage_key, result)
                self.log(f"Stored JavaScript result as '{storage_key}'")

            self.log("Executed JavaScript")

            return OperationResult(
                status="success",
                data={
                    "script_length": len(script),
                    "result": result,
                    "result_type": type(result).__name__
                    if result is not None
                    else None,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to execute JavaScript: {str(e)}",
            )


class WebBrowserSwitchTabOperation(BaseOperation):
    """タブ切り替え"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        tab_index = params.get("tab_index")
        tab_handle = params.get("tab_handle")

        error = self.validate_params(params, ["reference_id"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # 現在のタブハンドルを取得
            handles = driver.window_handles

            if tab_handle:
                # ハンドル指定で切り替え
                if tab_handle in handles:
                    driver.switch_to.window(tab_handle)
                else:
                    return OperationResult(
                        status="failure",
                        data={},
                        error=f"Tab handle '{tab_handle}' not found",
                    )
            elif tab_index is not None:
                # インデックス指定で切り替え
                if 0 <= tab_index < len(handles):
                    driver.switch_to.window(handles[tab_index])
                else:
                    return OperationResult(
                        status="failure",
                        data={},
                        error=f"Tab index {tab_index} out of range (0-{len(handles)-1})",
                    )
            else:
                return OperationResult(
                    status="failure",
                    data={},
                    error="Either tab_index or tab_handle must be specified",
                )

            self.log("Switched to tab")

            return OperationResult(
                status="success",
                data={
                    "current_tab": driver.current_window_handle,
                    "total_tabs": len(handles),
                    "title": driver.title,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to switch tab: {str(e)}"
            )


class WebBrowserRefreshOperation(BaseOperation):
    """ページ更新"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")
        wait_for_load = params.get("wait_for_load", True)

        error = self.validate_params(params, ["reference_id"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ブラウザインスタンスを取得
            driver = self.get_storage(f"browser_{reference_id}")
            if not driver:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Browser with reference ID '{reference_id}' not found",
                )

            # ページを更新
            driver.refresh()

            # ページ読み込み待機
            if wait_for_load:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )

            self.log("Page refreshed")

            return OperationResult(
                status="success",
                data={"title": driver.title, "current_url": driver.current_url},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to refresh page: {str(e)}"
            )
