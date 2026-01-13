#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GCSにファイルをアップロードする関数
"""

from google.cloud import storage
from dotenv import load_dotenv
import json

load_dotenv()

def upload_to_gcs(bucket_name, data, destination_blob_name):
    """GCSにファイルをアップロードする"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    if blob.exists():
        print(f"File {destination_blob_name} already exists in {bucket_name}.")
        return

    blob.upload_from_string(json.dumps(data, indent=4, ensure_ascii=False), content_type='application/json')
    print(f"File {destination_blob_name} uploaded to {bucket_name}.")


def main():
    # 環境変数から設定を取得
    import os
    bucket_name = os.getenv('GCS_BUCKET_NAME', 'lol-api-dev')
    
    data = {
        "id": 2,
        "name": "test_data",
        "status": "success"
    }
    upload_to_gcs(bucket_name, data, "folder/data.json")

if __name__ == "__main__":
    main()