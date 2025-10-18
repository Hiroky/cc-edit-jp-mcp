# FastMCP HTTP Transport - クイックスタート

FastMCP 2.12.5 で HTTP サーバーを起動する最速の方法。

## 最もシンプルな方法（推奨）

### 1. run() メソッドを使用

```python
from fastmcp import FastMCP

app = FastMCP(name="my-server")

@app.tool()
async def hello(name: str) -> str:
    return f"Hello, {name}!"

# これだけ！
app.run(transport="http")
```

起動後、サーバーは `http://127.0.0.1:8000/mcp` で利用可能です。

### 2. http_app() + uvicorn を使用

```python
from fastmcp import FastMCP
import uvicorn

app = FastMCP(name="my-server")

@app.tool()
async def hello(name: str) -> str:
    return f"Hello, {name}!"

http_app = app.http_app()
uvicorn.run(http_app, host="127.0.0.1", port=8000)
```

## よくある設定

### ホストとポートを変更

```python
app.run(transport="http", host="0.0.0.0", port=3000)
```

### カスタムパスを設定

```python
http_app = app.http_app(path="/api/mcp")
uvicorn.run(http_app, host="127.0.0.1", port=8000)
# → http://127.0.0.1:8000/api/mcp
```

### ステートレスモード（サーバーレス環境向け）

```python
http_app = app.http_app(stateless_http=True)
uvicorn.run(http_app, host="127.0.0.1", port=8000)
```

## 環境変数で設定

`.env` ファイルまたは環境変数:

```bash
FASTMCP_HOST=0.0.0.0
FASTMCP_PORT=3000
FASTMCP_STREAMABLE_HTTP_PATH=/mcp
```

コード:

```python
app.run(transport="http")  # 環境変数から設定を読み込む
```

## 重要な注意点

### ✅ DO（推奨）

- `http_app()` を使用する
- `run(transport="http")` を使用する
- デフォルト設定をそのまま使う（セッション管理は自動）

### ❌ DON'T（非推奨）

- ~~`streamable_http_app()`~~ を使用しない（廃止予定）
- セッション ID を手動で管理する必要はない
- 複雑な設定は不要

## 次のステップ

詳細なガイド: [HTTP_TRANSPORT_GUIDE.md](./HTTP_TRANSPORT_GUIDE.md)
実装例: [../examples/http_transport_examples.py](../examples/http_transport_examples.py)
