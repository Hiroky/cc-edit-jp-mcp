# FastMCP 2.12.5 - HTTP Transport 完全ガイド

このドキュメントでは、FastMCP 2.12.5 で JSON-RPC over HTTP を実装する正確な方法を説明します。

## 目次

1. [重要な変更点](#重要な変更点)
2. [推奨される実装方法](#推奨される実装方法)
3. [セッション管理について](#セッション管理について)
4. [実装例](#実装例)
5. [API リファレンス](#apiリファレンス)

---

## 重要な変更点

### FastMCP 2.3.2 以降の変更

**非推奨となったメソッド:**
- `streamable_http_app()` - 廃止予定（DeprecationWarning）
- `sse_app()` - 廃止予定（DeprecationWarning）
- `run_sse_async()` - 廃止予定（DeprecationWarning）
- `run_streamable_http_async()` - 廃止予定（DeprecationWarning）

**推奨されるメソッド:**
- `http_app()` - **これを使用してください**
- `run()` または `run_async()` with `transport="http"`

### なぜ http_app() が推奨されるのか

1. **統一されたインターフェース**: 単一のメソッドで StreamableHTTP と SSE の両方をサポート
2. **将来性**: 今後の FastMCP のバージョンでも安定して動作
3. **柔軟性**: ステートフル/ステートレスモードの両方をサポート
4. **シンプル**: より直感的で使いやすい API

---

## 推奨される実装方法

### 1. 基本的な HTTP サーバー（最も推奨）

```python
from fastmcp import FastMCP
import uvicorn

app = FastMCP(name="my-server")

@app.tool()
async def my_tool(arg: str) -> str:
    return f"Result: {arg}"

# HTTP アプリを作成（推奨方法）
http_app = app.http_app()

# Uvicorn で起動
uvicorn.run(http_app, host="127.0.0.1", port=8000)
```

**サーバー URL**: `http://127.0.0.1:8000/mcp`

**特徴**:
- デフォルトでステートフルモード（セッション管理あり）
- StreamableHTTP トランスポートを使用
- 双方向通信をサポート
- セッション ID は自動管理

### 2. run() メソッドを使用（開発に最適）

```python
from fastmcp import FastMCP

app = FastMCP(name="my-server")

@app.tool()
async def my_tool(arg: str) -> str:
    return f"Result: {arg}"

# 最もシンプルな起動方法
app.run(
    transport="http",  # または "streamable-http"
    host="127.0.0.1",
    port=8000,
)
```

**特徴**:
- 最もシンプルで直感的
- 開発・テストに最適
- Uvicorn の設定を自動で行う

### 3. ステートレス HTTP サーバー（サーバーレス環境向け）

```python
from fastmcp import FastMCP
import uvicorn

app = FastMCP(name="my-server")

@app.tool()
async def my_tool(arg: str) -> str:
    return f"Result: {arg}"

# ステートレスモードで HTTP アプリを作成
http_app = app.http_app(stateless_http=True)

uvicorn.run(http_app, host="127.0.0.1", port=8000)
```

**特徴**:
- リクエスト間でセッション状態を保持しない
- 各リクエストで新しいトランスポートを作成
- AWS Lambda、Google Cloud Functions などに最適
- セッション ID は相関のために使用される

---

## セッション管理について

### ステートフルモード（デフォルト）

```python
http_app = app.http_app(stateless_http=False)  # デフォルト
```

**動作**:
- `StreamableHTTPSessionManager` がセッションを管理
- セッション ID（`Mcp-Session-Id` ヘッダー）で識別
- セッション状態はサーバー側で保持
- 複数リクエスト間でコンテキストを維持

**適した用途**:
- 長時間実行されるサーバー
- セッション固有の状態が必要な場合
- シングルインスタンス展開

### ステートレスモード

```python
http_app = app.http_app(stateless_http=True)
```

**動作**:
- リクエストごとに新しいトランスポートを作成
- セッション状態はサーバー側で保持されない
- セッション ID は相関目的でのみ使用
- 各リクエストは独立して処理される

**適した用途**:
- サーバーレス環境（AWS Lambda、Cloud Functions など）
- ロードバランサー配下の複数インスタンス
- ステートレスな API として運用
- Amazon Bedrock AgentCore（ステートレス必須）

### セッション ID は必須か？

**いいえ、セッション ID は必須ではありません。**

FastMCP 2.12.5 では：
- セッション ID がない場合、自動的に生成される
- クライアントは `Mcp-Session-Id` ヘッダーを送信できるが、必須ではない
- ステートレスモードでは、セッション ID は相関のためのみに使用される

**重要**: 以前のバージョン（2.3.x 以前）では、セッション ID が必須だった可能性がありますが、**現在のバージョンでは不要です**。

---

## 実装例

### 例1: 基本的なファイル編集サーバー

```python
from pathlib import Path
from fastmcp import FastMCP
import uvicorn

app = FastMCP(name="file-editor", version="1.0.0")

@app.tool()
async def edit_file(file_path: str, old_text: str, new_text: str) -> dict:
    """ファイルを編集する"""
    try:
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")
        new_content = content.replace(old_text, new_text, 1)
        path.write_text(new_content, encoding="utf-8")
        return {"success": True, "message": "編集完了"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    http_app = app.http_app()
    uvicorn.run(http_app, host="127.0.0.1", port=8000)
```

### 例2: カスタムパスの設定

```python
from fastmcp import FastMCP
import uvicorn

app = FastMCP(name="my-server")

@app.tool()
async def greet(name: str) -> str:
    return f"こんにちは、{name}さん！"

# カスタムパスを指定
http_app = app.http_app(path="/api/mcp")

uvicorn.run(http_app, host="127.0.0.1", port=8000)
# サーバーは http://127.0.0.1:8000/api/mcp で利用可能
```

### 例3: 環境変数での設定

```bash
# .env ファイルまたは環境変数
FASTMCP_HOST=0.0.0.0
FASTMCP_PORT=3000
FASTMCP_STREAMABLE_HTTP_PATH=/mcp/v1
FASTMCP_STATELESS_HTTP=false
FASTMCP_LOG_LEVEL=INFO
```

```python
from fastmcp import FastMCP
import fastmcp

app = FastMCP(name="my-server")

@app.tool()
async def greet(name: str) -> str:
    return f"こんにちは、{name}さん！"

# 環境変数から設定を読み込む
print(f"Host: {fastmcp.settings.host}")
print(f"Port: {fastmcp.settings.port}")
print(f"Path: {fastmcp.settings.streamable_http_path}")

# 環境変数の設定を使用して起動
app.run(transport="http")
```

### 例4: FastAPI との統合

```python
from fastapi import FastAPI
from fastmcp import FastMCP
import uvicorn

# FastAPI アプリを作成
fastapi_app = FastAPI()

@fastapi_app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

# FastMCP サーバーを作成
mcp = FastMCP(name="my-mcp-server")

@mcp.tool()
async def greet(name: str) -> str:
    return f"こんにちは、{name}さん！"

# MCP アプリを作成してマウント
mcp_app = mcp.http_app(path="/mcp")
fastapi_app.mount("/api", mcp_app)

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
    # MCP サーバーは http://127.0.0.1:8000/api/mcp で利用可能
```

### 例5: ミドルウェアの追加

```python
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

app = FastMCP(name="my-server")

@app.tool()
async def greet(name: str) -> str:
    return f"こんにちは、{name}さん！"

# CORS ミドルウェアを追加
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

http_app = app.http_app(middleware=middleware)
uvicorn.run(http_app, host="127.0.0.1", port=8000)
```

---

## API リファレンス

### FastMCP.http_app()

```python
def http_app(
    self,
    path: str | None = None,
    middleware: list[ASGIMiddleware] | None = None,
    json_response: bool | None = None,
    stateless_http: bool | None = None,
    transport: Literal["http", "streamable-http", "sse"] = "http",
) -> StarletteWithLifespan:
    """
    HTTP トランスポートを使用した Starlette アプリを作成します。

    Args:
        path: HTTP エンドポイントのパス（デフォルト: "/mcp"）
        middleware: アプリに適用するミドルウェアのリスト
        json_response: JSON レスポンス形式を使用するか（デフォルト: False）
        stateless_http: ステートレスモードを使用するか（デフォルト: False）
        transport: 使用するトランスポート（"http", "streamable-http", "sse"）

    Returns:
        設定された Starlette アプリケーション
    """
```

### FastMCP.run()

```python
def run(
    self,
    transport: Transport | None = None,
    show_banner: bool = True,
    **transport_kwargs: Any,
) -> None:
    """
    FastMCP サーバーを実行します。

    Args:
        transport: 使用するトランスポート（"stdio", "http", "sse", "streamable-http"）
        show_banner: サーバーバナーを表示するか（デフォルト: True）
        **transport_kwargs: トランスポート固有の追加引数
            - host: ホストアドレス（デフォルト: "127.0.0.1"）
            - port: ポート番号（デフォルト: 8000）
            - path: エンドポイントパス（デフォルト: "/mcp"）
            - stateless_http: ステートレスモード（デフォルト: False）
    """
```

### 設定オプション（環境変数）

| 環境変数 | デフォルト値 | 説明 |
|---------|------------|------|
| `FASTMCP_HOST` | `127.0.0.1` | バインドするホストアドレス |
| `FASTMCP_PORT` | `8000` | バインドするポート番号 |
| `FASTMCP_STREAMABLE_HTTP_PATH` | `/mcp` | HTTP エンドポイントのパス |
| `FASTMCP_STATELESS_HTTP` | `false` | ステートレスモードの有効化 |
| `FASTMCP_JSON_RESPONSE` | `false` | JSON レスポンス形式の使用 |
| `FASTMCP_LOG_LEVEL` | `INFO` | ログレベル |
| `FASTMCP_DEBUG` | `false` | デバッグモード |

---

## まとめ

### 推奨される実装パターン

1. **開発・テスト**: `app.run(transport="http")` を使用
2. **本番環境（単一インスタンス）**: `app.http_app()` でステートフルモード
3. **サーバーレス環境**: `app.http_app(stateless_http=True)` でステートレスモード
4. **既存アプリへの統合**: `app.http_app()` を FastAPI/Starlette にマウント

### 重要なポイント

1. ✅ **http_app() を使用** - streamable_http_app() は廃止予定
2. ✅ **セッション ID は不要** - 自動的に管理される
3. ✅ **ステートフル/ステートレスを選択** - 用途に応じて選択
4. ✅ **環境変数で設定可能** - デプロイメントが簡単

### 参考リンク

- [FastMCP 公式ドキュメント](https://gofastmcp.com/)
- [FastMCP GitHub リポジトリ](https://github.com/jlowin/fastmcp)
- [MCP 仕様](https://spec.modelcontextprotocol.io/)
