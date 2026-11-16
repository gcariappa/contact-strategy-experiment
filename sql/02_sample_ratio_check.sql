-- 02 | Did randomisation work? Arm sizes and segment mix (sample-ratio mismatch check)
SELECT test_arm,
       COUNT(*)                                          AS customers,
       ROUND(100.0 * SUM(segment = 'Micro')  / COUNT(*), 1) AS pct_micro,
       ROUND(100.0 * SUM(segment = 'Small')  / COUNT(*), 1) AS pct_small,
       ROUND(100.0 * SUM(segment = 'Medium') / COUNT(*), 1) AS pct_medium
FROM test_population
GROUP BY test_arm;
