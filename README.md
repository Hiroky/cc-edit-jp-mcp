# Claude Edit MCP

FastMCP を使用した日本語対応ファイル編集MCP サーバー。

Tabインデントをベースとしたコードベースの場合にClaudeCodeの標準編集ツールがエラー(Error editing file)となる対策のためのMCPです。

## 特徴

- **UTF-8 対応**: 日本語を含むテキストファイルを正しく処理
- **暗黙的なインデント変換**: タブとスペース（4スペース）を自動変換
  - 読み込み時にタブを4スペースに変換
  - 編集時に4スペースをタブに変換して保存
- **HTTP インターフェース**: HTTP経由でアクセス可能
- **MCP プロトコル対応**: Claude と統合可能
- **複数の編集機能**:
  - ファイル読み込み (`read_file`) - タブは4スペースに変換
  - 文字列置換 (`edit_file`) - 自動インデント変換
  - ファイル書き込み (`write_file`) - スペースをタブに変換
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

#### ファイル読み込み

```bash
curl -X POST http://localhost:8000/read_file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.py"
  }'
```

**行番号と行数での範囲指定も可能**:

```bash
# 10行目から20行分を読み込む
curl -X POST http://localhost:8000/read_file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.py",
    "start_line": 10,
    "num_lines": 20
  }'
```

**注**: タブはすべて4スペースに自動変換されます。レスポンスにはメタデータ（`total_lines`, `start_line`, `end_line`, `num_lines_read`）も含まれます。

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

**注**: `old_string`と`new_string`は4スペースを使用してください。タブは自動的に4スペースに変換されて検索されます。

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

### インデント変換に関する質問

- 詳細は [INDENT_CONVERSION_GUIDE.md](docs/INDENT_CONVERSION_GUIDE.md) を参照してください
- ファイルはタブで保存されます
- すべてのAPI呼び出しでは4スペースを使用してください

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
