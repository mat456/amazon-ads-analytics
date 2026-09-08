-- ==================================================
-- MART LAYER
-- Analytical star schema
-- ==================================================

-- Drop fact table first because it depends on dimensions
DROP TABLE IF EXISTS mart.fact_ads_daily;

DROP TABLE IF EXISTS mart.dim_target;
DROP TABLE IF EXISTS mart.dim_ad_group;
DROP TABLE IF EXISTS mart.dim_campaign;
DROP TABLE IF EXISTS mart.dim_product;
DROP TABLE IF EXISTS mart.dim_date;


-- ==================================================
-- DATE DIMENSION
-- ==================================================

CREATE TABLE mart.dim_date (
    date_key        INTEGER PRIMARY KEY,
    date            DATE NOT NULL UNIQUE,
    day             INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,
    day_name        VARCHAR(20) NOT NULL,
    week            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    month_name      VARCHAR(20) NOT NULL,
    quarter         INTEGER NOT NULL,
    year            INTEGER NOT NULL
);

INSERT INTO mart.dim_date (
    date_key,
    date,
    day,
    day_of_week,
    day_name,
    week,
    month,
    month_name,
    quarter,
    year
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER AS date_key,
    d::DATE AS date,
    EXTRACT(DAY FROM d)::INTEGER AS day,
    EXTRACT(ISODOW FROM d)::INTEGER AS day_of_week,
    TO_CHAR(d, 'FMDay') AS day_name,
    EXTRACT(WEEK FROM d)::INTEGER AS week,
    EXTRACT(MONTH FROM d)::INTEGER AS month,
    TO_CHAR(d, 'FMMonth') AS month_name,
    EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
    EXTRACT(YEAR FROM d)::INTEGER AS year
FROM generate_series(
    (SELECT MIN(date) FROM staging.stg_ads_performance),
    (SELECT MAX(date) FROM staging.stg_ads_performance),
    INTERVAL '1 day'
) AS d;


-- ==================================================
-- PRODUCT DIMENSION
-- ==================================================

CREATE TABLE mart.dim_product (
    product_key     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      VARCHAR(10) NOT NULL UNIQUE,
    asin            VARCHAR(20),
    sku             VARCHAR(30),
    product_name    VARCHAR(100),
    category        VARCHAR(50),
    selling_price   NUMERIC(10, 2),
    unit_cost       NUMERIC(10, 2),
    launch_date     DATE,
    status          VARCHAR(20)
);

INSERT INTO mart.dim_product (
    product_id,
    asin,
    sku,
    product_name,
    category,
    selling_price,
    unit_cost,
    launch_date,
    status
)
SELECT
    product_id,
    asin,
    sku,
    product_name,
    category,
    selling_price,
    unit_cost,
    launch_date,
    status
FROM staging.stg_products;


-- ==================================================
-- CAMPAIGN DIMENSION
-- ==================================================

CREATE TABLE mart.dim_campaign (
    campaign_key    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    campaign_id     VARCHAR(10) NOT NULL UNIQUE,
    campaign_name   VARCHAR(150),
    campaign_type   VARCHAR(50),
    targeting_type  VARCHAR(50),
    daily_budget    NUMERIC(10, 2),
    start_date      DATE,
    end_date        DATE,
    status          VARCHAR(20)
);

INSERT INTO mart.dim_campaign (
    campaign_id,
    campaign_name,
    campaign_type,
    targeting_type,
    daily_budget,
    start_date,
    end_date,
    status
)
SELECT
    campaign_id,
    campaign_name,
    campaign_type,
    targeting_type,
    daily_budget,
    start_date,
    end_date,
    status
FROM staging.stg_campaigns;


-- ==================================================
-- AD GROUP DIMENSION
-- ==================================================

CREATE TABLE mart.dim_ad_group (
    ad_group_key    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ad_group_id     VARCHAR(10) NOT NULL UNIQUE,
    ad_group_name   VARCHAR(150),
    status          VARCHAR(20)
);

INSERT INTO mart.dim_ad_group (
    ad_group_id,
    ad_group_name,
    status
)
SELECT
    ad_group_id,
    ad_group_name,
    status
FROM staging.stg_ad_groups;


-- ==================================================
-- TARGET DIMENSION
-- ==================================================

CREATE TABLE mart.dim_target (
    target_key      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_id       VARCHAR(10) NOT NULL UNIQUE,
    target_type     VARCHAR(30),
    target_value    VARCHAR(150),
    match_type      VARCHAR(20),
    default_bid     NUMERIC(10, 2),
    status          VARCHAR(20)
);

INSERT INTO mart.dim_target (
    target_id,
    target_type,
    target_value,
    match_type,
    default_bid,
    status
)
SELECT
    target_id,
    target_type,
    target_value,
    match_type,
    default_bid,
    status
FROM staging.stg_targets;


-- ==================================================
-- FACT TABLE
-- Grain: one row per target per day
-- ==================================================

CREATE TABLE mart.fact_ads_daily (
    date_key            INTEGER NOT NULL,
    product_key         INTEGER NOT NULL,
    campaign_key        INTEGER NOT NULL,
    ad_group_key        INTEGER NOT NULL,
    target_key          INTEGER NOT NULL,

    impressions         INTEGER NOT NULL,
    clicks              INTEGER NOT NULL,
    spend               NUMERIC(10, 2) NOT NULL,
    orders              INTEGER NOT NULL,
    units_sold          INTEGER NOT NULL,
    attributed_sales    NUMERIC(12, 2) NOT NULL,

    PRIMARY KEY (date_key, target_key),

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES mart.dim_date(date_key),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_key)
        REFERENCES mart.dim_product(product_key),

    CONSTRAINT fk_fact_campaign
        FOREIGN KEY (campaign_key)
        REFERENCES mart.dim_campaign(campaign_key),

    CONSTRAINT fk_fact_ad_group
        FOREIGN KEY (ad_group_key)
        REFERENCES mart.dim_ad_group(ad_group_key),

    CONSTRAINT fk_fact_target
        FOREIGN KEY (target_key)
        REFERENCES mart.dim_target(target_key)
);


INSERT INTO mart.fact_ads_daily (
    date_key,
    product_key,
    campaign_key,
    ad_group_key,
    target_key,
    impressions,
    clicks,
    spend,
    orders,
    units_sold,
    attributed_sales
)
SELECT
    d.date_key,
    p.product_key,
    c.campaign_key,
    a.ad_group_key,
    t.target_key,
    f.impressions,
    f.clicks,
    f.spend,
    f.orders,
    f.units_sold,
    f.attributed_sales
FROM staging.stg_ads_performance f

JOIN mart.dim_date d
    ON f.date = d.date

JOIN mart.dim_product p
    ON f.product_id = p.product_id

JOIN mart.dim_campaign c
    ON f.campaign_id = c.campaign_id

JOIN mart.dim_ad_group a
    ON f.ad_group_id = a.ad_group_id

JOIN mart.dim_target t
    ON f.target_id = t.target_id;