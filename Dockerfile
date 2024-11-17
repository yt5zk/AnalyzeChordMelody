# Dockerfile

# 公式のEssentia Dockerイメージをベースに使用
FROM mtgupf/essentia:latest

# 作業ディレクトリの設定
WORKDIR /app

# 必要なシステムパッケージのインストール（pipを含む）
RUN apt-get update && \
    apt-get install -y build-essential ffmpeg python3-pip && \
    rm -rf /var/lib/apt/lists/*

# requirements.txtをコンテナにコピー
COPY requirements.txt .

# pipをアップグレード
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Pythonライブラリのインストール（PyYAMLを上書き）
RUN python3 -m pip install --no-cache-dir -r requirements.txt --ignore-installed PyYAML

# アプリケーションコードのコピー
COPY . /app

# デフォルトのコマンド設定（docker-compose.ymlで上書き）
CMD ["python3", "main.py", "/data"]