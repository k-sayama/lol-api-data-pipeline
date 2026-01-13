#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
League of Legends API メインファイル
"""

import os
from dotenv import load_dotenv
import requests
from pprint import pprint

# 環境変数を読み込む
load_dotenv()

# 環境変数から設定を取得
RIOT_API_REGION_JP = os.getenv('RIOT_API_REGION_JP', 'jp1')
MASTER_LEAGUE_URL = f"https://{RIOT_API_REGION_JP}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5"

def get_master_league(api_key: str):
    """マスターリーグを取得する"""
    headers = {
        'X-Riot-Token': api_key
    }
    response = requests.get(MASTER_LEAGUE_URL, headers=headers)

    return response.json()


def main():
    """メイン関数"""
    api_key = os.getenv('RIOT_API_KEY')
    if not api_key:
        print("警告: RIOT_API_KEYが設定されていません")
        print(".envファイルを作成して、APIキーを設定してください")
        return

    master_league = get_master_league(api_key)
    pprint(master_league)

if __name__ == "__main__":
    main()

