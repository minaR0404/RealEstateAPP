# RealEstateAPP
This app returns the average property price in Tokyo.

# 🏠 RealEstateAPP（不動産価格検索アプリ）

このアプリは、SQLite データベースに保存された**令和7年度の関東圏の不動産平均価格情報** を  
簡単に検索・閲覧できる Streamlit Web アプリケーションです。  
参考情報は以下の通りです。
[令和7年都道府県地価調査](https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/tochi_fudousan_kensetsugyo_fr4_000001_00318.html)

<img src="./assets/AppImage.png" alt="アプリ画面" width="500">

---

## 🚀 機能概要

- 不動産データ（都道府県名・市区名・平均価格など）を表示
- サイドバーで物件名・価格帯で検索
- SQLiteデータベース（`realestate_sample.db`）を自動読み込み
- AWS / Docker / CI/CD 対応可能

---

## 🗂️ ディレクトリ構成

<pre>
realestate_app/
├── backend/
│   ├── main.py              # FastAPIメインAPI
│   ├── app.py               # Stramlitメインアプリ
│   ├── models.py            # SQLAlchemyモデル定義
│   ├── database.py          # DB接続設定
│   ├── crud.py              # データ操作ロジック
│   ├── schemas.py           # Pydanticスキーマ
│   ├── init_db.py           # 数行のDB初期設定
│   ├── excel_sample.py      # 不動産情報のDB設定
│   └── requirements.txt     # 依存ライブラリ
├── data/
│   └── realestate_sample.db # SQLiteデータベース
└── assets/
    └── 001908994.xlsx       # 令和7年度関東圏地価情報
</pre>

---

## ⚙️ セットアップ方法

### ① 仮想環境の作成（ローカル開発の場合）

```bash
git clone https://github.com/yourname/realestate-app.git
cd realestate-app

python -m venv venv
source venv/bin/activate  # (Windowsは venv\Scripts\activate)

pip install -r requirements.txt
```

### ② アプリの起動
```bash
streamlit run app.py
```
アプリが自動でブラウザに開きます。
または手動で以下にアクセスしてください：
👉 [http://localhost:8501](http://localhost:8501)

### 🗃️ データベース追加（例：Excelから生成）
もしデータがExcel形式（例：sample.xlsx）の場合は、
以下のPythonコードで realestate_sample.db を追加できます：

```python
import pandas as pd
import sqlite3

file_path = "001908994.xlsx"
df = pd.read_excel(file_path, sheet_name=None)

# すべてのシートを結合して1つのDataFrameに
columns = ['都道府県名', '市区名', '基準地数', '平均価格', '最上位の価格', '最下位の価格']
df_all = pd.concat([pd.DataFrame(sheet.values, columns=columns) for sheet in df.values()])

# DBに書き込み
conn = sqlite3.connect("realestate_sample.db")
df_all.to_sql("properties", conn, if_exists="replace", index=False)
conn.close()
```

---

## 🧠 使用技術
| 分類 | 使用技術 |
|------|-----------|
| フロントエンド | Streamlit |
| バックエンド | FastAPI |
| データベース | SQLite3 |
| 環境構築 | Python venv / Docker（任意） |

---

## 🧑‍💻 著者情報

| 項目 | 内容 |
|------|------|
| **Author** | minaR0404 |
| **GitHub** | [https://github.com/minaR0404](https://github.com/minaR0404) |

## 📜 ライセンス

**MIT License**  
© 2025 minaR0404