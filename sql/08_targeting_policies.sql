-- 08 | Targeting vs "email everyone": extra conversions and unsubscribes per 1,000 emails,
-- for each policy "email deciles N to 10". Uses each decile's measured uplift and unsubscribe rate.
WITH d AS (
    SELECT decile,
           COUNT(*) AS customers,
           AVG(CASE WHEN emailed = 1 THEN converted END)
             - AVG(CASE WHEN emailed = 0 THEN converted END) AS uplift,
           AVG(CASE WHEN emailed = 1 THEN unsubscribed END)  AS unsub
    FROM reengagement_deciles
    GROUP BY decile
)
SELECT 'Email deciles ' || p.decile || '-10'                          AS policy,
       SUM(d.customers)                                                 AS emails_sent,
       ROUND(SUM(d.customers * d.uplift), 0)                            AS extra_conversions,
       ROUND(1000.0 * SUM(d.customers * d.uplift) / SUM(d.customers), 1) AS extra_conv_per_1000,
       ROUND(1000.0 * SUM(d.customers * d.unsub)  / SUM(d.customers), 1) AS unsubs_per_1000
FROM d p
JOIN d ON d.decile >= p.decile
GROUP BY p.decile
ORDER BY p.decile;
