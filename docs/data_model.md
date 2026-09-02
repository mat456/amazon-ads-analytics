# Data Model

## 1. Analytical objective

The data model is designed to analyze the performance and profitability of
Amazon Sponsored Products campaigns for Nexa Living.

The model must support analysis by:

- date
- product
- campaign
- ad group
- target
- targeting type
- keyword match type

The main metrics analyzed are impressions, clicks, advertising spend,
orders, units sold and attributed sales.

---

## 2. Fact table grain

The grain of the main fact table is:

> One row per advertising target per day.

A target belongs to one ad group, one campaign and one advertised product.

Example:

2026-03-12 × "ergonomic laptop stand / EXACT"

The fact table therefore stores the daily advertising performance of each
active target.

---

## 3. Star schema

The analytical layer uses a star schema centered around `fact_ads_daily`.

                       dim_date
                           |
                           |
    dim_product ---- fact_ads_daily ---- dim_campaign
                           |
                    +------+------+
                    |             |
               dim_ad_group   dim_target

Each dimension can be joined directly to the fact table using a surrogate key.

---

## 4. Fact table

### fact_ads_daily

Keys:

- date_key
- product_key
- campaign_key
- ad_group_key
- target_key

Measures:

- impressions
- clicks
- spend
- orders
- units_sold
- attributed_sales

Derived KPIs such as CTR, CPC, conversion rate, ACOS and ROAS should be
calculated from the underlying additive measures instead of being stored as
daily ratios.

Examples:

CTR = SUM(clicks) / SUM(impressions)

CPC = SUM(spend) / SUM(clicks)

Conversion Rate = SUM(orders) / SUM(clicks)

ACOS = SUM(spend) / SUM(attributed_sales)

ROAS = SUM(attributed_sales) / SUM(spend)

---

## 5. Dimensions

### dim_date

Describes the calendar context of each observation.

Main attributes:

- date_key
- date
- day
- day_of_week
- week
- month
- month_name
- quarter
- year

### dim_product

Describes the advertised product.

Main attributes:

- product_key
- product_id
- asin
- sku
- product_name
- category
- selling_price
- unit_cost
- launch_date
- status

### dim_campaign

Describes the Amazon Ads campaign.

Main attributes:

- campaign_key
- campaign_id
- campaign_name
- campaign_type
- targeting_type
- daily_budget
- start_date
- end_date
- status

### dim_ad_group

Describes the ad group.

Main attributes:

- ad_group_key
- ad_group_id
- ad_group_name
- status

### dim_target

Describes the advertising target.

Main attributes:

- target_key
- target_id
- target_type
- target_value
- match_type
- default_bid
- status

---

## 6. Keys

Source identifiers such as:

- P010
- C018
- AG018
- T082

are business keys.

The analytical model will also use surrogate integer keys such as:

- product_key
- campaign_key
- ad_group_key
- target_key

These keys are generated inside the analytical layer and used for joins
between fact and dimension tables.

---

## 7. Data layers

The project will follow a layered SQL architecture:

CSV sources
    |
    v
RAW
    |
    v
STAGING
    |
    v
MART
    |
    v
TABLEAU

### Raw

Contains data close to the original source structure.

Examples:

- raw.products
- raw.campaigns
- raw.ad_groups
- raw.targets
- raw.ads_performance

### Staging

Contains cleaned, standardized and quality-controlled data.

Examples:

- staging.stg_products
- staging.stg_campaigns
- staging.stg_ad_groups
- staging.stg_targets
- staging.stg_ads_performance

### Mart

Contains the analytical star schema used by Tableau.

- mart.dim_date
- mart.dim_product
- mart.dim_campaign
- mart.dim_ad_group
- mart.dim_target
- mart.fact_ads_daily