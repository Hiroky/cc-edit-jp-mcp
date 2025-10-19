# インデント変換機能ガイド

## 概要

Claude Edit MCP は、ファイル操作時に**暗黙的なインデント変換**を行います。これにより、使用者がタブとスペースを明確に区別する必要がなくなります。

## 変換ルール

### 読み込み時（`read_file`）

ファイルから読み込む際、**タブはすべて4スペースに変換**されます。

```
入力（ファイル内容）：
def hello():
→tabprint('world')

出力（read_fileの戻り値）：
def hello():
    print('world')
```

これにより、タブ文字に対応していないクライアント側でもインデントを正しく認識できます。

### 編集時（`edit_file`）

置換操作時に以下のプロセスが実行されます：

1. ファイルの内容を読み込む
2. **タブを4スペースに正規化**する
3. 提供された`old_string`と`new_string`（4スペース使用）で置換を実行
4. **4スペースをタブに変換**して書き込む

```
ファイル内容（タブ使用）：
def func():
→tab→tabprint('nested')

正規化（内部処理）：
def func():
        print('nested')

置換後（タブに変換して保存）：
def func():
→tab→tabprint('modified')
```

### 書き込み時（`write_file`）

ファイルに書き込む際：

1. 入力内容（4スペース使用）を受け取る
2. **4スペースをタブに変換**
3. タブを使用した状態でファイルに保存

```
入力：
def hello():
    print('world')

出力（ファイルに保存）：
def hello():
→tabprint('world')
```

## 利点

1. **クライアント側は常に4スペースを使用**
   - タブ文字を明示的に処理する必要がない
   - コードは読みやすい統一形式

2. **サーバー側でタブを維持**
   - 既存のタブインデント形式のファイルを保護
   - ファイルシステムの一貫性を保証

3. **相互運用性の向上**
   - エディタ、言語、OSの違いに関わらず動作

## 実装詳細

### `indent_converter.py`

#### `tabs_to_spaces(content: str, spaces: int = 4) -> str`

タブをスペースに変換します。

```python
content = "def hello():\n\tprint('world')"
result = tabs_to_spaces(content)
# 結果: "def hello():\n    print('world')"
```

#### `spaces_to_tabs(content: str, spaces: int = 4) -> str`

連続するスペースをタブに変換します（行の先頭のみ）。

```python
content = "def hello():\n    print('world')"
result = spaces_to_tabs(content)
# 結果: "def hello():\n\tprint('world')"
```

**注意**: 行の先頭以外のスペースは変換されません。

```python
content = "x = 'hello    world'"
result = spaces_to_tabs(content)
# 結果: "x = 'hello    world'"  # 変わらない
```

## 使用例

### API経由での使用

```bash
# ファイルの読み込み（タブは4スペースに変換されて返される）
curl -X POST http://localhost:8000/read_file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.py"
  }'

# レスポンス例（タブが4スペースに変換されている）
{
  "success": true,
  "content": "def hello():\n    print('world')",
  "file_path": "/path/to/file.py"
}
```

### 置換の例

```bash
# 入力は4スペースを使用
curl -X POST http://localhost:8000/edit_file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.py",
    "old_string": "def hello():\n    print('world')",
    "new_string": "def hello():\n    print('modified')"
  }'

# ファイルには自動的にタブが保存される
```

## トラブルシューティング

### 置換が見つからない場合

ファイルがタブを使用している場合、`old_string`は**4スペース**で指定してください：

```python
# ❌ 間違い（タブを直接指定）
old_string = "def func():\n\tprint()"

# ✓ 正しい（4スペースを指定）
old_string = "def func():\n    print()"
```

### テスト

ユーティリティ関数のテストを実行：

```bash
uv run pytest tests/test_indent_converter.py -v
```

## 設定

デフォルトでは4スペース1タブとして処理されます。別の値に変更する場合は、`indent_converter.py`内の関数呼び出しを修正してください：

```python
# 2スペース1タブに変更する場合
content_normalized = tabs_to_spaces(content, spaces=2)
new_content = spaces_to_tabs(new_content_normalized, spaces=2)
```

## 仕様書

### 変換対象

- **読み込み**: ファイル内のすべてのタブ文字
- **書き込み**: 行の先頭の4スペースの連続（4の倍数のみ）

### 非対象

- **行の途中のスペース**: 保持される
- **文字列内のスペース**: 保持される
- **不完全なインデント**: スペースが4の倍数でない場合は変換されない
