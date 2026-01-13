import requests
from pprint import pprint
import os
from dotenv import load_dotenv
from upload_to_gcs import upload_to_gcs
from download_gcs_file import download_from_gcs

# 環境変数を読み込む
load_dotenv()

# 環境変数から設定を取得
RIOT_API_REGION_ASIA = os.getenv('RIOT_API_REGION_ASIA', 'asia')
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'lol-api-dev')
BASE_MATCH_URL = f"https://{RIOT_API_REGION_ASIA}.api.riotgames.com/lol/match/v5/matches/by-puuid"


def fetch_master_players_from_gcs(bucket_name: str, source_blob_name: str):
    """
    GCSからマスタープレイヤー情報を取得してpuuidのリストを返す
    
    Args:
        bucket_name: GCSバケット名
        source_blob_name: GCS上のファイルパス（例: "master_players/2026/01/13/master_players.json"）
    
    Returns:
        puuidのリスト
    """
    data = download_from_gcs(bucket_name, source_blob_name)
    
    if not data:
        print("データの取得に失敗しました")
        return []
    
    # entriesからpuuidを抽出
    puuids = []
    if 'entries' in data:
        for entry in data['entries']:
            if 'puuid' in entry:
                puuids.append(entry['puuid'])
    
    print(f"{len(puuids)}人のプレイヤーのpuuidを取得しました")
    return puuids
    


def get_match_ids(api_key: str, puuid: str):
    """マッチIDを取得する"""
    url = f"{BASE_MATCH_URL}/{puuid}/ids"
    headers = {
        'X-Riot-Token': api_key
    }
    response = requests.get(url, headers=headers)
    return response.json()


def upload_match_ids(api_key: str, puuid: str):
    """マッチIDをGCSにアップロードする"""
    match_ids = get_match_ids(api_key, puuid)
    upload_to_gcs(GCS_BUCKET_NAME, match_ids, f"match_ids/{puuid}/latest.json")


def main():
    api_key = os.getenv('RIOT_API_KEY')
    
    # GCSからマスタープレイヤーのpuuidを取得
    from datetime import datetime
    today = datetime.now().strftime("%Y/%m/%d")
    source_blob_name = f"master_players/{today}/master_players.json"
    
    puuids = fetch_master_players_from_gcs(GCS_BUCKET_NAME, source_blob_name)
    
    if not puuids:
        print("puuidの取得に失敗しました")
        return
    
    # 最初の5人のプレイヤーのマッチIDを取得（テスト用）
    for i, puuid in enumerate(puuids[:5]):
        print(f"\n--- プレイヤー {i+1}/{min(5, len(puuids))} ---")
        match_ids = get_match_ids(api_key, puuid)
        pprint(match_ids)
        
        # GCSにアップロード
        upload_match_ids(api_key, puuid)

if __name__ == "__main__":
    main()