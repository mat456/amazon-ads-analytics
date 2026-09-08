-- ==================================================
-- DATA QUALITY CHECKS
-- ==================================================


-- --------------------------------------------------
-- 1. Duplicate business keys
-- --------------------------------------------------

SELECT product_id, COUNT(*)
FROM raw.products
GROUP BY product_id
HAVING COUNT(*) > 1;

SELECT campaign_id, COUNT(*)
FROM raw.campaigns
GROUP BY campaign_id
HAVING COUNT(*) > 1;

SELECT ad_group_id, COUNT(*)
FROM raw.ad_groups
GROUP BY ad_group_id
HAVING COUNT(*) > 1;

SELECT target_id, COUNT(*)
FROM raw.targets
GROUP BY target_id
HAVING COUNT(*) > 1;


-- --------------------------------------------------
-- 2. Referential integrity
-- --------------------------------------------------

SELECT c.*
FROM raw.campaigns c
LEFT JOIN raw.products p
    ON c.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT a.*
FROM raw.ad_groups a
LEFT JOIN raw.campaigns c
    ON a.campaign_id = c.campaign_id
WHERE c.campaign_id IS NULL;

SELECT t.*
FROM raw.targets t
LEFT JOIN raw.ad_groups a
    ON t.ad_group_id = a.ad_group_id
WHERE a.ad_group_id IS NULL;


-- --------------------------------------------------
-- 3. Mandatory fields
-- --------------------------------------------------

SELECT *
FROM raw.ads_performance
WHERE date IS NULL
   OR product_id IS NULL
   OR campaign_id IS NULL
   OR ad_group_id IS NULL
   OR target_id IS NULL;


-- --------------------------------------------------
-- 4. Negative values
-- --------------------------------------------------

SELECT *
FROM raw.ads_performance
WHERE impressions < 0
   OR clicks < 0
   OR spend < 0
   OR orders < 0
   OR units_sold < 0
   OR attributed_sales < 0;


-- --------------------------------------------------
-- 5. Business consistency
-- --------------------------------------------------

SELECT *
FROM raw.ads_performance
WHERE clicks > impressions;

SELECT *
FROM raw.ads_performance
WHERE orders > clicks;

SELECT *
FROM raw.ads_performance
WHERE units_sold < orders;


-- --------------------------------------------------
-- 6. Performance foreign keys
-- --------------------------------------------------

SELECT f.*
FROM raw.ads_performance f
LEFT JOIN raw.products p
    ON f.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT f.*
FROM raw.ads_performance f
LEFT JOIN raw.campaigns c
    ON f.campaign_id = c.campaign_id
WHERE c.campaign_id IS NULL;

SELECT f.*
FROM raw.ads_performance f
LEFT JOIN raw.ad_groups a
    ON f.ad_group_id = a.ad_group_id
WHERE a.ad_group_id IS NULL;

SELECT f.*
FROM raw.ads_performance f
LEFT JOIN raw.targets t
    ON f.target_id = t.target_id
WHERE t.target_id IS NULL;


-- --------------------------------------------------
-- 7. Campaign activity dates
-- --------------------------------------------------

SELECT f.*
FROM raw.ads_performance f
JOIN raw.campaigns c
    ON f.campaign_id = c.campaign_id
WHERE f.date < c.start_date
   OR (
        c.end_date IS NOT NULL
        AND f.date > c.end_date
   );


-- --------------------------------------------------
-- 8. Daily campaign budget
-- --------------------------------------------------

SELECT
    f.date,
    f.campaign_id,
    SUM(f.spend) AS total_spend,
    c.daily_budget
FROM raw.ads_performance f
JOIN raw.campaigns c
    ON f.campaign_id = c.campaign_id
GROUP BY
    f.date,
    f.campaign_id,
    c.daily_budget
HAVING SUM(f.spend) > c.daily_budget;