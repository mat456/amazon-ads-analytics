-- ==================================================
-- STAGING LAYER
-- Cleaned and standardized source tables
-- ==================================================

DROP TABLE IF EXISTS staging.stg_ads_performance;
DROP TABLE IF EXISTS staging.stg_targets;
DROP TABLE IF EXISTS staging.stg_ad_groups;
DROP TABLE IF EXISTS staging.stg_campaigns;
DROP TABLE IF EXISTS staging.stg_products;


-- --------------------------------------------------
-- Products
-- --------------------------------------------------

CREATE TABLE staging.stg_products AS
SELECT
    TRIM(product_id) AS product_id,
    TRIM(asin) AS asin,
    TRIM(sku) AS sku,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    selling_price,
    unit_cost,
    launch_date,
    UPPER(TRIM(status)) AS status
FROM raw.products;

ALTER TABLE staging.stg_products
ADD PRIMARY KEY (product_id);


-- --------------------------------------------------
-- Campaigns
-- --------------------------------------------------

CREATE TABLE staging.stg_campaigns AS
SELECT
    TRIM(campaign_id) AS campaign_id,
    TRIM(campaign_name) AS campaign_name,
    TRIM(product_id) AS product_id,
    TRIM(campaign_type) AS campaign_type,
    UPPER(TRIM(targeting_type)) AS targeting_type,
    daily_budget,
    start_date,
    end_date,
    UPPER(TRIM(status)) AS status
FROM raw.campaigns;

ALTER TABLE staging.stg_campaigns
ADD PRIMARY KEY (campaign_id);

ALTER TABLE staging.stg_campaigns
ADD CONSTRAINT fk_campaign_product
FOREIGN KEY (product_id)
REFERENCES staging.stg_products(product_id);


-- --------------------------------------------------
-- Ad groups
-- --------------------------------------------------

CREATE TABLE staging.stg_ad_groups AS
SELECT
    TRIM(ad_group_id) AS ad_group_id,
    TRIM(ad_group_name) AS ad_group_name,
    TRIM(campaign_id) AS campaign_id,
    UPPER(TRIM(status)) AS status
FROM raw.ad_groups;

ALTER TABLE staging.stg_ad_groups
ADD PRIMARY KEY (ad_group_id);

ALTER TABLE staging.stg_ad_groups
ADD CONSTRAINT fk_ad_group_campaign
FOREIGN KEY (campaign_id)
REFERENCES staging.stg_campaigns(campaign_id);


-- --------------------------------------------------
-- Targets
-- --------------------------------------------------

CREATE TABLE staging.stg_targets AS
SELECT
    TRIM(target_id) AS target_id,
    TRIM(ad_group_id) AS ad_group_id,
    UPPER(TRIM(target_type)) AS target_type,
    TRIM(target_value) AS target_value,
    NULLIF(UPPER(TRIM(match_type)), '') AS match_type,
    default_bid,
    UPPER(TRIM(status)) AS status
FROM raw.targets;

ALTER TABLE staging.stg_targets
ADD PRIMARY KEY (target_id);

ALTER TABLE staging.stg_targets
ADD CONSTRAINT fk_target_ad_group
FOREIGN KEY (ad_group_id)
REFERENCES staging.stg_ad_groups(ad_group_id);


-- --------------------------------------------------
-- Ads performance
-- --------------------------------------------------

CREATE TABLE staging.stg_ads_performance AS
SELECT
    date,
    TRIM(product_id) AS product_id,
    TRIM(campaign_id) AS campaign_id,
    TRIM(ad_group_id) AS ad_group_id,
    TRIM(target_id) AS target_id,
    impressions,
    clicks,
    spend,
    orders,
    units_sold,
    attributed_sales
FROM raw.ads_performance;

ALTER TABLE staging.stg_ads_performance
ADD PRIMARY KEY (date, target_id);

ALTER TABLE staging.stg_ads_performance
ADD CONSTRAINT fk_performance_product
FOREIGN KEY (product_id)
REFERENCES staging.stg_products(product_id);

ALTER TABLE staging.stg_ads_performance
ADD CONSTRAINT fk_performance_campaign
FOREIGN KEY (campaign_id)
REFERENCES staging.stg_campaigns(campaign_id);

ALTER TABLE staging.stg_ads_performance
ADD CONSTRAINT fk_performance_ad_group
FOREIGN KEY (ad_group_id)
REFERENCES staging.stg_ad_groups(ad_group_id);

ALTER TABLE staging.stg_ads_performance
ADD CONSTRAINT fk_performance_target
FOREIGN KEY (target_id)
REFERENCES staging.stg_targets(target_id);