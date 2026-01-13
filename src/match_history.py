import requests
from pprint import pprint
import os
from dotenv import load_dotenv
from download_gcs_file import download_from_gcs
from upload_to_gcs import upload_to_gcs
import time

# 環境変数を読み込む
load_dotenv()

# 環境変数から設定を取得
RIOT_API_REGION_ASIA = os.getenv('RIOT_API_REGION_ASIA', 'asia')
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'lol-api-dev')
BASE_MATCH_URL = f"https://{RIOT_API_REGION_ASIA}.api.riotgames.com/lol/match/v5/matches"

def get_match_detail(api_key: str, match_id: str):
    """試合詳細を取得する"""
    url = f"{BASE_MATCH_URL}/{match_id}"
    headers = {
        'X-Riot-Token': api_key
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"エラー: {match_id} の取得に失敗しました (status: {response.status_code})")
        return None


def fetch_match_ids_from_gcs(bucket_name: str, puuid: str):
    """
    GCSから特定のプレイヤーのマッチIDリストを取得する
    
    Args:
        bucket_name: GCSバケット名
        puuid: プレイヤーのPUUID
    
    Returns:
        マッチIDのリスト
    """
    source_blob_name = f"match_ids/{puuid}/latest.json"
    match_ids = download_from_gcs(bucket_name, source_blob_name)
    
    if not match_ids:
        print(f"マッチIDの取得に失敗しました: {puuid}")
        return []
    
    print(f"{len(match_ids)}件のマッチIDを取得しました")
    return match_ids


def save_match_detail(bucket_name: str, match_id: str, match_detail: dict):
    """
    試合詳細をGCSに保存する
    
    Args:
        bucket_name: GCSバケット名
        match_id: マッチID
        match_detail: 試合詳細データ
    """
    destination_blob_name = f"match_details/{match_id}.json"
    upload_to_gcs(bucket_name, match_detail, destination_blob_name)


def process_match_details(api_key: str, bucket_name: str, puuid: str, limit: int = None):
    """
    プレイヤーの全マッチIDに対して試合詳細を取得してGCSに保存する
    
    Args:
        api_key: Riot API キー
        bucket_name: GCSバケット名
        puuid: プレイヤーのPUUID
        limit: 処理するマッチ数の上限（Noneの場合は全て処理）
    """
    # GCSからマッチIDリストを取得
    match_ids = fetch_match_ids_from_gcs(bucket_name, puuid)
    
    if not match_ids:
        return
    
    # 処理するマッチ数を制限
    if limit:
        match_ids = match_ids[:limit]
        print(f"最初の{limit}件のマッチを処理します")
    
    # 各マッチの詳細を取得して保存
    success_count = 0
    for i, match_id in enumerate(match_ids, 1):
        print(f"\n処理中 [{i}/{len(match_ids)}]: {match_id}")
        
        # 試合詳細を取得
        match_detail = get_match_detail(api_key, match_id)
        
        if match_detail:
            # GCSに保存
            save_match_detail(bucket_name, match_id, match_detail)
            success_count += 1
        
        # API制限を考慮して待機（Riot APIは20リクエスト/秒、100リクエスト/2分）
        if i < len(match_ids):
            time.sleep(1.2)  # 安全のため1.2秒待機
    
    print(f"\n完了: {success_count}/{len(match_ids)} 件の試合詳細を保存しました")


def main():
    api_key = os.getenv('RIOT_API_KEY')
    
    # テスト: 特定のPUUIDのマッチ詳細を取得
    # TEST_PUUIDを環境変数に設定してください
    test_puuid = os.getenv('TEST_PUUID')
    if not test_puuid:
        print("エラー: TEST_PUUID環境変数が設定されていません")
        print(".envファイルにTEST_PUUID=your_puuid_hereを追加してください")
        return
    
    test_limit = int(os.getenv('TEST_MATCH_LIMIT', '3'))
    
    process_match_details(api_key, GCS_BUCKET_NAME, test_puuid, limit=test_limit)

if __name__ == "__main__":
    main()