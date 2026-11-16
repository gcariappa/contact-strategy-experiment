-- 03 | Conversion and guardrails by arm, overall and by segment
SELECT 'All' AS segment, test_arm, COUNT(*) AS customers,
       ROUND(100.0 * AVG(converted), 2)    AS conversion_pct,
       ROUND(100.0 * AVG(unsubscribed), 2) AS unsubscribe_pct,
       ROUND(100.0 * AVG(complained), 2)   AS complaint_pct
FROM test_population GROUP BY test_arm
UNION ALL
SELECT segment, test_arm, COUNT(*),
       ROUND(100.0 * AVG(converted), 2),
       ROUND(100.0 * AVG(unsubscribed), 2),
       ROUND(100.0 * AVG(complained), 2)
FROM test_population GROUP BY segment, test_arm
ORDER BY 1, 2;
