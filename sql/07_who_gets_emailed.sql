-- 07 | Selection bias check: what share of each decile does the model email?
-- Where almost everyone is emailed, the "not emailed" comparison group is tiny, so uplift there is uncertain,
-- and a model retrained on outcomes only sees how emailed customers behave.
SELECT decile,
       COUNT(*)                              AS customers,
       ROUND(100.0 * AVG(emailed), 1)        AS pct_emailed,
       SUM(1 - emailed)                      AS comparison_group_size
FROM reengagement_deciles
GROUP BY decile
ORDER BY decile;
