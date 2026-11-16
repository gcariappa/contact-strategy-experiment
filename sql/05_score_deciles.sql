-- 05 | Model check population: every customer eligible for the re-engagement email,
-- split into 10 equal groups by model score (decile 10 = highest score), flagged emailed or not.
CREATE VIEW IF NOT EXISTS reengagement_deciles AS
SELECT o.customer_id,
       c.model_score,
       NTILE(10) OVER (ORDER BY c.model_score) AS decile,
       EXISTS (SELECT 1 FROM emails_sent e
               WHERE e.customer_id = o.customer_id
                 AND e.email_type = 'reengagement')  AS emailed,
       o.converted,
       o.unsubscribed
FROM outcomes o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.campaign = 'reengagement';

SELECT * FROM reengagement_deciles;
