-- ==================================================
-- ANALYTICS VIEW
-- Flat presentation layer for Tableau
-- ==================================================

DROP VIEW IF EXISTS mart.v_ads_performance;

CREATE VIEW mart.v_ads_performance AS

SELECT
    -- Date
    d.date,
    d.day,
    d.day_of_week,
    d.day_name,
    d.week,
    d.month,
    d.month_name,
    d.quarter,
    d.year,

    -- Product
    p.product_id,
    p.asin,
    p.sku,
    p.product_name,
    p.category,
    p.selling_price,
    p.unit_cost,

    -- Campaign
    c.campaign_id,
    c.campaign_name,
    c.campaign_type,
    c.targeting_type,
    c.daily_budget,
    c.start_date AS campaign_start_date,
    c.end_date AS campaign_end_date,

    -- Ad group
    a.ad_group_id,
    a.ad_group_name,

    -- Target
    t.target_id,
    t.target_type,
    t.target_value,
    t.match_type,
    t.default_bid,

    -- Advertising metrics
    f.impressions,
    f.clicks,
    f.spend,
    f.orders,
    f.units_sold,
    f.attributed_sales,

    -- Profitability metrics
    ROUND(
        f.units_sold * p.unit_cost,
        2
    ) AS cogs,

    ROUND(
        f.attributed_sales - (f.units_sold * p.unit_cost),
        2
    ) AS gross_profit_before_ads,

    ROUND(
        f.attributed_sales
        - (f.units_sold * p.unit_cost)
        - f.spend,
        2
    ) AS ad_profit

FROM mart.fact_ads_daily f

JOIN mart.dim_date d
    ON f.date_key = d.date_key

JOIN mart.dim_product p
    ON f.product_key = p.product_key

JOIN mart.dim_campaign c
    ON f.campaign_key = c.campaign_key

JOIN mart.dim_ad_group a
    ON f.ad_group_key = a.ad_group_key

JOIN mart.dim_target t
    ON f.target_key = t.target_key;