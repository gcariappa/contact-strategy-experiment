-- 01 | Who is in the split test, after cleaning?
-- Each customer's FIRST abandonment only, one reminder per customer (duplicates removed),
-- reminders with no recorded test arm excluded. One row per randomised customer.
CREATE VIEW IF NOT EXISTS test_population AS
WITH first_abandon AS (
    SELECT customer_id, MIN(started_date) AS abandoned_date
    FROM applications
    WHERE status = 'abandoned'
    GROUP BY customer_id
),
reminder AS (
    SELECT DISTINCT customer_id, test_arm          -- DISTINCT removes duplicate sends
    FROM emails_sent
    WHERE email_type = 'abandoned_reminder'
      AND test_arm IS NOT NULL
)
SELECT f.customer_id,
       r.test_arm,
       TRIM(c.segment) AS segment,
       o.converted,
       o.loan_value,
       o.repaid_on_time,
       o.unsubscribed,
       o.complained
FROM first_abandon f
JOIN reminder  r ON r.customer_id = f.customer_id
JOIN customers c ON c.customer_id = f.customer_id
JOIN outcomes  o ON o.customer_id = f.customer_id
                AND o.campaign = 'abandoned_reminder';

SELECT * FROM test_population;
