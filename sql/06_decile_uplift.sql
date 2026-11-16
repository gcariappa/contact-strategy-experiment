-- 06 | Does emailing help in each score decile? Conversion uplift (emailed minus not emailed)
-- and the unsubscribe rate among those emailed.
SELECT decile,
       SUM(emailed)                                              AS n_emailed,
       SUM(1 - emailed)                                          AS n_not_emailed,
       ROUND(100.0 * AVG(CASE WHEN emailed = 1 THEN converted END), 2) AS conv_emailed_pct,
       ROUND(100.0 * AVG(CASE WHEN emailed = 0 THEN converted END), 2) AS conv_not_emailed_pct,
       ROUND(100.0 * (AVG(CASE WHEN emailed = 1 THEN converted END)
                    - AVG(CASE WHEN emailed = 0 THEN converted END)), 2) AS uplift_pp,
       ROUND(100.0 * AVG(CASE WHEN emailed = 1 THEN unsubscribed END), 2) AS unsub_emailed_pct
FROM reengagement_deciles
GROUP BY decile
ORDER BY decile;
