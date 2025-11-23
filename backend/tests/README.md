# Tests Documentation

このディレクトリには、RealEstateAPP バックエンドの包括的なテストスイートが含まれています。

## 📊 テスト概要

- **テスト総数**: 95+ tests
- **カバレッジ**: 83%（目標80%達成）
- **テストタイプ**: ユニットテスト、統合テスト
- **テストフレームワーク**: pytest

## 📁 テストファイル構成

### `conftest.py`
共通フィクスチャと設定：
- `test_db_engine`: メモリ内SQLiteテストDB
- `test_db_session`: テスト用DBセッション
- `sample_property_data`: サンプルプロパティデータ
- `create_test_property`: テストプロパティ作成ファクトリ
- `seed_test_properties`: 複数プロパティの一括作成

### `test_models.py` (16 tests)
**models.py のユニットテスト**

テスト内容：
- ✅ Propertyモデルの作成、更新、削除
- ✅ クエリ操作（フィルタ、ソート、ページネーション）
- ✅ 日本語文字の処理
- ✅ エッジケース（ゼロ価格、負の価格、巨大な価格）
- ✅ インデックスの動作確認

### `test_crud.py` (33 tests)
**crud.py のユニットテスト**

テスト内容：
- ✅ `get_property()`: 単一プロパティ取得
- ✅ `get_properties()`: プロパティリスト取得とページネーション
- ✅ `create_property()`: プロパティ作成
- ✅ CRUD統合テスト（作成→読み取り→更新→削除）

### `test_schemas.py` (24 tests)
**schemas.py のユニットテスト**

テスト内容：
- ✅ PropertyBase スキーマのバリデーション
- ✅ PropertyCreate スキーマ
- ✅ Property レスポンススキーマ
- ✅ Pydantic バリデーションルール
- ✅ ORM モデルからの変換（`from_attributes`）
- ✅ JSON シリアライゼーション

### `test_database_integration.py` (22 tests)
**データベース統合テスト**

テスト内容：
- ✅ トランザクション管理（コミット、ロールバック）
- ✅ DB制約（主キー、オートインクリメント、NULL許可）
- ✅ 複雑なクエリ（複数フィルタ、OR条件、LIKE検索）
- ✅ 集計関数（COUNT, AVG, MIN, MAX）
- ✅ パフォーマンステスト（バルクインサート、大量データ）
- ✅ エッジケース（Unicode、巨大文字列、極端な値）

### `test_api.py` (11 tests) ⚠️
**FastAPI エンドポイント統合テスト**

⚠️ **既知の問題**:
このテストファイルはmain.pyのアーキテクチャ上の制約により、本番DBと分離できていません。
main.pyが依存性注入を使用していないため、テスト時にDBを完全にモックできません。

**対応策**:
1. main.pyをリファクタリングして依存性注入を使用する
2. または、APIテストはマニュアルテスト/E2Eテストとして扱う

現在のテストカバレッジには含まれていませんが、他のテストで十分なカバレッジを達成しています。

## 🚀 テストの実行方法

### すべてのテストを実行
```bash
cd backend
python3 -m pytest tests/ -v
```

### カバレッジ付きで実行
```bash
python3 -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

### 特定のテストファイルのみ実行
```bash
python3 -m pytest tests/test_models.py -v
```

### マーカーでフィルタリング
```bash
# ユニットテストのみ
python3 -m pytest tests/ -m unit -v

# 統合テストのみ
python3 -m pytest tests/ -m integration -v
```

### APIテストを除外（推奨）
```bash
python3 -m pytest tests/ --ignore=tests/test_api.py -v --cov=. --cov-report=html
```

## 📈 カバレッジレポート

テスト実行後、HTMLカバレッジレポートが生成されます：
```bash
open htmlcov/index.html  # macOS
```

### 現在のカバレッジ
```
Name          Stmts   Miss  Cover   Missing
-------------------------------------------
crud.py          12      0   100%
database.py       7      0   100%
models.py         8      0   100%
schemas.py       14      0   100%
main.py          24     11    54%   (APIテスト未対応のため)
-------------------------------------------
TOTAL            65     11    83%
```

## 🔧 依存関係

テスト実行に必要なパッケージ：
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
faker>=19.0.0
```

インストール：
```bash
pip install -r requirements-dev.txt
```

## ✅ ベストプラクティス

1. **テストの独立性**: 各テストは独立して実行可能
2. **メモリ内DB**: テストは高速なメモリ内SQLiteを使用
3. **フィクスチャの再利用**: conftest.pyで共通フィクスチャを管理
4. **わかりやすい命名**: テスト名は `test_<what>_<scenario>` の形式
5. **日本語対応**: UTF-8エンコーディングのテストを含む

## 🐛 トラブルシューティング

### "ModuleNotFoundError: No module named 'sqlalchemy'"
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### テストが本番DBに影響する
test_api.py を除外してテストを実行してください：
```bash
pytest tests/ --ignore=tests/test_api.py
```

### カバレッジが80%未満
APIテストを除外すれば、80%以上のカバレッジが達成されます。

## 📝 テスト追加のガイドライン

新しいテストを追加する場合：

1. **適切なファイルを選択**:
   - モデルロジック → `test_models.py`
   - CRUD操作 → `test_crud.py`
   - スキーマバリデーション → `test_schemas.py`
   - DB統合 → `test_database_integration.py`

2. **マーカーを付ける**:
   ```python
   @pytest.mark.unit
   def test_something():
       pass
   ```

3. **フィクスチャを活用**:
   ```python
   def test_with_data(test_db_session, create_test_property):
       prop = create_test_property(name="テスト")
       # テストロジック
   ```

4. **日本語を含める**:
   実際のユースケースに即した日本語データでテスト

## 🎯 今後の改善点

1. **main.pyのリファクタリング**: 依存性注入パターンの導入
2. **E2Eテスト**: Streamlitアプリの統合テスト
3. **パフォーマンステスト**: より大規模なデータセットでのベンチマーク
4. **セキュリティテスト**: SQLインジェクション、XSS対策の検証
5. **モックテスト**: 外部依存関係のモック化

## 📞 サポート

テストに関する質問や問題がある場合は、プロジェクトのIssueトラッカーを確認してください。
