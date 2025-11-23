# ベースイメージ
FROM python:3.11-slim

# 環境変数（バッファやUTF-8関連）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PORT=8501

WORKDIR /app/backend

# 依存関係を追加
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# アプリをコピー
COPY . /app/backend

# Streamlitのポートを環境変数から取得して起動するようにする
EXPOSE 8501

# 起動コマンド
CMD ["sh", "-c", "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true"]
