from pathlib import Path

import numpy as np
import pandas as pd


from product_profiles import PRODUCT_PROFILES

from simulation_config import (
    START_DATE,
    END_DATE,
    SEASONALITY_FACTORS,
    TARGET_PROFILES,
    CAMPAIGN_MATURITY,
    AUTO_RELEVANCE,
    DEFAULT_KEYWORD_RELEVANCE,
    KEYWORD_RELEVANCE_OVERRIDES,
    PRODUCT_TARGET_RELEVANCE,
    RANDOM_SEED,
    BASE_DAILY_IMPRESSIONS,
    DAILY_TRAFFIC_NOISE_STD,
    CTR_NOISE_STD,
    CPC_NOISE_STD,
    MIN_CPC_FACTOR,
    MAX_CPC_FACTOR,
    COMPETITION_CPC_WEIGHT,
    BASE_CONVERSION_RATE,
    MIN_CONVERSION_RATE,
    MAX_CONVERSION_RATE,
    CONVERSION_NOISE_STD,
    MULTI_UNIT_ORDER_PROBABILITY
    )


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
# --------------------------------------------------
# Load reference data
# --------------------------------------------------

def load_reference_data():
    products = pd.read_csv(REFERENCE_DIR / "products.csv")
    campaigns = pd.read_csv(REFERENCE_DIR / "campaigns.csv")
    ad_groups = pd.read_csv(REFERENCE_DIR / "ad_groups.csv")
    targets = pd.read_csv(REFERENCE_DIR / "targets.csv")

    return products, campaigns, ad_groups, targets


# --------------------------------------------------
# Validate relationships
# --------------------------------------------------

def validate_reference_data(products, campaigns, ad_groups, targets):
    # Unique business keys
    assert products["product_id"].is_unique, "Duplicate product_id detected"
    assert campaigns["campaign_id"].is_unique, "Duplicate campaign_id detected"
    assert ad_groups["ad_group_id"].is_unique, "Duplicate ad_group_id detected"
    assert targets["target_id"].is_unique, "Duplicate target_id detected"

    # Campaign → Product
    unknown_products = set(campaigns["product_id"]) - set(products["product_id"])
    assert not unknown_products, (
        f"Unknown product_id in campaigns: {unknown_products}"
    )

    # Ad Group → Campaign
    unknown_campaigns = set(ad_groups["campaign_id"]) - set(
        campaigns["campaign_id"]
    )
    assert not unknown_campaigns, (
        f"Unknown campaign_id in ad_groups: {unknown_campaigns}"
    )

    # Target → Ad Group
    unknown_ad_groups = set(targets["ad_group_id"]) - set(
        ad_groups["ad_group_id"]
    )
    assert not unknown_ad_groups, (
        f"Unknown ad_group_id in targets: {unknown_ad_groups}"
    )

    print("Reference data validation successful.")


# --------------------------------------------------
# Build target-level base table
# --------------------------------------------------

def build_target_base(products, campaigns, ad_groups, targets):
    target_base = (
        targets
        .merge(
            ad_groups,
            on="ad_group_id",
            how="left",
            suffixes=("", "_ad_group"),
        )
        .merge(
            campaigns,
            on="campaign_id",
            how="left",
            suffixes=("", "_campaign"),
        )
        .merge(
            products,
            on="product_id",
            how="left",
            suffixes=("", "_product"),
        )
    )

    # Add hidden product simulation parameters
    profile_df = (
        pd.DataFrame.from_dict(PRODUCT_PROFILES, orient="index")
        .rename_axis("product_id")
        .reset_index()
    )

    target_base = target_base.merge(
        profile_df,
        on="product_id",
        how="left",
    )

    return target_base



# --------------------------------------------------
# Build daily target-level frame
# --------------------------------------------------

def build_daily_target_frame(target_base):
    rows = []

    for _, target in target_base.iterrows():
        campaign_start = pd.to_datetime(target["start_date"]).date()

        if pd.isna(target["end_date"]):
            campaign_end = END_DATE
        else:
            campaign_end = min(
                pd.to_datetime(target["end_date"]).date(),
                END_DATE,
            )

        campaign_start = max(campaign_start, START_DATE)

        active_dates = pd.date_range(
            start=campaign_start,
            end=campaign_end,
            freq="D",
        )

        for current_date in active_dates:
            row = target.to_dict()
            row["date"] = current_date.date()
            rows.append(row)

    daily_frame = pd.DataFrame(rows)

    return daily_frame


# --------------------------------------------------
# Simulation factors
# --------------------------------------------------

def get_target_profile_key(row):
    if row["target_type"] == "AUTO":
        mapping = {
            "close_match": "AUTO_CLOSE",
            "loose_match": "AUTO_LOOSE",
            "substitutes": "AUTO_SUBSTITUTES",
            "complements": "AUTO_COMPLEMENTS",
        }
        return mapping[row["target_value"]]

    if row["target_type"] == "KEYWORD":
        return f"KEYWORD_{row['match_type']}"

    if row["target_type"] == "PRODUCT":
        return "PRODUCT"

    if row["target_type"] == "CATEGORY":
        return "CATEGORY"

    raise ValueError(f"Unknown target type: {row['target_type']}")


def get_relevance_score(row):
    if row["target_type"] == "AUTO":
        return AUTO_RELEVANCE[row["target_value"]]

    if row["target_type"] == "KEYWORD":
        keyword = row["target_value"].lower()

        return KEYWORD_RELEVANCE_OVERRIDES.get(
            keyword,
            DEFAULT_KEYWORD_RELEVANCE,
        )

    if row["target_type"] in ("PRODUCT", "CATEGORY"):
        return PRODUCT_TARGET_RELEVANCE[row["target_type"]]

    raise ValueError(f"Unknown target type: {row['target_type']}")


def add_simulation_factors(daily_frame):
    daily_frame = daily_frame.copy()

    # Seasonality
    daily_frame["seasonality_factor"] = daily_frame.apply(
        lambda row: SEASONALITY_FACTORS[
            row["seasonality_profile"]
        ][row["date"].month],
        axis=1,
    )

    # Campaign maturity
    campaign_start = pd.to_datetime(
        daily_frame["start_date"]
    )

    current_date = pd.to_datetime(
        daily_frame["date"]
    )

    days_active = (current_date - campaign_start).dt.days

    daily_frame["campaign_maturity_factor"] = 1.0

    daily_frame.loc[
        days_active < 7,
        "campaign_maturity_factor",
    ] = CAMPAIGN_MATURITY["week_1"]

    daily_frame.loc[
        (days_active >= 7) & (days_active < 21),
        "campaign_maturity_factor",
    ] = CAMPAIGN_MATURITY["week_2_3"]

    daily_frame.loc[
        days_active >= 21,
        "campaign_maturity_factor",
    ] = CAMPAIGN_MATURITY["mature"]

    # Target behaviour
    daily_frame["target_profile"] = daily_frame.apply(
        get_target_profile_key,
        axis=1,
    )

    daily_frame["traffic_multiplier"] = daily_frame[
        "target_profile"
    ].map(
        lambda profile: TARGET_PROFILES[profile][
            "traffic_multiplier"
        ]
    )

    daily_frame["ctr_base"] = daily_frame[
        "target_profile"
    ].map(
        lambda profile: TARGET_PROFILES[profile]["ctr_base"]
    )

    daily_frame["target_conversion_multiplier"] = daily_frame[
        "target_profile"
    ].map(
        lambda profile: TARGET_PROFILES[profile][
            "conversion_multiplier"
        ]
    )

    # Semantic relevance
    daily_frame["relevance_score"] = daily_frame.apply(
        get_relevance_score,
        axis=1,
    )

    return daily_frame

# --------------------------------------------------
# Daily traffic variation
# --------------------------------------------------

def add_daily_traffic_variation(daily_frame):
    daily_frame = daily_frame.copy()
    daily_frame = daily_frame.sort_values(
        ["target_id", "date"]
    ).reset_index(drop=True)

    rng = np.random.default_rng(RANDOM_SEED)

    daily_frame["daily_traffic_factor"] = 1.0

    for target_id, group in daily_frame.groupby("target_id"):
        n_days = len(group)

        innovations = rng.normal(
            loc=0.0,
            scale=DAILY_TRAFFIC_NOISE_STD,
            size=n_days,
        )

        correlated_noise = np.zeros(n_days)

        for i in range(1, n_days):
            correlated_noise[i] = (
                0.75 * correlated_noise[i - 1]
                + innovations[i]
            )

        traffic_factor = np.clip(
            1.0 + correlated_noise,
            0.70,
            1.30,
        )

        daily_frame.loc[
            group.index,
            "daily_traffic_factor",
        ] = traffic_factor

    return daily_frame

# --------------------------------------------------
# Generate impressions
# --------------------------------------------------

def generate_impressions(daily_frame):
    daily_frame = daily_frame.copy()

    rng = np.random.default_rng(RANDOM_SEED + 1)

    daily_frame["expected_impressions"] = (
        BASE_DAILY_IMPRESSIONS
        * daily_frame["base_demand"]
        * daily_frame["traffic_multiplier"]
        * daily_frame["seasonality_factor"]
        * daily_frame["campaign_maturity_factor"]
        * daily_frame["daily_traffic_factor"]
    )

    daily_frame["impressions"] = rng.poisson(
        daily_frame["expected_impressions"]
    )

    return daily_frame

# --------------------------------------------------
# Generate clicks
# --------------------------------------------------

def generate_clicks(daily_frame):
    daily_frame = daily_frame.copy()

    rng = np.random.default_rng(RANDOM_SEED + 2)

    ctr_noise = rng.normal(
        loc=1.0,
        scale=CTR_NOISE_STD,
        size=len(daily_frame),
    )

    daily_frame["simulated_ctr"] = (
        daily_frame["ctr_base"]
        * daily_frame["relevance_score"]
        * ctr_noise
    ).clip(
        lower=0.005,
        upper=0.12,
    )

    daily_frame["clicks"] = rng.binomial(
        n=daily_frame["impressions"].astype(int),
        p=daily_frame["simulated_ctr"],
    )

    return daily_frame


# --------------------------------------------------
# Generate CPC and theoretical spend
# --------------------------------------------------

def generate_cpc_and_spend(daily_frame):
    daily_frame = daily_frame.copy()

    rng = np.random.default_rng(RANDOM_SEED + 3)

    cpc_noise = rng.normal(
        loc=1.0,
        scale=CPC_NOISE_STD,
        size=len(daily_frame),
    )

    competition_factor = (
        1.0
        + COMPETITION_CPC_WEIGHT
        * (daily_frame["competition_level"] - 0.5)
    )

    cpc_factor = (
        competition_factor
        * cpc_noise
    ).clip(
        lower=MIN_CPC_FACTOR,
        upper=MAX_CPC_FACTOR,
    )

    daily_frame["simulated_cpc"] = (
        daily_frame["default_bid"]
        * cpc_factor
    ).round(2)

    daily_frame["theoretical_spend"] = (
        daily_frame["clicks"]
        * daily_frame["simulated_cpc"]
    ).round(2)

    return daily_frame

# --------------------------------------------------
# Apply campaign daily budget constraint
# --------------------------------------------------

def apply_budget_constraint(daily_frame):
    daily_frame = daily_frame.copy()

    # Keep potential performance before budget limitation
    daily_frame["potential_impressions"] = daily_frame["impressions"]
    daily_frame["potential_clicks"] = daily_frame["clicks"]

    # Total theoretical spend by campaign and day
    campaign_daily_spend = (
        daily_frame
        .groupby(["date", "campaign_id"])["theoretical_spend"]
        .transform("sum")
    )

    # Share of theoretical traffic that can actually be served
    daily_frame["budget_factor"] = (
        daily_frame["daily_budget"]
        / campaign_daily_spend.replace(0, np.nan)
    ).clip(upper=1.0)

    daily_frame["budget_factor"] = (
        daily_frame["budget_factor"]
        .fillna(1.0)
    )

    daily_frame["is_budget_constrained"] = (
        daily_frame["budget_factor"] < 1.0
    )

    # Reduce traffic proportionally when campaign is budget constrained
    daily_frame["impressions"] = np.floor(
        daily_frame["potential_impressions"]
        * daily_frame["budget_factor"]
    ).astype(int)

    daily_frame["clicks"] = np.floor(
        daily_frame["potential_clicks"]
        * daily_frame["budget_factor"]
    ).astype(int)

    # Safety check
    daily_frame["clicks"] = np.minimum(
        daily_frame["clicks"],
        daily_frame["impressions"],
    )

    # Actual advertising spend
    daily_frame["spend"] = (
        daily_frame["clicks"]
        * daily_frame["simulated_cpc"]
    ).round(2)

    return daily_frame

# --------------------------------------------------
# Generate conversions
# --------------------------------------------------

def generate_conversions(daily_frame):
    daily_frame = daily_frame.copy()

    rng = np.random.default_rng(RANDOM_SEED + 4)

    conversion_noise = rng.normal(
        loc=1.0,
        scale=CONVERSION_NOISE_STD,
        size=len(daily_frame),
    )

    # Convert the 0-1 product score into a moderate multiplier
    product_conversion_factor = (
        0.60 + daily_frame["conversion_potential"]
    )

    daily_frame["simulated_conversion_rate"] = (
        BASE_CONVERSION_RATE
        * product_conversion_factor
        * daily_frame["target_conversion_multiplier"]
        * daily_frame["relevance_score"]
        * conversion_noise
    ).clip(
        lower=MIN_CONVERSION_RATE,
        upper=MAX_CONVERSION_RATE,
    )

    daily_frame["orders"] = rng.binomial(
        n=daily_frame["clicks"].astype(int),
        p=daily_frame["simulated_conversion_rate"],
    )

    return daily_frame

# --------------------------------------------------
# Generate units sold
# --------------------------------------------------

def generate_units_sold(daily_frame):
    daily_frame = daily_frame.copy()

    rng = np.random.default_rng(RANDOM_SEED + 5)

    extra_units = rng.binomial(
        n=daily_frame["orders"].astype(int),
        p=MULTI_UNIT_ORDER_PROBABILITY,
    )

    daily_frame["units_sold"] = (
        daily_frame["orders"] + extra_units
    )

    return daily_frame

# --------------------------------------------------
# Generate attributed sales
# --------------------------------------------------

def generate_attributed_sales(daily_frame):
    daily_frame = daily_frame.copy()

    daily_frame["attributed_sales"] = (
        daily_frame["units_sold"]
        * daily_frame["selling_price"]
    ).round(2)

    return daily_frame

# --------------------------------------------------
# Export synthetic source data
# --------------------------------------------------

def export_ads_performance(daily_frame):
    output_columns = [
        "date",
        "product_id",
        "campaign_id",
        "ad_group_id",
        "target_id",
        "impressions",
        "clicks",
        "spend",
        "orders",
        "units_sold",
        "attributed_sales",
    ]

    ads_performance = (
        daily_frame[output_columns]
        .sort_values(["date", "campaign_id", "target_id"])
        .reset_index(drop=True)
    )

    output_path = RAW_DIR / "ads_performance.csv"

    ads_performance.to_csv(
        output_path,
        index=False,
    )

    print(f"\nExported: {output_path}")
    print(f"Rows: {len(ads_performance):,}")

    return ads_performance

# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    # Load reference data
    products, campaigns, ad_groups, targets = load_reference_data()

    # Basic checks
    print(f"Products:   {len(products)}")
    print(f"Campaigns:  {len(campaigns)}")
    print(f"Ad groups:  {len(ad_groups)}")
    print(f"Targets:    {len(targets)}")

    # Validate relationships
    validate_reference_data(
        products,
        campaigns,
        ad_groups,
        targets,
    )

    # Build enriched target table
    target_base = build_target_base(
        products,
        campaigns,
        ad_groups,
        targets,
    )

    print("\nTarget base:")
    print(f"Rows:    {len(target_base)}")
    print(f"Columns: {len(target_base.columns)}")

    print(
        target_base[
            [
                "target_id",
                "target_value",
                "campaign_id",
                "product_id",
                "product_name",
                "selling_price",
                "daily_budget",
                "base_demand",
                "conversion_potential",
                "competition_level",
                "seasonality_profile",
            ]
        ].head()
    )

    # Build one row per active target per day
    daily_frame = build_daily_target_frame(target_base)
    daily_frame = add_simulation_factors(daily_frame)
    daily_frame = add_daily_traffic_variation(daily_frame)
    daily_frame = generate_impressions(daily_frame)
    daily_frame = generate_clicks(daily_frame)
    daily_frame = generate_cpc_and_spend(daily_frame)
    daily_frame = apply_budget_constraint(daily_frame)
    daily_frame = generate_conversions(daily_frame)
    daily_frame = generate_units_sold(daily_frame)
    daily_frame = generate_attributed_sales(daily_frame)
    ads_performance = export_ads_performance(daily_frame)

    print("\nDaily target frame:")
    print(f"Rows: {len(daily_frame):,}")
    print(
        f"Date range: {daily_frame['date'].min()} "
        f"to {daily_frame['date'].max()}"
    )

    print("\nRows by targeting type:")
    print(
        daily_frame
        .groupby("targeting_type")
        .size()
    )

    print("\nSimulation factors sample:")
    print(
        daily_frame[
            [
                "date",
                "product_name",
                "target_value",
                "match_type",
                "seasonality_factor",
                "campaign_maturity_factor",
                "traffic_multiplier",
                "ctr_base",
                "target_conversion_multiplier",
                "relevance_score",
            ]
        ].head(10)
    )
    print("\nImpressions summary:")
    print(
        daily_frame["impressions"].describe()
    )

    print("\nAverage impressions by target profile:")
    print(
        daily_frame
        .groupby("target_profile")["impressions"]
        .mean()
        .round(0)
        .sort_values(ascending=False)
    )

    print("\nClicks summary:")
    print(
        daily_frame["clicks"].describe()
    )

    print("\nCTR by target profile:")
    ctr_summary = (
        daily_frame
        .groupby("target_profile")
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
        )
    )

    ctr_summary["ctr"] = (
        ctr_summary["clicks"]
        / ctr_summary["impressions"]
    )

    print(
        (ctr_summary["ctr"] * 100)
        .round(2)
        .sort_values(ascending=False)
    )

    print("\nCPC summary:")
    print(
        daily_frame["simulated_cpc"].describe()
    )

    print("\nAverage CPC by product:")
    print(
        daily_frame
        .groupby("product_name")["simulated_cpc"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )

    print("\nTheoretical spend summary:")
    print(
        daily_frame["theoretical_spend"].describe()
    )

    campaign_daily_spend = (
        daily_frame
        .groupby(
            ["date", "campaign_id", "daily_budget"],
            as_index=False,
        )["theoretical_spend"]
        .sum()
    )

    campaign_daily_spend["budget_ratio"] = (
        campaign_daily_spend["theoretical_spend"]
        / campaign_daily_spend["daily_budget"]
    )

    print("\nCampaign/day theoretical spend vs budget:")
    print(
        campaign_daily_spend["budget_ratio"].describe()
    )
    print(
        "\nShare of campaign-days exceeding daily budget:"
    )

    budget_constrained_share = (
        campaign_daily_spend["budget_ratio"] > 1
    ).mean() * 100

    print(
        f"{budget_constrained_share:.1f}%"
    )

    actual_campaign_spend = (
        daily_frame
        .groupby(
            ["date", "campaign_id", "daily_budget"],
            as_index=False,
        )["spend"]
        .sum()
    )

    actual_campaign_spend["budget_ratio"] = (
        actual_campaign_spend["spend"]
        / actual_campaign_spend["daily_budget"]
    )

    print("\nActual campaign/day spend vs budget:")
    print(
        actual_campaign_spend["budget_ratio"].describe()
    )

    print("\nCampaign-days exceeding budget:")
    print(
        (
            actual_campaign_spend["budget_ratio"] > 1
        ).sum()
    )

    print("\nShare of rows affected by budget constraint:")
    print(
        f"{daily_frame['is_budget_constrained'].mean() * 100:.1f}%"
    )

    print("\nOrders summary:")
    print(
        daily_frame["orders"].describe()
    )

    conversion_summary = (
        daily_frame
        .groupby("target_profile")
        .agg(
            clicks=("clicks", "sum"),
            orders=("orders", "sum"),
        )
    )

    conversion_summary["conversion_rate"] = (
        conversion_summary["orders"]
        / conversion_summary["clicks"]
    )

    print("\nConversion rate by target profile:")
    print(
        (conversion_summary["conversion_rate"] * 100)
        .round(2)
        .sort_values(ascending=False)
    )

    print("\nSales summary:")
    print(
        daily_frame["attributed_sales"].describe()
    )

    print("\nTotal attributed sales:")
    print(
        f"€{daily_frame['attributed_sales'].sum():,.2f}"
    )

    