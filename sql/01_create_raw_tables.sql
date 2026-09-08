-- ==================================================
-- RAW LAYER
-- Source-shaped tables for synthetic Amazon Ads data
-- ==================================================


-- --------------------------------------------------
-- Products
-- --------------------------------------------------

CREATE TABLE raw.products (
    product_id      VARCHAR(10),
    asin            VARCHAR(20),
    sku             VARCHAR(30),
    product_name    VARCHAR(100),
    category        VARCHAR(50),
    selling_price   NUMERIC(10, 2),
    unit_cost       NUMERIC(10, 2),
    launch_date     DATE,
    status          VARCHAR(20)
);


-- --------------------------------------------------
-- Campaigns
-- --------------------------------------------------

CREATE TABLE raw.campaigns (
    campaign_id     VARCHAR(10),
    campaign_name   VARCHAR(150),
    product_id      VARCHAR(10),
    campaign_type   VARCHAR(50),
    targeting_type  VARCHAR(50),
    daily_budget    NUMERIC(10, 2),
    start_date      DATE,
    end_date        DATE,
    status          VARCHAR(20)
);


-- --------------------------------------------------
-- Ad groups
-- --------------------------------------------------

CREATE TABLE raw.ad_groups (
    ad_group_id     VARCHAR(10),
    ad_group_name   VARCHAR(150),
    campaign_id     VARCHAR(10),
    status          VARCHAR(20)
);


-- --------------------------------------------------
-- Targets
-- --------------------------------------------------

CREATE TABLE raw.targets (
    target_id       VARCHAR(10),
    ad_group_id     VARCHAR(10),
    target_type     VARCHAR(30),
    target_value    VARCHAR(150),
    match_type      VARCHAR(20),
    default_bid     NUMERIC(10, 2),
    status          VARCHAR(20)
);


-- --------------------------------------------------
-- Ads performance
-- --------------------------------------------------

CREATE TABLE raw.ads_performance (
    date                DATE,
    product_id          VARCHAR(10),
    campaign_id         VARCHAR(10),
    ad_group_id         VARCHAR(10),
    target_id           VARCHAR(10),
    impressions         INTEGER,
    clicks              INTEGER,
    spend               NUMERIC(10, 2),
    orders              INTEGER,
    units_sold          INTEGER,
    attributed_sales    NUMERIC(12, 2)
);