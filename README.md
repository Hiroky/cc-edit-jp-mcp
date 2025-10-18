# Claude Edit MCP

FastMCP を使用した日本語対応ファイル編集MCP サーバー。

ClaudeCode の編集機能で文字コードエラーが発生する場合のフォールバックとして機能します。

## 特徴

- **UTF-8 対応**: 日本語を含むテキストファイルを正しく処理
- **HTTP インターフェース**: HTTP経由でアクセス可能
- **MCP プロトコル対応**: Claude と統合可能
- **複数の編集機能**:
  - 文字列置換 (`edit_file`)
  - ファイル書き込み (`write_file`)
  - 行置換 (`replace_line`)

## インストール

### 前提条件

- Python 3.11 以上
- uv (Python パッケージマネージャー)

### セットアップ

```bash
# リポジトリをクローン
cd claude-edit-mcp

# uv でプロジェクトをインストール
uv sync
```

## 使用方法

### HTTP サーバーとして起動

```bash
# デフォルト (127.0.0.1:8000)
uv run claude-edit-mcp

# カスタムホスト・ポート
uv run claude-edit-mcp --host 0.0.0.0 --port 5000
```

### Stdio モードで起動

```bash
# MCP プロトコル経由で直接使用
uv run claude-edit-mcp --mode stdio

# または専用コマンド
uv run claude-edit-mcp-stdio
```

### API エンドポイント

#### 文字列置換

```bash
curl -X POST http://localhost:8000/edit_file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.txt",
    "old_string": "古い文字列",
    "new_string": "新しい文字列"
  }'
```

#### ファイル書き込み

```bash
curl -X POST http://localhost:8000/write_file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.txt",
    "content": "ファイルの内容"
  }'
```

#### 行置換

```bash
curl -X POST http://localhost:8000/replace_line \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.txt",
    "line_number": 5,
    "new_line": "新しい行の内容"
  }'
```

## Claude Code MCP 統合

Claude Code で MCP として使用するには、設定ファイルを編集:

```json
{
  "mcpServers": {
    "claude-edit": {
      "command": "uv",
      "args": ["run", "claude-edit-mcp"],
      "env": {
        "CLAUDE_EDIT_HOST": "127.0.0.1",
        "CLAUDE_EDIT_PORT": "8000"
      }
    }
  }
}
```

## トラブルシューティング

### ファイルが見つからないエラー

- ファイルパスが正しいことを確認
- 親ディレクトリが存在することを確認

### エンコーディングエラー

- すべてのファイルは UTF-8 としてエンコードされます
- 異なるエンコーディングが必要な場合は機能を拡張してください

### ポート既に使用中

```bash
uv run claude-edit-mcp --port 8001
```

## 開発

### テスト実行

```bash
uv run pytest
```

### パッケージの更新

```bash
uv sync
```

## ライセンス

MIT
