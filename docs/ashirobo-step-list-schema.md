# 操作一覧（A〜Q 完全版）

## A. アプリ・画面
- アプリ
  - 起動
  - 起動（終了待ち）
- 画面
  - 最前画面を覚える
  - 画面を覚える（名前）
  - 切り替え（参照ID）
  - 切り替え（名前）
  - 画面の名前を取得
  - 移動
  - 最大化 / 最小化
  - スクリーンショットを撮る


### パラメータ定義（操作A）

#### A-1 アプリ起動 (`run-executable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| path | string | "" | 実行対象のパス。未設定では動作しない | はい |
| arguments | string | "" | コマンドライン引数 | いいえ |
| interval | number (sec) | 3 | 待機・間隔の秒数 | いいえ |
| maximized | True / False | - | 起動時のウィンドウ状態の切替 | いいえ |

#### A-2 アプリ起動（終了待ち） (`run-executable-and-wait`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| path | string | "" | 実行対象のパス。未設定では動作しない | はい |
| arguments | string | "" | コマンドライン引数 | いいえ |
| timeout | number (sec) | 300 | 待機の上限時間（秒） | いいえ |
| output-variable | string | "" | 標準出力の格納先変数 | いいえ |
| error-variable | string | "" | 標準エラー出力の格納先変数 | いいえ |

#### A-3 最前画面を覚える (`remember-focused-window`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | （空） | 値やウィンドウを保持する変数名 | いいえ |

#### A-4 画面を覚える（名前） (`remember-named-window`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| match-type | contains / equals | - | タイトル一致方式の切替 | いいえ |
| window-name | string | （空） | 対象ウィンドウのタイトル文字列 | はい |
| variable | string | （空） | 値やウィンドウを保持する変数名 | いいえ |

#### A-5 最前画面切り替え (`focus-window`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | "" | 値やウィンドウを保持する変数名 | はい |

#### A-6 画面切り替え（名前） (`focus-window-by-name`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | はい |

#### A-7 画面の名前を取得 (`get-window-title`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| window | window-ref | __focused_window__ | 対象ウィンドウ指定（既定は最前面など） | いいえ |
| variable | string | （空） | 値やウィンドウを保持する変数名 | いいえ |

#### A-8 ウィンドウを移動 (`align-focused-window`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| alignment | left / right / top / bottom / center | - | ウィンドウ配置の切替 | いいえ |

#### A-9 ウィンドウ最大化／最小化 (`maximize-focused-window`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| behavior | maximize / minimize | - | ウィンドウ操作種別の切替 | いいえ |

#### A-10 スクリーンショットを撮る (`take-screenshot`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| dir-path | string | "" | 保存先フォルダ | はい |
| file-name | string | "" | 保存ファイル名（拡張子なし） | はい |
| area | area-whole / area-window / area-selection | - | キャプチャ範囲の切替 | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| timestamp | False / True | - | タイムスタンプ付与の有無 | いいえ |
| extension | png / jpg / bmp | - | 保存ファイルの拡張子 | いいえ |



## B. 待機・終了・エラー
- 秒
- 画像出現を待つ
- 続行確認
- タイマー付き続行確認（秒）
- コマンド間待機時間を変更
- 作業強制終了
- エラー発生
- エラー確認・処理
- エラー確認・処理（リトライ前処理）

### パラメータ定義（操作B）

#### B-11 待機（秒） (`pause`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| interval | number (sec) | 3 | 待機・間隔の秒数 | いいえ |

#### B-12 画像出現を待つ (`search-screen-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| filename | string | "" | 任意設定項目（用途に応じて指定） | はい |
| precision | number (%) | 85 | 画像一致の厳しさ（%） | いいえ |
| interval | number (sec) | 5 | 待機・間隔の秒数 | いいえ |
| noise-filter | number (%) | 100.0 | 画像検索時のノイズ除去率 | いいえ |
| search-area-type | screen / window / area | - | 検索範囲の種類 | いいえ |
| search-area | rect (x1,y1)-(x2,y2) | (0,0)-(0,0) | 検索座標の範囲指定 | いいえ |

#### B-13 続行確認 (`pause-and-ask-to-proceed`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### B-14 タイマー付き続行確認 (`pause-and-countdown-to-proceed`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| interval | number (sec) | 3 | 待機・間隔の秒数 | いいえ |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### B-15 コマンド間の待機時間を変更 (`change-speed-for-command-execution`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| interval | number (sec) | 0.2 | 待機・間隔の秒数 | いいえ |

#### B-16 作業強制終了 (`abort`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| result-type | abort / exit | - | 終了動作の種類 | いいえ |

#### B-17 エラーを発生させる (`raise-error`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### B-18 直前のコマンドのエラーを確認・処理 (`check-for-errors`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| retries | number | 0 | リトライ回数 | いいえ |
| wait | number (sec) | 1 | リトライ間隔（秒） | いいえ |
| err-cmd | string | [ERR_CMD] | エラー発生コマンド名の格納先 | いいえ |
| err-memo | string | [ERR_MEMO] | エラーメモの格納先 | いいえ |
| err-msg | string | [ERR_MSG] | エラーメッセージの格納先 | いいえ |
| err-param | string | [ERR_PARAM] | エラー時パラメータの格納先 | いいえ |

#### B-19 直前のコマンドのエラーを確認・処理（リトライ前処理） (`check-for-errors-2`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| retries | number | 0 | リトライ回数 | いいえ |
| wait | number (sec) | 1 | リトライ間隔（秒） | いいえ |
| err-cmd | string | [ERR_CMD] | エラー発生コマンド名の格納先 | いいえ |
| err-memo | string | [ERR_MEMO] | エラーメモの格納先 | いいえ |
| err-msg | string | [ERR_MSG] | エラーメッセージの格納先 | いいえ |
| err-param | string | [ERR_PARAM] | エラー時パラメータの格納先 | いいえ |

## C. マウス
- 移動
  - 座標
  - 距離
  - 画像認識
- ドラッグ＆ドロップ
  - 座標（D&D）
  - 距離（D&D）
  - 画像認識（D&D）
- マウスクリック
- スクロール

### パラメータ定義（操作C）

#### C-20 マウス移動（座標） (`move-mouse-to-absolute-coordinates`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| x | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |
| y | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |
| click | string | single | 任意設定項目（用途に応じて指定） | いいえ |

#### C-21 マウス移動（距離） (`move-mouse-to-relative-coordinates`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| x | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |
| y | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |
| click | string | single | 任意設定項目（用途に応じて指定） | いいえ |

#### C-22 マウス移動（画像認識） (`move-mouse-to-image`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| filename | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| precision | number (%) | 85 | 画像一致の厳しさ（%） | いいえ |
| noise-filter | number (%) | 100.0 | 画像検索時のノイズ除去率 | いいえ |
| search-area-type | screen / window / area | - | 検索範囲の種類 | いいえ |
| search-area | rect (x1,y1)-(x2,y2) | (0,0)-(0,0) | 検索座標の範囲指定 | いいえ |
| click | string | single | 任意設定項目（用途に応じて指定） | いいえ |

#### C-23 現在位置からドラッグ&ドロップ（座標） (`drag-and-drop-to-absolute-coordinates`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| x | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |
| y | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |

#### C-24 現在位置からドラッグ&ドロップ（距離） (`drag-and-drop-to-relative-coordinates`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| x | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |
| y | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |

#### C-25 現在位置からドラッグ&ドロップ（画像認識） (`drag-and-drop-to-image`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| filename | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| precision | number (%) | 85 | 画像一致の厳しさ（%） | いいえ |
| noise-filter | number (%) | 100.0 | 画像検索時のノイズ除去率 | いいえ |
| search-area-type | screen / window / area | - | 検索範囲の種類 | いいえ |
| search-area | rect (x1,y1)-(x2,y2) | (0,0)-(0,0) | 検索座標の範囲指定 | いいえ |

#### C-26 マウスクリック (`click-mouse`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| type | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| key | string | __null__ | 任意設定項目（用途に応じて指定） | いいえ |

#### C-27 マウススクロール (`scroll-mouse`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| direction | string | up | 任意設定項目（用途に応じて指定） | いいえ |
| amount | number | 3 | 任意設定項目（用途に応じて指定） | いいえ |

## D. キーボード
- 入力
  - 文字
  - 文字（貼り付け）
  - パスワード
  - ショートカットキー

### パラメータ定義（操作D）

#### D-28 キーボード入力（文字） (`typewrite-static-string`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | いいえ |
| enter | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### D-29 キーボード入力（貼り付け） (`typewrite-all-string`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | いいえ |
| enter | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### D-30 キーボード入力（パスワード） (`typewrite-password`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| enter | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | type-input / ほか | type-input | 任意設定項目（用途に応じて指定） | いいえ |
| ciphertext | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| nonce | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| encryption | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |

#### D-31 ショートカットキーを入力 (`type-hotkeys`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| key-0 | string | __null__ | 任意設定項目（用途に応じて指定） | いいえ |
| key-1 | string | __null__ | 任意設定項目（用途に応じて指定） | いいえ |
| key-2 | string | __null__ | 任意設定項目（用途に応じて指定） | いいえ |
| key-3 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

## E. 記憶
- 文字
- パスワード
- 環境情報
- 日付
- 日付（営業日）
- 日付（曜日）
- 日付計算
- 曜日
- 時刻
- 時刻計算
- 計算
- 乱数
- コピー内容
- クリップボードへコピー
- 実行中に入力
- ファイル更新日時
- ファイルサイズ
- 最新ファイル・フォルダ

### パラメータ定義（操作E）

#### E-32 データの記憶（文字） (`assign-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### E-33 パスワードの記憶 (`assign-password-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| password-type | type-input | type-input | 任意設定項目（用途に応じて指定） | いいえ |
| password | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-id | string | パスワード | 任意設定項目（用途に応じて指定） | いいえ |

#### E-34 データの記憶（環境情報） (`assign-environment-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 環境 | 値やウィンドウを保持する変数名 | いいえ |
| environment | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### E-35 日付を記憶 (`assign-date-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 日付 | 値やウィンドウを保持する変数名 | いいえ |
| offset | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| format | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |
| 0-option | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### E-36 日付を記憶（営業日） (`assign-date-business-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 日付 | 値やウィンドウを保持する変数名 | いいえ |
| offset | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| busidays | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| mon | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| tue | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| wed | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| thu | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| fri | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| sat | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| sun | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| holidays | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| holidays-custom | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| format | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |
| 0-option | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### E-37 日付を記憶（曜日） (`assign-date-weekdays-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 日付 | 値やウィンドウを保持する変数名 | いいえ |
| month | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| week | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| weekdays | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| mon | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| tue | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| wed | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| thu | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| fri | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| sat | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| sun | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| holidays | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| holidays-custom | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| adjust | forward | forward | 任意設定項目（用途に応じて指定） | いいえ |
| format | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |
| 0-option | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### E-38 日付計算結果を記憶 (`assign-date-calculation-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 日付 | 値やウィンドウを保持する変数名 | いいえ |
| input-date | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| format1 | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |
| format2 | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |
| operator | add | add | 任意設定項目（用途に応じて指定） | いいえ |
| year | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| month | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| day | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| mon | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| tue | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| wed | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| thu | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| fri | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| sat | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| sun | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| holidays | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| holidays-custom | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| count-method | everyday | everyday | 任意設定項目（用途に応じて指定） | いいえ |
| adjust | forward | forward | 任意設定項目（用途に応じて指定） | いいえ |
| 0-option | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### E-39 曜日を記憶 (`assign-day-of-week-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 曜日 | 値やウィンドウを保持する変数名 | いいえ |
| offset | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| format | string | 月曜日 | 任意設定項目（用途に応じて指定） | いいえ |
| type | today | today | 任意設定項目（用途に応じて指定） | いいえ |
| date | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| format-date | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |

#### E-40 現在の時刻を記憶 (`assign-timestamp-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 時刻 | 値やウィンドウを保持する変数名 | いいえ |
| format | string | hh:mm:ss | 任意設定項目（用途に応じて指定） | いいえ |
| language | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| timezone | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| 0-option | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### E-41 時刻計算結果を記憶 (`assign-time-calculation-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 時刻 | 値やウィンドウを保持する変数名 | いいえ |
| time | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| format | string | hh:mm:ss | 任意設定項目（用途に応じて指定） | いいえ |
| operator | add | add | 任意設定項目（用途に応じて指定） | いいえ |
| hours | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| minutes | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| seconds | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| format2 | string | hh:mm:ss | 任意設定項目（用途に応じて指定） | いいえ |
| language | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| timezone | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| 0-option | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### E-42 計算結果を記憶 (`assign-arithmetic-result-to-string-variable-v2`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 計算結果 | 値やウィンドウを保持する変数名 | いいえ |
| number1 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| number2 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| operator | add | add | 任意設定項目（用途に応じて指定） | いいえ |
| round-type | none | none | 任意設定項目（用途に応じて指定） | いいえ |
| precision | string | "" | 画像一致の厳しさ（%） | いいえ |

#### E-43 乱数を記憶 (`assign-random-number-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| min-number | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| max-number | number | 100 | 任意設定項目（用途に応じて指定） | いいえ |
| precision | number | 0 | 画像一致の厳しさ（%） | いいえ |
| zero-fill | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |

#### E-44 コピー内容を記憶 (`assign-clipboard-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |

#### E-45 クリップボードへコピー (`copy-to-clipboard`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### E-46 実行中に入力 (`assign-live-input-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### E-47 ファイル更新日時を記憶 (`assign-file-modification-timestamp-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 日時 | 値やウィンドウを保持する変数名 | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| timestamp | modification / True / False | modification / True / False | タイムスタンプ付与の有無 | いいえ |
| format | string | yyyy-mm-dd_hh:mm:ss | 任意設定項目（用途に応じて指定） | いいえ |

#### E-48 ファイルサイズを記憶 (`assign-file-size-to-string-variable`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | サイズ | 値やウィンドウを保持する変数名 | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| unit | string | bytes | 任意設定項目（用途に応じて指定） | いいえ |

#### E-49 最新ファイル・フォルダを取得 (`find-newest-file-from-fixed-directory`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | ファイル保存場所 | 値やウィンドウを保持する変数名 | いいえ |
| file-or-dir | file | file | 任意設定項目（用途に応じて指定） | いいえ |
| date-check | string | 更新日時 | 任意設定項目（用途に応じて指定） | いいえ |
| number | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |


## F. 文字抽出
- 括弧・引用符号から
- 区切り文字から
- 改行・空白を削除
- ファイルパスから
- ルールにマッチ
- 置換
- 文字変換
- 日付形式変換
- 1行ずつループ

### パラメータ定義（操作F）

#### F-50 文字列抽出（括弧・引用符号） (`parse-brackets`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-variable | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-variable | string | 抽出文字 | 任意設定項目（用途に応じて指定） | いいえ |
| bracket-types | string/list | ['()'] | 任意設定項目（用途に応じて指定） | いいえ |
| index | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| strip | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |

#### F-51 文字抽出（区切り文字） (`parse-delimiters`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-variable | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-variable | string | 抽出文字 | 任意設定項目（用途に応じて指定） | いいえ |
| delimiter-type | string | , | 任意設定項目（用途に応じて指定） | いいえ |
| custom-str | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| index | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |

#### F-52 文字列抽出（改行・空白を削除） (`parse-break-and-space`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| break-space | break / space / both | break | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| all | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| head | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| end | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |

#### F-53 ファイル・フォルダ名抽出（ファイルパス） (`extract-fname`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-variable | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-variable | string | ファイル名 | 任意設定項目（用途に応じて指定） | いいえ |
| extension | False / png / jpg / bmp | False | 保存ファイルの拡張子 | いいえ |

#### F-54 文字列抽出（ルールにマッチする） (`parse-regex`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-variable | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-variable | string | 抽出文字 | 任意設定項目（用途に応じて指定） | いいえ |
| regex | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| option | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### F-55 文字を置換 (`replace-strings`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-variable | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-variable | string | 置換結果 | 任意設定項目（用途に応じて指定） | いいえ |
| src-str | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-str | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### F-56 文字変換 (`convert-character-type`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | いいえ |
| type | string | z2h-all | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |

#### F-57 日付の形式を変換 (`convert-date-format`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| date | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| before-format | string | yyyy/mm/dd | 任意設定項目（用途に応じて指定） | いいえ |
| before-custom | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| format | string | yyyy/mm/dd | 任意設定項目（用途に応じて指定） | いいえ |
| custom | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 変換結果 | 値やウィンドウを保持する変数名 | いいえ |

#### F-58 文字抽出ループ（1行ずつ） (`loop-by-line`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-variable | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-variable | string | ライン | 任意設定項目（用途に応じて指定） | いいえ |


## G. 分岐
- 文字列
- 数値
- 日付
- ファイル・フォルダの有/無を確認
- 画像

### パラメータ定義（操作G）

#### G-59 文字列比較 (`compare-strings-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string1 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| string2 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| match | string | full | 任意設定項目（用途に応じて指定） | いいえ |

#### G-60 数値比較 (`compare-numbers-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| number | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| comparator | any | 0 | 任意設定項目（用途に応じて指定） | いいえ |

#### G-61 日付比較 (`compare-dates-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| date1 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| date2 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| format1 | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |
| format2 | string | yyyy-mm-dd | 任意設定項目（用途に応じて指定） | いいえ |
| comparator | string | eq | 任意設定項目（用途に応じて指定） | いいえ |

#### G-62 ファイル・フォルダの有/無を確認 (`search-file-from-directory-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| file-name | string | "" | 保存ファイル名（拡張子なし） | いいえ |
| file-or-dir | file / dir | file | 任意設定項目（用途に応じて指定） | いいえ |
| dir-path | string | "" | 保存先フォルダ | いいえ |

#### G-63 画像を探す (`find-image-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| filename | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| precision | number (%) | 85 | 画像一致の厳しさ（%） | いいえ |
| interval | number (sec) | 5 | 待機・間隔の秒数 | いいえ |
| noise-filter | number (%) | 100.0 | 画像検索時のノイズ除去率 | いいえ |
| search-area-type | screen / window / area | - | 検索範囲の種類 | いいえ |
| search-area | rect (x1,y1)-(x2,y2) | (0,0)-(0,0) | 検索座標の範囲指定 | いいえ |


## H. 繰り返し
- 繰り返し
- 繰り返しを抜ける
- 繰り返しの最初に戻る

### パラメータ定義（操作H）

#### H-64 繰り返し (`loop-n-times`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| count | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| type | string | times | 任意設定項目（用途に応じて指定） | いいえ |

#### H-65 繰り返しを抜ける (`break-loop`)

このステップにパラメータはありません。

#### H-66 繰り返しの最初に戻る (`continue-loop`)

このステップにパラメータはありません。

## I. ファイル・フォルダ
- ファイル
  - 開く / 読み込む / 書き込む / 移動 / コピー / 削除 / 名前変更 / 圧縮 / 解凍
- フォルダ
  - 開く / 作成 / ループ
- ファイル名加工
  - 文字挿入 / 日付挿入 / 参照ID挿入

### パラメータ定義（操作I）

#### I-67 ファイルを開く (`open-static-file-name`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| interval | number (sec) | 3 | 待機・間隔の秒数 | いいえ |
| maximized | True / False | - | 起動時のウィンドウ状態を切り替える項目 | いいえ |

#### I-68 ファイルを移動 (`move-fixed-file-to-fixed-directory`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |

#### I-69 テキストファイルを読み込む (`read-file`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| encoding | auto | auto | 任意設定項目（用途に応じて指定） | いいえ |
| custom-encoding | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### I-70 テキストファイルに書き込む (`write-file`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メッセージや対象文字列 | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| mode | create / append など | create | 任意設定項目（用途に応じて指定） | いいえ |
| encoding | system-default / utf-8 など | system-default | 任意設定項目（用途に応じて指定） | いいえ |
| custom-encoding | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### I-71 フォルダを開く (`open-fixed-directory-name`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |

#### I-72 フォルダを作成 (`create-directory`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| dir-path | string | "" | 保存先フォルダ | いいえ |
| dir-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |

#### I-73 フォルダ内をループ (`loop-directory-contents`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | ファイル保存場所 | 値やウィンドウを保持する変数名 | いいえ |
| target | file / dir | file | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| extension | .txt / png / jpg / bmp | .txt / png / jpg / bmp | 保存ファイルの拡張子 | いいえ |
| order | dict_windows など | dict_windows | 任意設定項目（用途に応じて指定） | いいえ |
| case-sensitive | case-enable / case-disable | case-disable | 任意設定項目（用途に応じて指定） | いいえ |

#### I-74 ファイル・フォルダ名の変更 (`rename-file-or-directory`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| extension-opt | extension-yes / extension-no | extension-yes | 任意設定項目（用途に応じて指定） | いいえ |
| rename | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| act-option | overwrite / skip など | overwrite | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |

#### I-75 ファイル・フォルダをコピー (`copy-file-or-directory`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| act-check | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |

#### I-76 ファイル・フォルダを削除 (`delete-file-or-directory`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| delete | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### I-77 ファイル・フォルダを圧縮 (`compress-file-or-directory`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| compression-method | zip など | zip | 任意設定項目（用途に応じて指定） | いいえ |
| src-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | type-empty / type-input など | type-empty | 任意設定項目（用途に応じて指定） | いいえ |
| password | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |

#### I-78 ファイル・フォルダに解凍 (`decompress-file`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| decompression-method | zip など | zip | 任意設定項目（用途に応じて指定） | いいえ |
| src-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | type-empty / type-input など | type-empty | 任意設定項目（用途に応じて指定） | いいえ |
| password | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |

#### I-79 文字をファイル名に挿入 (`prepend-string-to-variable-filename`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| string | string | "" | メッセージや対象文字列 | いいえ |
| position | head / tail など | head | 任意設定項目（用途に応じて指定） | いいえ |
| update | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### I-80 日付をファイル名に挿入 (`prepend-date-to-variable-filename`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| position | head / tail など | head | 任意設定項目（用途に応じて指定） | いいえ |
| update | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### I-81 参照IDをファイル名に挿入 (`prepend-variable-to-file`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| position | head / tail など | head | 任意設定項目（用途に応じて指定） | いいえ |
| update-var | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

## J. エクセル・CSV
- ブック
  - ブックを開く
  - ブックを覚える
  - ブックを保存
  - ブックを閉じる
- シート操作
  - 新規作成
  - 削除
  - 切り替え
  - 移動・コピー
  - 名前取得
  - 名前変更
- セル操作
  - 範囲指定
  - 指定範囲の移動
  - 指定範囲の削除
  - 指定範囲にセルを挿入
  - 値を取得
  - 値を入力
  - セルをコピー
  - セルを貼り付け
  - 位置を取得
  - 最終行取得
  - 最終列取得
  - 列計算
  - マクロ実行
  - 行ループ
  - 列ループ
- CSV読込ループ

### パラメータ定義（操作J）

#### J-82 エクセルブックを開く (`run-excel`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | エクセル | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| password-type | type-empty | type-empty | 任意設定項目（用途に応じて指定） | いいえ |
| ciphertext | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| nonce | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| encryption | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| maximized | True / False | - | 起動時のウィンドウ状態を切り替える項目 | いいえ |
| update-links | ask | ask | 任意設定項目（用途に応じて指定） | いいえ |

#### J-83 開いているエクセルブックを覚える (`remember-open-excel-book`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | エクセル | 任意設定項目（用途に応じて指定） | いいえ |
| target | foremost | foremost | 任意設定項目（用途に応じて指定） | いいえ |
| bookname | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-84 エクセルブックを保存 (`save-excel-book`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| overwrite | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |

#### J-85 エクセルブックを閉じる (`close-excel-book`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-86 新規エクセルシート (`create-excel-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-87 エクセルシート削除 (`delete-excel-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-88 エクセルシート切り替え (`switch-excel-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| switch | string | switch-name | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| index | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |

#### J-89 エクセルシート移動・コピー (`move-excel-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-book | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-position | string | last | 任意設定項目（用途に応じて指定） | いいえ |
| target-sheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| copy | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| copy-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-90 エクセルシート名取得 (`get-excel-sheet-name`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 名前 | 値やウィンドウを保持する変数名 | いいえ |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-91 エクセルシート名変更 (`rename-excel-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| rename | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-92 エクセル範囲指定 (`select-excel-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-93 エクセル指定範囲の移動 (`offset-excel-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| offset-x | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |
| offset-y | number | 0 | 任意設定項目（用途に応じて指定） | いいえ |

#### J-94 エクセル指定範囲を削除 (`delete-excel-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| shift-type | string | up | 任意設定項目（用途に応じて指定） | いいえ |

#### J-95 エクセル指定範囲にセルを挿入 (`insert-excel-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| shift-type | string | down | 任意設定項目（用途に応じて指定） | いいえ |

#### J-96 エクセルのセル値を取得 (`get-excel-values`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| type | string | value-formatted | 任意設定項目（用途に応じて指定） | いいえ |

#### J-97 エクセルのセル値を入力 (`set-excel-values`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| single-cell | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### J-98 エクセルのセルをコピー (`copy-excel-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### J-99 エクセルのセルを貼り付け (`paste-excel-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| option | string | None | 任意設定項目（用途に応じて指定） | いいえ |

#### J-100 エクセルのセル位置を取得 (`get-excel-address`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| variable2 | string | 列 | 任意設定項目（用途に応じて指定） | いいえ |
| variable3 | string | 行 | 任意設定項目（用途に応じて指定） | いいえ |
| var-type | string | standard | 任意設定項目（用途に応じて指定） | いいえ |
| format | string | a1 | 任意設定項目（用途に応じて指定） | いいえ |

#### J-101 エクセル最終行取得 (`get-excel-last-row`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-type | string | col | 任意設定項目（用途に応じて指定） | いいえ |
| target-col | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 最終行 | 値やウィンドウを保持する変数名 | いいえ |

#### J-102 エクセル最終列取得 (`get-excel-last-column`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-type | string | row | 任意設定項目（用途に応じて指定） | いいえ |
| target-row | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 最終列 | 値やウィンドウを保持する変数名 | いいえ |

#### J-103 エクセルの列を計算 (`calculate-excel-column`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| base-column | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| operator | string | add | 任意設定項目（用途に応じて指定） | いいえ |
| amount | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 計算列 | 値やウィンドウを保持する変数名 | いいえ |

#### J-104 エクセルマクロ実行 (`run-excel-macro`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| macro-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| arguments | list | [] | コマンドライン引数 | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| is-display-alerts | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### J-105 エクセル行ループ (`loop-excel-row`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| count | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-value | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-row | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| end-condition-type | string | row | 任意設定項目（用途に応じて指定） | いいえ |
| start-cell | string | A1 | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 行番号 | 値やウィンドウを保持する変数名 | いいえ |
| variable2 | string | セル値 | 任意設定項目（用途に応じて指定） | いいえ |
| get-value-type | string | value-formatted | 任意設定項目（用途に応じて指定） | いいえ |

#### J-106 エクセル列ループ (`loop-excel-col`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| excel | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| count | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-value | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-col | string | A | 任意設定項目（用途に応じて指定） | いいえ |
| end-condition-type | string | col | 任意設定項目（用途に応じて指定） | いいえ |
| start-cell | string | A1 | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 列名 | 値やウィンドウを保持する変数名 | いいえ |
| variable2 | string | セル値 | 任意設定項目（用途に応じて指定） | いいえ |
| get-value-type | string | value-formatted | 任意設定項目（用途に応じて指定） | いいえ |

#### J-107 CSV読込ループ (`loop-csv`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| ignore-first | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| variables | list | [[1, 'カラム1']] | 任意設定項目（用途に応じて指定） | いいえ |

## K. スプレッドシート
- スプレッドシート
  - 作成
  - 読み込む
  - 削除
  - 名前変更
  - URL取得
- シート
  - 新規作成
  - 削除
  - 移動
  - コピー
  - 名前取得
  - 名前変更
- セル操作
  - 指定範囲の削除
  - 指定範囲にセルを挿入
  - 値を取得
  - 値を入力
  - セルをコピー・貼り付け
  - 最終行取得
  - 行ループ
  - 列ループ

### パラメータ定義（操作K）

#### K-108 スプレッドシートを作成 (`create-spreadsheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| account | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| spreadsheet | string | スプレッドシート | 任意設定項目（用途に応じて指定） | いいえ |

#### K-109 スプレッドシートを読み込む (`remember-spreadsheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| account | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| spreadsheet | string | スプレッドシート | 任意設定項目（用途に応じて指定） | いいえ |
| method | string | url | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| id | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-110 スプレッドシートを削除 (`delete-spreadsheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| account | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| method | string | url | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| id | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-111 スプレッドシート名を変更 (`rename-spreadsheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| account | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| method | string | url | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| id | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| rename | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-112 スプレッドシートのURL取得 (`get-spreadsheet-url`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | url | 値やウィンドウを保持する変数名 | いいえ |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-113 新規シート (`create-spreadsheet-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-114 シート削除 (`delete-spreadsheet-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-115 スプレッドシートのシート移動 (`move-spreadsheet-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-position | string | last | 任意設定項目（用途に応じて指定） | いいえ |
| target-sheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-116 スプレッドシートのシートコピー (`copy-spreadsheet-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| copy-sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-117 スプレッドシートのシート名取得 (`get-spreadsheet-sheet-name`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | 名前 | 値やウィンドウを保持する変数名 | いいえ |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-position | string | by-index | 任意設定項目（用途に応じて指定） | いいえ |
| target-index | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-118 スプレッドシートのシート名変更 (`rename-spreadsheet-sheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| rename | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### K-119 スプレッドシート指定範囲を削除 (`delete-spreadsheet-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| shift-type | string | rows | 任意設定項目（用途に応じて指定） | いいえ |

#### K-120 スプレッドシート指定範囲にセルを挿入 (`insert-spreadsheet-range`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| shift-type | string | rows | 任意設定項目（用途に応じて指定） | いいえ |

#### K-121 スプレッドシートのセル値を取得 (`get-spreadsheet-values`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| type | string | formatted-value | 任意設定項目（用途に応じて指定） | いいえ |

#### K-122 スプレッドシートのセル値を入力 (`set-spreadsheet-values`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| single-cell | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### K-123 スプレッドシートのセルをコピー・貼り付け (`copy-paste-spreadsheet`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| src-sheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| src-range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-sheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-range | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| paste-type | string | PASTE_NORMAL | 任意設定項目（用途に応じて指定） | いいえ |

#### K-124 スプレッドシート最終行取得 (`get-spreadsheet-last-row`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| target-type | string | col | 任意設定項目（用途に応じて指定） | いいえ |
| target-col | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 最終行 | 値やウィンドウを保持する変数名 | いいえ |

#### K-125 スプレッドシート行ループ (`loop-spreadsheet-row`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| count | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-value | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-row | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| end-condition-type | string | row | 任意設定項目（用途に応じて指定） | いいえ |
| start-cell | string | A1 | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 行番号 | 値やウィンドウを保持する変数名 | いいえ |
| variable2 | string | セル値 | 任意設定項目（用途に応じて指定） | いいえ |

#### K-126 スプレッドシート列ループ (`loop-spreadsheet-col`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| spreadsheet | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| sheet-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| count | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-value | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| terminate-col | string | A | 任意設定項目（用途に応じて指定） | いいえ |
| end-condition-type | string | col | 任意設定項目（用途に応じて指定） | いいえ |
| start-cell | string | A1 | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 列名 | 値やウィンドウを保持する変数名 | いいえ |
| variable2 | string | セル値 | 任意設定項目（用途に応じて指定） | いいえ |

## L. ウェブブラウザ
- 起動
- 起動（ユーザ情報引継）
- 閉じる
- 派生ブラウザ画面記憶
- URL移動
- URL移動（Basic認証）
- Cookie追加
- ページ操作
  - HTMLクリック
  - HTMLショートカットキー
  - HTML選択
  - HTMLチェック確認
  - HTMLキーボード入力
  - HTMLキーボード入力（パスワード）
  - HTMLドロップダウン操作
  - HTML文字列抽出
  - HTMLリンク抽出
  - HTML画像URL抽出
  - HTML画像ダウンロード
  - HTML表ダウンロード（CSV）
  - HTML属性抽出
  - HTMLポップアップクリック
  - HTMLポップアップ内容抽出
  - HTMLエレメント出現を待つ
  - JavaScript実行
- IFrame移動
  - IFrameに入る
  - IFrameから出る

### パラメータ定義（操作L）

#### L-127 ブラウザ起動 (`run-browser`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| vendor | string | assirobo_browser | 任意設定項目（用途に応じて指定） | いいえ |
| browser | string | ブラウザ | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| arguments | string | "" | コマンドライン引数 | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| maximized | True / False | - | 起動時のウィンドウ状態を切り替える項目 | いいえ |
| plugins | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| iemode | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### L-128 ブラウザ起動（ユーザ情報引継） (`run-browser-with-profile`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| vendor | string | google_chrome_auto | 任意設定項目（用途に応じて指定） | いいえ |
| browser | string | ブラウザ | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| profile-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| maximized | True / False | - | 起動時のウィンドウ状態を切り替える項目 | いいえ |
| plugins | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### L-129 ブラウザを閉じる (`close-browser`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-130 派生ブラウザ画面記憶 (`remember-focused-browser-window`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| new-browser | string | 派生ブラウザ | 任意設定項目（用途に応じて指定） | いいえ |

#### L-131 ブラウザURL移動 (`visit-url`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-132 ブラウザURL移動（Basic認証） (`visit-url-with-basic-auth`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| user | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | string | type-empty | 任意設定項目（用途に応じて指定） | いいえ |
| ciphertext | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| nonce | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| encryption | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |

#### L-133 ブラウザCookieを追加 (`set-browser-cookie`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| value | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| domain | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| secure | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| httpOnly | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| expiry | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-134 HTMLクリック (`click-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| click-type | string | single | 任意設定項目（用途に応じて指定） | いいえ |

#### L-135 HTMLショートカットキーを入力 (`type-html-hotkeys`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| key-0 | string | __null__ | 任意設定項目（用途に応じて指定） | いいえ |
| key-1 | string | __null__ | 任意設定項目（用途に応じて指定） | いいえ |
| key-2 | string | __null__ | 任意設定項目（用途に応じて指定） | いいえ |
| key-3 | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-136 HTML選択 (`focus-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-137 HTMLチェック確認 (`check-html-checkbox-or-radiobutton`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-138 HTMLキーボード入力 (`send-text-to-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| text | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| reset | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### L-139 HTMLキーボード入力（パスワード） (`send-password-to-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | string | type-input | 任意設定項目（用途に応じて指定） | いいえ |
| ciphertext | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| nonce | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| encryption | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| overwrite | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### L-140 HTMLドロップダウン操作 (`set-dropdown-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| value-type | string | text | 任意設定項目（用途に応じて指定） | いいえ |
| value | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| multi-select | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### L-141 HTML文字列抽出 (`retrieve-text-of-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 抽出文字 | 値やウィンドウを保持する変数名 | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dropdown-all-text | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### L-142 HTMLリンク抽出 (`retrieve-link-of-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | リンク | 値やウィンドウを保持する変数名 | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-143 HTML画像URL抽出 (`retrieve-src-of-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 画像URL | 値やウィンドウを保持する変数名 | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-144 HTML画像ダウンロード (`download-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |

#### L-145 HTML表ダウンロード（CSV） (`download-html-csv`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |

#### L-146 HTML属性抽出 (`retrieve-attribute-of-html-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| attribute-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 属性 | 値やウィンドウを保持する変数名 | いいえ |

#### L-147 HTMLポップアップクリック (`click-html-alert`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| button | string | OK | 任意設定項目（用途に応じて指定） | いいえ |

#### L-148 HTMLポップアップ内容抽出 (`retrieve-text-of-html-alert`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | ポップアップ内容 | 値やウィンドウを保持する変数名 | いいえ |

#### L-149 HTMLエレメント出現を待つ (`search-html-element-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| selector-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| selector | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| timeout | number (sec) | 10 | 待機の上限時間（秒） | いいえ |

#### L-150 JavaScript実行 (`run-javascript-in-browser`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| javascript | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |

#### L-151 IFrameに入る (`switch-html-iframe`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| iframe-id-type | string | xpath | 任意設定項目（用途に応じて指定） | いいえ |
| iframe-id | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### L-152 IFrameから出る (`escape-html-iframe`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| browser | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

## M. メール
- 送信
- 受信
- 送信（Gmail）
- 受信（Gmail）
- 送信（Microsoft）
- 受信（Microsoft）

### パラメータ定義（操作M）

#### M-153 メールを送信 (`send-email`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| server | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| protocol | string | STARTTLS | 任意設定項目（用途に応じて指定） | いいえ |
| port | number | 587 | 任意設定項目（用途に応じて指定） | いいえ |
| sender | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| login | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | string | type-empty | 任意設定項目（用途に応じて指定） | いいえ |
| ciphertext | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| nonce | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| encryption | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| receiver | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver-cc | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver-bcc | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| subject | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| body | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| attachment | list | [] | 任意設定項目（用途に応じて指定） | いいえ |
| skip-file | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### M-154 メール受信 (`receive-emails`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| server | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| protocol | string | SSL/TLS | 任意設定項目（用途に応じて指定） | いいえ |
| port | number | 993 | 任意設定項目（用途に応じて指定） | いいえ |
| receiver | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | string | type-empty | 任意設定項目（用途に応じて指定） | いいえ |
| ciphertext | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| nonce | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| encryption | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| filters | list | [] | 任意設定項目（用途に応じて指定） | いいえ |
| attachments-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| unread-only | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| mark-read | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| mark-flag | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### M-155 メールを送信（Gmail） (`send-email-gmail`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| login | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver-cc | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver-bcc | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| subject | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| body | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| attachment | list | [] | 任意設定項目（用途に応じて指定） | いいえ |
| skip-file | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### M-156 メール受信（Gmail） (`receive-emails-gmail`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| receiver | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| filters | list | [] | 任意設定項目（用途に応じて指定） | いいえ |
| attachments-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| unread-only | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| mark-read | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| mark-flag | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| dl-inline | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| dl-not-multipart | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |

#### M-157 メールを送信（Microsoft） (`send-email-microsoft`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| login | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver-cc | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| receiver-bcc | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| subject | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| body | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| attachment | list | [] | 任意設定項目（用途に応じて指定） | いいえ |
| skip-file | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

#### M-158 メール受信（Microsoft） (`receive-emails-microsoft`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| receiver | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| filters | list | [] | 任意設定項目（用途に応じて指定） | いいえ |
| attachments-path | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| unread-only | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| mark-read | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |
| mark-flag | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

## N. 特殊アプリ操作
- 操作記録
- クリック
- 文字入力
- 文字入力（パスワード）
- 座標取得
- 文字取得

### パラメータ定義（操作N）

#### N-159 アプリをクリック (`click-uia-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| window | window-ref | __uia_focused_window__ | 対象ウィンドウ指定（既定は最前面など） | いいえ |
| controlType | number | 50000 | 任意設定項目（用途に応じて指定） | いいえ |
| frameworkId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| className | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| identifier | string | name | 任意設定項目（用途に応じて指定） | いいえ |
| automationId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| index | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| depth | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| ancestors | string | None | 任意設定項目（用途に応じて指定） | いいえ |
| search-level | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| clicktype | string | click-uia | 任意設定項目（用途に応じて指定） | いいえ |

#### N-160 アプリ文字入力 (`send-text-to-uia-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| window | window-ref | __uia_focused_window__ | 対象ウィンドウ指定（既定は最前面など） | いいえ |
| controlType | number | 50000 | 任意設定項目（用途に応じて指定） | いいえ |
| frameworkId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| className | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| identifier | string | name | 任意設定項目（用途に応じて指定） | いいえ |
| automationId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| index | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| depth | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| ancestors | string | None | 任意設定項目（用途に応じて指定） | いいえ |
| search-level | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| string | string | "" | メッセージや対象文字列 | いいえ |

#### N-161 アプリ文字入力（パスワード） (`send-password-to-uia-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| window | window-ref | __uia_focused_window__ | 対象ウィンドウ指定（既定は最前面など） | いいえ |
| controlType | number | 50000 | 任意設定項目（用途に応じて指定） | いいえ |
| frameworkId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| className | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| identifier | string | name | 任意設定項目（用途に応じて指定） | いいえ |
| automationId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| index | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| depth | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| ancestors | string | None | 任意設定項目（用途に応じて指定） | いいえ |
| search-level | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| password-type | string | type-input | 任意設定項目（用途に応じて指定） | いいえ |
| ciphertext | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| nonce | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| encryption | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |

#### N-162 アプリ座標取得 (`get-uia-element-clickable-point`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| window | window-ref | __uia_focused_window__ | 対象ウィンドウ指定（既定は最前面など） | いいえ |
| controlType | number | 50000 | 任意設定項目（用途に応じて指定） | いいえ |
| frameworkId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| className | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| identifier | string | name | 任意設定項目（用途に応じて指定） | いいえ |
| automationId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| index | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| depth | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| ancestors | string | None | 任意設定項目（用途に応じて指定） | いいえ |
| search-level | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| x | string | X | 任意設定項目（用途に応じて指定） | いいえ |
| y | string | Y | 任意設定項目（用途に応じて指定） | いいえ |

#### N-163 アプリ文字取得 (`get-text-from-uia-element`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| window | window-ref | __uia_focused_window__ | 対象ウィンドウ指定（既定は最前面など） | いいえ |
| controlType | number | 50000 | 任意設定項目（用途に応じて指定） | いいえ |
| frameworkId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| className | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| identifier | string | name | 任意設定項目（用途に応じて指定） | いいえ |
| automationId | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| index | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| depth | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| ancestors | string | None | 任意設定項目（用途に応じて指定） | いいえ |
| search-level | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | 取得文字 | 値やウィンドウを保持する変数名 | いいえ |

## O. API
- Web API
- JSON
  - JSON値取得
  - JSON型確認

### パラメータ定義（操作O）

#### O-164 Web API (`api-web`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| method | string | GET | 任意設定項目（用途に応じて指定） | いいえ |
| services | string | custom-get | 任意設定項目（用途に応じて指定） | いいえ |
| url | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| queries | object | {} | 任意設定項目（用途に応じて指定） | いいえ |
| headers | object | {} | 任意設定項目（用途に応じて指定） | いいえ |
| body | string | form-data | 任意設定項目（用途に応じて指定） | いいえ |
| form-data | object | {} | 任意設定項目（用途に応じて指定） | いいえ |
| raw | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| json | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| timeout | number (sec) | 10 | 待機の上限時間（秒） | いいえ |
| res-status | string | [応答ステータス] | 格納先変数 | いいえ |
| res-headers | string | [応答ヘッダ] | 格納先変数 | いいえ |
| res-data | string | [応答データ] | 格納先変数 | いいえ |
| res-content-type | string | [応答コンテントタイプ] | 格納先変数 | いいえ |

#### O-165 JSON値取得 (`get-json-values`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| src-variable | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| dst-variable | string | データ | 任意設定項目（用途に応じて指定） | いいえ |
| type | string | dict | 任意設定項目（用途に応じて指定） | いいえ |
| dict | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| array | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| custom | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### O-166 JSON型確認 (`check-json-type`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| variable | string | "" | 値やウィンドウを保持する変数名 | いいえ |
| type | string | dict | 任意設定項目（用途に応じて指定） | いいえ |
| dict | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| array | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| custom | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| check-type | string | string | 任意設定項目（用途に応じて指定） | いいえ |

## P. シナリオ整理
- グループ化
- メモ
- 通知音を再生

### パラメータ定義（操作P）

#### P-167 グループ (`group-commands`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### P-168 メモ (`add-memo`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| string | string | "" | メモの内容 | いいえ |

#### P-169 通知音を再生 (`play-sound`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| sound | string | Beep | 任意設定項目（用途に応じて指定） | いいえ |
| path | string | "" | 実行対象のパス。未設定では動かない | いいえ |
| count | number | 1 | 任意設定項目（用途に応じて指定） | いいえ |
| interval | number (sec) | 1 | 待機・間隔の秒数 | いいえ |
| async | True / False | False | 任意設定項目（用途に応じて指定） | いいえ |

## Q. 別シナリオ実行・継承
- 別シナリオ実行
- 親シナリオからデータを継承
- 親シナリオからパスワードを継承
- 親シナリオからウィンドウを継承
- 親シナリオからエクセルを継承
- 親シナリオからブラウザを継承

### パラメータ定義（操作Q）

#### Q-170 別のシナリオを実行 (`run-external-scenario-and-branch`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| scenario-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| uuid | string | "" | 任意設定項目（用途に応じて指定） | いいえ |

#### Q-171 親シナリオからデータを継承 (`inherit-variables`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| uuid | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | データ | 値やウィンドウを保持する変数名 | いいえ |
| overwrite | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| scenario-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| type | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| variables | list | [] | 任意設定項目（用途に応じて指定） | いいえ |

#### Q-172 親シナリオからパスワードを継承 (`inherit-passwords`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| uuid | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| password-id | string | パスワード | 任意設定項目（用途に応じて指定） | いいえ |
| overwrite | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| scenario-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| type | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| passwords | list | [] | 任意設定項目（用途に応じて指定） | いいえ |

#### Q-173 親シナリオからウィンドウを継承 (`inherit-windows`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| uuid | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| variable | string | ウィンドウ | 値やウィンドウを保持する変数名 | いいえ |
| overwrite | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| scenario-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| type | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| windows | list | [] | 任意設定項目（用途に応じて指定） | いいえ |

#### Q-174 親シナリオからエクセルを継承 (`inherit-excel`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| uuid | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| excel | string | エクセル | 任意設定項目（用途に応じて指定） | いいえ |
| overwrite | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| scenario-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| type | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| excels | list | [] | 任意設定項目（用途に応じて指定） | いいえ |

#### Q-175 親シナリオからブラウザを継承 (`inherit-browsers`)

| パラメータ | 型/候補 | 既定値 | 説明 | 必須 |
| --- | --- | --- | --- | --- |
| uuid | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| browser | string | ブラウザ | 任意設定項目（用途に応じて指定） | いいえ |
| overwrite | True / False | True | 任意設定項目（用途に応じて指定） | いいえ |
| scenario-name | string | "" | 任意設定項目（用途に応じて指定） | いいえ |
| type | string | single | 任意設定項目（用途に応じて指定） | いいえ |
| browsers | list | [] | 任意設定項目（用途に応じて指定） | いいえ |

