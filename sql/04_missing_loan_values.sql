-- 04 | Data quality: conversions with no loan value, by arm (excluded from value, kept in conversion)
SELECT test_arm,
       SUM(converted = 1)                         AS conversions,
       SUM(converted = 1 AND loan_value IS NULL)  AS missing_loan_value
FROM test_population
GROUP BY test_arm;
