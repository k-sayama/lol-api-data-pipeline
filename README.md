# League of Legends API プロジェクト

このプロジェクトは、Riot Games の League of Legends API を使用するための Python プロジェクトです。

## セットアップ

### 1. 仮想環境の作成

```bash
python3 -m venv venv
```

### 2. 仮想環境の有効化

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`env.example` をコピーして `.env` ファイルを作成:

```bash
cp env.example .env
```

`.env` ファイルを編集して、以下を設定:

```bash
# Riot Games API設定
RIOT_API_KEY=your_api_key_here

# Google Cloud Platform設定
GCS_BUCKET_NAME=lol-api-dev
GCP_PROJECT_ID=your_project_id_here

# BigQuery設定
BQ_DATASET_ID=lol_api
BQ_TABLE_ID=matches
BQ_LOCATION=asia-northeast1

# Riot API エンドポイント（デフォルト値が設定されているため変更不要）
RIOT_API_REGION_JP=jp1
RIOT_API_REGION_ASIA=asia

# テスト用設定（オプション）
TEST_PUUID=your_test_puuid_here
TEST_MATCH_LIMIT=3

# GCP 認証（サービスアカウントキーのパス）
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

**必須の環境変数:**
- `RIOT_API_KEY`: Riot Games の API キー
- `GCS_BUCKET_NAME`: GCS バケット名
- `GCP_PROJECT_ID`: GCP プロジェクトID
- `GOOGLE_APPLICATION_CREDENTIALS`: GCP サービスアカウントキーのパス

**オプションの環境変数:**
- `BQ_DATASET_ID`: BigQuery データセットID（デフォルト: `lol_api`）
- `BQ_TABLE_ID`: BigQuery テーブルID（デフォルト: `matches`）
- `BQ_LOCATION`: BigQuery ロケーション（デフォルト: `asia-northeast1`）
- `RIOT_API_REGION_JP`: Riot API 日本リージョン（デフォルト: `jp1`）
- `RIOT_API_REGION_ASIA`: Riot API アジアリージョン（デフォルト: `asia`）
- `TEST_PUUID`: テスト用プレイヤー PUUID
- `TEST_MATCH_LIMIT`: テスト時の取得マッチ数上限（デフォルト: `3`）

### 5. プログラムの実行

```bash
python src/main.py
```

## GCP への保存（オプション）

取得したデータを GCP (Google Cloud Platform) に保存できます。

### 対応ストレージ

- **Cloud Storage**: JSON ファイルとして保存
- **BigQuery**: 構造化データとして保存（分析に最適）

### セットアップ方法

詳細は [GCP_SETUP.md](GCP_SETUP.md) を参照してください。

簡易セットアップ：

1. GCP プロジェクトを作成
2. Cloud Storage バケットを作成
3. BigQuery データセットを作成
4. サービスアカウントを作成して権限を付与
5. `.env` ファイルに GCP 設定を追加
6. `SAVE_TO_GCS=true` または `SAVE_TO_BIGQUERY=true` に設定

### 実行例

```bash
# Cloud Storage に保存
SAVE_TO_GCS=true python src/main.py

# BigQuery に保存
SAVE_TO_BIGQUERY=true python src/main.py

# 両方に保存
SAVE_TO_GCS=true SAVE_TO_BIGQUERY=true python src/main.py
```

## Riot API キーの取得方法

1. [Riot Developer Portal](https://developer.riotgames.com/) にアクセス
2. Riot アカウントでログイン
3. Development API Key を取得
4. `.env` ファイルに API キーを設定

## プロジェクト構造

```
lol_api/
├── src/
│   ├── main.py              # メインプログラム
│   ├── match_id.py          # マッチID取得
│   ├── match_history.py     # マッチ履歴取得
│   ├── gcp_storage.py       # Cloud Storage 連携
│   └── gcp_bigquery.py      # BigQuery 連携
├── requirements.txt         # Python 依存関係
├── .env                     # 環境変数（Git管理外）
├── .gitignore               # Git除外設定
├── README.md                # このファイル
└── GCP_SETUP.md             # GCP セットアップガイド
```

## 使用するライブラリ

- **requests**: HTTP リクエスト用
- **python-dotenv**: 環境変数管理
- **pandas**: データ処理
- **flask**: Web API 構築（オプション）
- **pytest**: テスト用
- **google-cloud-storage**: Cloud Storage 連携（オプション）
- **google-cloud-bigquery**: BigQuery 連携（オプション）

## 機能

### データ取得
- ✅ マスターリーグランキング取得
- ✅ マッチID取得
- ✅ マッチ履歴取得

### データ保存
- ✅ Cloud Storage（JSON）
- ✅ BigQuery（構造化データ）
- ⏳ ローカルファイル保存（予定）

### データ分析
- ⏳ ランキング分析（予定）
- ⏳ 勝率分析（予定）
- ⏳ チャンピオン統計（予定）

## ライセンス

MIT

