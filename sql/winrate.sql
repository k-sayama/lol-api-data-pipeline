-- チャンピオン別勝率
SELECT 
  participant.champion_name,
  COUNT(*) as total_games,
  SUM(CASE WHEN participant.win THEN 1 ELSE 0 END) as wins,
  ROUND(SUM(CASE WHEN participant.win THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as win_rate
FROM `{project_id}.{dataset_id}.{table_id}`,
UNNEST(participants) as participant
GROUP BY participant.champion_name
HAVING COUNT(*) >= 5
ORDER BY total_games DESC