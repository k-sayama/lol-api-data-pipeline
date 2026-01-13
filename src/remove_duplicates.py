#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BigQueryから重複データを削除する
"""

from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()

# 環境変数から設定を取得
BQ_DATASET_ID = os.getenv('BQ_DATASET_ID', 'lol_api')
BQ_TABLE_ID = os.getenv('BQ_TABLE_ID', 'matches')


def check_duplicates(client, dataset_id, table_id):
    """
    重複データの数を確認する
    
    Args:
        client: BigQueryクライアント
        dataset_id: データセットID
        table_id: テーブルID
    
    Returns:
        重複数
    """
    full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    
    query = f"""
        SELECT 
            match_id,
            COUNT(*) as count
        FROM `{full_table_id}`
        GROUP BY match_id
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """
    
    print("重複データを確認中...")
    query_job = client.query(query)
    results = list(query_job.result())
    
    if results:
        print(f"\n重複が見つかりました: {len(results)}件のmatch_idが重複しています")
        print("\n例（最初の5件）:")
        for i, row in enumerate(results[:5], 1):
            print(f"  {i}. match_id: {row.match_id}, 重複数: {row.count}")
        
        total_duplicates = sum(row.count - 1 for row in results)
        print(f"\n削除対象の重複レコード数: {total_duplicates}件")
        return len(results), total_duplicates
    else:
        print("重複データは見つかりませんでした")
        return 0, 0


def remove_duplicates(client, dataset_id, table_id):
    """
    重複データを削除する（match_idが重複している場合、最新のものを残す）
    
    Args:
        client: BigQueryクライアント
        dataset_id: データセットID
        table_id: テーブルID
    """
    full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    temp_table_id = f"{full_table_id}_temp"
    
    # 重複を除外したデータで一時テーブルを作成
    query = f"""
        CREATE OR REPLACE TABLE `{temp_table_id}` AS
        SELECT * FROM (
            SELECT 
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY match_id 
                    ORDER BY game_creation DESC
                ) as row_num
            FROM `{full_table_id}`
        )
        WHERE row_num = 1
    """
    
    print(f"\n重複を除外した一時テーブルを作成中...")
    query_job = client.query(query)
    query_job.result()
    print("一時テーブル作成完了")
    
    # 元のテーブルを削除
    print(f"\n元のテーブルを削除中...")
    client.delete_table(full_table_id)
    print("削除完了")
    
    # 一時テーブルを元のテーブル名にコピー
    print(f"\n一時テーブルを元のテーブル名にコピー中...")
    copy_query = f"""
        CREATE OR REPLACE TABLE `{full_table_id}` AS
        SELECT * EXCEPT(row_num) FROM `{temp_table_id}`
    """
    query_job = client.query(copy_query)
    query_job.result()
    print("コピー完了")
    
    # 一時テーブルを削除
    print(f"\n一時テーブルを削除中...")
    client.delete_table(temp_table_id)
    print("削除完了")
    
    # パーティショニングを再設定
    print(f"\nパーティショニングを再設定中...")
    alter_query = f"""
        ALTER TABLE `{full_table_id}`
        SET OPTIONS (
            partition_expiration_days = NULL
        )
    """
    try:
        query_job = client.query(alter_query)
        query_job.result()
        print("パーティショニング設定完了")
    except Exception as e:
        print(f"パーティショニング設定のエラー（無視しても問題ありません）: {e}")


def verify_removal(client, dataset_id, table_id):
    """
    重複が削除されたことを確認する
    
    Args:
        client: BigQueryクライアント
        dataset_id: データセットID
        table_id: テーブルID
    """
    full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    
    # 総レコード数を確認
    count_query = f"""
        SELECT COUNT(*) as total_count
        FROM `{full_table_id}`
    """
    
    query_job = client.query(count_query)
    result = list(query_job.result())[0]
    
    print(f"\n削除後のレコード数: {result.total_count}件")
    
    # 重複チェック
    check_duplicates(client, dataset_id, table_id)


def main():
    """メイン関数"""
    client = bigquery.Client()
    
    print("=" * 60)
    print("BigQuery 重複データ削除ツール")
    print("=" * 60)
    
    # 重複をチェック
    duplicate_match_count, total_duplicates = check_duplicates(client, BQ_DATASET_ID, BQ_TABLE_ID)
    
    if duplicate_match_count == 0:
        print("\n処理を終了します")
        return
    
    # 確認
    print("\n" + "=" * 60)
    response = input(f"重複データを削除しますか？ (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\n重複削除を開始します...")
        remove_duplicates(client, BQ_DATASET_ID, BQ_TABLE_ID)
        
        # 削除後の確認
        print("\n" + "=" * 60)
        print("削除後の確認:")
        verify_removal(client, BQ_DATASET_ID, BQ_TABLE_ID)
        
        print("\n" + "=" * 60)
        print("重複削除が完了しました！")
        print("=" * 60)
    else:
        print("\n処理をキャンセルしました")


if __name__ == "__main__":
    main()
