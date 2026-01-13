#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GCSからファイルをダウンロードする関数
"""

from google.cloud import storage
from dotenv import load_dotenv
import json
import os

load_dotenv()

def download_from_gcs(bucket_name, source_blob_name, destination_file_name=None):
    """
    GCSからファイルをダウンロードする
    
    Args:
        bucket_name: GCSバケット名
        source_blob_name: GCS上のファイルパス
        destination_file_name: ローカルに保存する場合のファイルパス（Noneの場合はJSONデータとして返す）
    
    Returns:
        destination_file_nameがNoneの場合はJSON形式のデータを返す
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    if not blob.exists():
        print(f"File {source_blob_name} does not exist in {bucket_name}.")
        return None

    if destination_file_name:
        # ローカルファイルとしてダウンロード
        blob.download_to_filename(destination_file_name)
        print(f"File {source_blob_name} downloaded to {destination_file_name}.")
    else:
        # 文字列として取得してJSONとしてパース
        content = blob.download_as_string()
        data = json.loads(content)
        print(f"File {source_blob_name} downloaded from {bucket_name}.")
        return data


def main():
    # 環境変数から設定を取得
    bucket_name = os.getenv('GCS_BUCKET_NAME', 'lol-api-dev')
    
    # 例1: ファイルとしてダウンロード
    download_from_gcs(bucket_name, "folder/data.json", "downloaded_data.json")
    
    # 例2: JSONデータとして取得
    data = download_from_gcs(bucket_name, "folder/data.json")
    if data:
        print("Downloaded data:", data)


if __name__ == "__main__":
    main()
