#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GCSからBigQueryにデータをロードする
"""

from google.cloud import bigquery
from google.cloud import storage
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# 環境変数から設定を取得
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'lol-api-dev')
BQ_DATASET_ID = os.getenv('BQ_DATASET_ID', 'lol_api')
BQ_TABLE_ID = os.getenv('BQ_TABLE_ID', 'matches')
BQ_LOCATION = os.getenv('BQ_LOCATION', 'asia-northeast1')


def create_dataset_if_not_exists(client, dataset_id):
    """
    データセットが存在しない場合は作成する
    
    Args:
        client: BigQueryクライアント
        dataset_id: データセットID（例: "lol_api"）
    """
    try:
        client.get_dataset(dataset_id)
        print(f"データセット {dataset_id} は既に存在します")
    except:
        dataset = bigquery.Dataset(f"{client.project}.{dataset_id}")
        dataset.location = BQ_LOCATION  # 環境変数から取得
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"データセット {dataset_id} を作成しました")


def create_matches_table_schema():
    """
    試合データテーブルのスキーマを定義する
    """
    schema = [
        bigquery.SchemaField("match_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("game_creation", "TIMESTAMP"),
        bigquery.SchemaField("game_start_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("game_end_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("game_duration", "INTEGER"),
        bigquery.SchemaField("game_mode", "STRING"),
        bigquery.SchemaField("game_type", "STRING"),
        bigquery.SchemaField("game_version", "STRING"),
        bigquery.SchemaField("map_id", "INTEGER"),
        bigquery.SchemaField("queue_id", "INTEGER"),
        bigquery.SchemaField(
            "participants",
            "RECORD",
            mode="REPEATED",
            fields=[
                bigquery.SchemaField("puuid", "STRING"),
                bigquery.SchemaField("summoner_name", "STRING"),
                bigquery.SchemaField("summoner_id", "STRING"),
                bigquery.SchemaField("champion_name", "STRING"),
                bigquery.SchemaField("champion_id", "INTEGER"),
                bigquery.SchemaField("team_id", "INTEGER"),
                bigquery.SchemaField("team_position", "STRING"),
                bigquery.SchemaField("individual_position", "STRING"),
                bigquery.SchemaField("win", "BOOLEAN"),
                bigquery.SchemaField("kills", "INTEGER"),
                bigquery.SchemaField("deaths", "INTEGER"),
                bigquery.SchemaField("assists", "INTEGER"),
                bigquery.SchemaField("gold_earned", "INTEGER"),
                bigquery.SchemaField("total_damage_dealt", "INTEGER"),
                bigquery.SchemaField("total_damage_dealt_to_champions", "INTEGER"),
                bigquery.SchemaField("total_damage_taken", "INTEGER"),
                bigquery.SchemaField("damage_dealt_to_objectives", "INTEGER"),
                bigquery.SchemaField("damage_dealt_to_turrets", "INTEGER"),
                bigquery.SchemaField("champion_level", "INTEGER"),
                bigquery.SchemaField("minions_killed", "INTEGER"),
                bigquery.SchemaField("neutral_minions_killed", "INTEGER"),
                bigquery.SchemaField("vision_score", "INTEGER"),
                bigquery.SchemaField("wards_placed", "INTEGER"),
                bigquery.SchemaField("wards_killed", "INTEGER"),
                bigquery.SchemaField("first_blood_kill", "BOOLEAN"),
                bigquery.SchemaField("first_tower_kill", "BOOLEAN"),
                bigquery.SchemaField("double_kills", "INTEGER"),
                bigquery.SchemaField("triple_kills", "INTEGER"),
                bigquery.SchemaField("quadra_kills", "INTEGER"),
                bigquery.SchemaField("penta_kills", "INTEGER"),
            ],
        ),
        bigquery.SchemaField(
            "teams",
            "RECORD",
            mode="REPEATED",
            fields=[
                bigquery.SchemaField("team_id", "INTEGER"),
                bigquery.SchemaField("win", "BOOLEAN"),
                bigquery.SchemaField("baron_kills", "INTEGER"),
                bigquery.SchemaField("dragon_kills", "INTEGER"),
                bigquery.SchemaField("tower_kills", "INTEGER"),
                bigquery.SchemaField("inhibitor_kills", "INTEGER"),
                bigquery.SchemaField("rift_herald_kills", "INTEGER"),
                bigquery.SchemaField("first_baron", "BOOLEAN"),
                bigquery.SchemaField("first_dragon", "BOOLEAN"),
                bigquery.SchemaField("first_tower", "BOOLEAN"),
                bigquery.SchemaField("first_inhibitor", "BOOLEAN"),
                bigquery.SchemaField("first_rift_herald", "BOOLEAN"),
            ],
        ),
    ]
    return schema


def create_table_if_not_exists(client, dataset_id, table_id):
    """
    テーブルが存在しない場合は作成する
    
    Args:
        client: BigQueryクライアント
        dataset_id: データセットID
        table_id: テーブルID（例: "matches"）
    """
    full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    
    try:
        client.get_table(full_table_id)
        print(f"テーブル {full_table_id} は既に存在します")
    except:
        schema = create_matches_table_schema()
        table = bigquery.Table(full_table_id, schema=schema)
        
        # パーティショニング設定（日付で分割）
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="game_creation",
        )
        
        table = client.create_table(table)
        print(f"テーブル {full_table_id} を作成しました")


def transform_match_data(match_data):
    """
    APIレスポンスをBigQuery形式に変換する
    
    Args:
        match_data: Riot APIから取得した試合データ
    
    Returns:
        BigQuery用に変換されたデータ
    """
    metadata = match_data.get("metadata", {})
    info = match_data.get("info", {})
    
    # 基本情報
    transformed = {
        "match_id": metadata.get("matchId"),
        "game_creation": datetime.fromtimestamp(info.get("gameCreation", 0) / 1000).isoformat() if info.get("gameCreation") else None,
        "game_start_timestamp": datetime.fromtimestamp(info.get("gameStartTimestamp", 0) / 1000).isoformat() if info.get("gameStartTimestamp") else None,
        "game_end_timestamp": datetime.fromtimestamp(info.get("gameEndTimestamp", 0) / 1000).isoformat() if info.get("gameEndTimestamp") else None,
        "game_duration": info.get("gameDuration"),
        "game_mode": info.get("gameMode"),
        "game_type": info.get("gameType"),
        "game_version": info.get("gameVersion"),
        "map_id": info.get("mapId"),
        "queue_id": info.get("queueId"),
    }
    
    # 参加者情報
    participants = []
    for p in info.get("participants", []):
        participant = {
            "puuid": p.get("puuid"),
            "summoner_name": p.get("summonerName"),
            "summoner_id": p.get("summonerId"),
            "champion_name": p.get("championName"),
            "champion_id": p.get("championId"),
            "team_id": p.get("teamId"),
            "team_position": p.get("teamPosition"),
            "individual_position": p.get("individualPosition"),
            "win": p.get("win"),
            "kills": p.get("kills"),
            "deaths": p.get("deaths"),
            "assists": p.get("assists"),
            "gold_earned": p.get("goldEarned"),
            "total_damage_dealt": p.get("totalDamageDealt"),
            "total_damage_dealt_to_champions": p.get("totalDamageDealtToChampions"),
            "total_damage_taken": p.get("totalDamageTaken"),
            "damage_dealt_to_objectives": p.get("damageDealtToObjectives"),
            "damage_dealt_to_turrets": p.get("damageDealtToTurrets"),
            "champion_level": p.get("champLevel"),
            "minions_killed": p.get("totalMinionsKilled"),
            "neutral_minions_killed": p.get("neutralMinionsKilled"),
            "vision_score": p.get("visionScore"),
            "wards_placed": p.get("wardsPlaced"),
            "wards_killed": p.get("wardsKilled"),
            "first_blood_kill": p.get("firstBloodKill"),
            "first_tower_kill": p.get("firstTowerKill"),
            "double_kills": p.get("doubleKills"),
            "triple_kills": p.get("tripleKills"),
            "quadra_kills": p.get("quadraKills"),
            "penta_kills": p.get("pentaKills"),
        }
        participants.append(participant)
    
    transformed["participants"] = participants
    
    # チーム情報
    teams = []
    for t in info.get("teams", []):
        objectives = t.get("objectives", {})
        team = {
            "team_id": t.get("teamId"),
            "win": t.get("win"),
            "baron_kills": objectives.get("baron", {}).get("kills", 0),
            "dragon_kills": objectives.get("dragon", {}).get("kills", 0),
            "tower_kills": objectives.get("tower", {}).get("kills", 0),
            "inhibitor_kills": objectives.get("inhibitor", {}).get("kills", 0),
            "rift_herald_kills": objectives.get("riftHerald", {}).get("kills", 0),
            "first_baron": objectives.get("baron", {}).get("first", False),
            "first_dragon": objectives.get("dragon", {}).get("first", False),
            "first_tower": objectives.get("tower", {}).get("first", False),
            "first_inhibitor": objectives.get("inhibitor", {}).get("first", False),
            "first_rift_herald": objectives.get("riftHerald", {}).get("first", False),
        }
        teams.append(team)
    
    transformed["teams"] = teams
    
    return transformed


def get_existing_match_ids(bq_client, dataset_id, table_id):
    """
    BigQueryから既存のmatch_idのセットを取得する
    
    Args:
        bq_client: BigQueryクライアント
        dataset_id: データセットID
        table_id: テーブルID
    
    Returns:
        既存のmatch_idのセット
    """
    full_table_id = f"{bq_client.project}.{dataset_id}.{table_id}"
    
    try:
        query = f"""
            SELECT DISTINCT match_id
            FROM `{full_table_id}`
        """
        query_job = bq_client.query(query)
        results = query_job.result()
        
        existing_ids = {row.match_id for row in results}
        print(f"既存のmatch_id数: {len(existing_ids)}")
        return existing_ids
    except Exception as e:
        print(f"既存データの取得中にエラー: {e}")
        return set()


def load_gcs_to_bigquery(bucket_name, gcs_prefix, dataset_id, table_id):
    """
    GCSのJSONファイルをBigQueryにロードする（重複チェック付き）
    
    Args:
        bucket_name: GCSバケット名
        gcs_prefix: GCSのプレフィックス（例: "match_details/"）
        dataset_id: BigQueryデータセットID
        table_id: BigQueryテーブルID
    """
    bq_client = bigquery.Client()
    storage_client = storage.Client()
    
    # データセットとテーブルを作成（存在しない場合）
    create_dataset_if_not_exists(bq_client, dataset_id)
    create_table_if_not_exists(bq_client, dataset_id, table_id)
    
    # 既存のmatch_idを取得（重複チェック用）
    print("\n既存データをチェック中...")
    existing_match_ids = get_existing_match_ids(bq_client, dataset_id, table_id)
    
    # GCSからファイル一覧を取得
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=gcs_prefix))
    
    print(f"\n{len(blobs)}個のファイルを処理します...")
    
    # データを変換してBigQueryに挿入
    full_table_id = f"{bq_client.project}.{dataset_id}.{table_id}"
    table = bq_client.get_table(full_table_id)
    
    rows_to_insert = []
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, blob in enumerate(blobs, 1):
        if not blob.name.endswith('.json'):
            continue
            
        print(f"処理中 [{i}/{len(blobs)}]: {blob.name}")
        
        try:
            # GCSからJSONを読み込み
            import json
            content = blob.download_as_string()
            match_data = json.loads(content)
            
            # match_idを取得
            match_id = match_data.get("metadata", {}).get("matchId")
            
            # 重複チェック
            if match_id in existing_match_ids:
                print(f"  → スキップ（既に存在）: {match_id}")
                skipped_count += 1
                continue
            
            # データを変換
            transformed_data = transform_match_data(match_data)
            rows_to_insert.append(transformed_data)
            
            # 既存のセットに追加（同じ実行中の重複も防ぐ）
            existing_match_ids.add(match_id)
            
            # 100件ごとにバッチ挿入
            if len(rows_to_insert) >= 100:
                errors = bq_client.insert_rows_json(table, rows_to_insert)
                if errors:
                    print(f"エラー: {errors}")
                    error_count += len(errors)
                else:
                    success_count += len(rows_to_insert)
                    print(f"  → {len(rows_to_insert)}件を挿入しました")
                rows_to_insert = []
                
        except Exception as e:
            print(f"エラー: {blob.name} の処理に失敗しました - {e}")
            error_count += 1
    
    # 残りのデータを挿入
    if rows_to_insert:
        errors = bq_client.insert_rows_json(table, rows_to_insert)
        if errors:
            print(f"エラー: {errors}")
            error_count += len(errors)
        else:
            success_count += len(rows_to_insert)
            print(f"  → {len(rows_to_insert)}件を挿入しました")
    
    print(f"\n完了: {success_count}件挿入, {skipped_count}件スキップ, {error_count}件失敗")


def main():
    """メイン関数"""
    gcs_prefix = "match_details/"
    
    print("GCSからBigQueryへのデータロードを開始します...")
    load_gcs_to_bigquery(GCS_BUCKET_NAME, gcs_prefix, BQ_DATASET_ID, BQ_TABLE_ID)
    
    print("\nクエリ例:")
    print(f"SELECT match_id, game_mode, game_duration FROM `{BQ_DATASET_ID}.{BQ_TABLE_ID}` LIMIT 10")


if __name__ == "__main__":
    main()
