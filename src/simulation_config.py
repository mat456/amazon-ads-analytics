from datetime import date

# --------------------------------------------------
# General settings
# --------------------------------------------------

RANDOM_SEED = 42

START_DATE = date(2025, 10, 1)
END_DATE = date(2026, 6, 30)

BASE_DAILY_IMPRESSIONS = 350


# --------------------------------------------------
# Seasonality
# --------------------------------------------------

SEASONALITY_FACTORS = {
    "stable": {
        10: 1.00,
        11: 1.05,
        12: 1.10,
        1: 0.95,
        2: 1.00,
        3: 1.00,
        4: 1.00,
        5: 1.00,
        6: 1.00,
    },
    "winter": {
        10: 0.85,
        11: 1.05,
        12: 1.25,
        1: 1.20,
        2: 1.10,
        3: 0.90,
        4: 0.75,
        5: 0.65,
        6: 0.60,
    },
    "summer": {
        10: 0.65,
        11: 0.55,
        12: 0.50,
        1: 0.55,
        2: 0.60,
        3: 0.75,
        4: 0.90,
        5: 1.15,
        6: 1.35,
    },
    "january": {
        10: 0.80,
        11: 0.85,
        12: 0.95,
        1: 1.45,
        2: 0.95,
        3: 0.85,
        4: 0.80,
        5: 0.80,
        6: 0.75,
    },
    "back_to_school": {
        10: 1.10,
        11: 1.00,
        12: 0.95,
        1: 1.10,
        2: 1.00,
        3: 0.95,
        4: 0.95,
        5: 0.90,
        6: 0.90,
    },
}


# --------------------------------------------------
# Target behaviour
# --------------------------------------------------

TARGET_PROFILES = {
    "AUTO_CLOSE": {
        "traffic_multiplier": 0.90,
        "ctr_base": 0.040,
        "conversion_multiplier": 1.05,
    },
    "AUTO_LOOSE": {
        "traffic_multiplier": 1.20,
        "ctr_base": 0.023,
        "conversion_multiplier": 0.80,
    },
    "AUTO_SUBSTITUTES": {
        "traffic_multiplier": 0.80,
        "ctr_base": 0.028,
        "conversion_multiplier": 0.90,
    },
    "AUTO_COMPLEMENTS": {
        "traffic_multiplier": 0.55,
        "ctr_base": 0.014,
        "conversion_multiplier": 0.65,
    },

    "KEYWORD_BROAD": {
        "traffic_multiplier": 1.25,
        "ctr_base": 0.024,
        "conversion_multiplier": 0.80,
    },
    "KEYWORD_PHRASE": {
        "traffic_multiplier": 0.90,
        "ctr_base": 0.036,
        "conversion_multiplier": 1.00,
    },
    "KEYWORD_EXACT": {
        "traffic_multiplier": 0.65,
        "ctr_base": 0.050,
        "conversion_multiplier": 1.20,
    },

    "PRODUCT": {
        "traffic_multiplier": 0.75,
        "ctr_base": 0.027,
        "conversion_multiplier": 0.90,
    },
    "CATEGORY": {
        "traffic_multiplier": 1.10,
        "ctr_base": 0.018,
        "conversion_multiplier": 0.70,
    },
}


# --------------------------------------------------
# Conversion rate
# --------------------------------------------------

BASE_CONVERSION_RATE = 0.08

MIN_CONVERSION_RATE = 0.01
MAX_CONVERSION_RATE = 0.22


# --------------------------------------------------
# CPC / competition
# --------------------------------------------------

MIN_CPC_FACTOR = 0.70
MAX_CPC_FACTOR = 1.15

COMPETITION_CPC_WEIGHT = 0.35


# --------------------------------------------------
# Daily variation
# --------------------------------------------------

DAILY_TRAFFIC_NOISE_STD = 0.08
CTR_NOISE_STD = 0.10
CPC_NOISE_STD = 0.07
CONVERSION_NOISE_STD = 0.10


# --------------------------------------------------
# Campaign maturity
# --------------------------------------------------

CAMPAIGN_MATURITY = {
    "week_1": 0.65,
    "week_2_3": 0.85,
    "mature": 1.00,
}


# --------------------------------------------------
# Units per order
# --------------------------------------------------

MULTI_UNIT_ORDER_PROBABILITY = 0.08

# --------------------------------------------------
# Target relevance
# --------------------------------------------------

AUTO_RELEVANCE = {
    "close_match": 1.10,
    "loose_match": 0.80,
    "substitutes": 0.90,
    "complements": 0.65,
}


DEFAULT_KEYWORD_RELEVANCE = 1.00


KEYWORD_RELEVANCE_OVERRIDES = {
    # Milk Frother
    "coffee milk frother": 1.05,
    "handheld milk frother": 1.05,
    "coffee accessories": 0.65,

    # Kitchen Scale
    "food weighing scale": 1.00,
    "precision kitchen scale": 1.10,
    "baking accessories": 0.65,

    # Travel Mug
    "coffee travel mug": 1.05,
    "thermal coffee mug": 1.10,

    # Desk Lamp
    "office desk lamp": 1.05,
    "adjustable desk lamp": 1.10,
    "desk accessories": 0.65,

    # Water Bottle
    "insulated water bottle": 1.05,
    "reusable water bottle": 1.00,
    "sports bottle": 0.80,

    # Laptop Stand
    "adjustable laptop stand": 1.10,
    "ergonomic laptop stand": 1.15,
    "macbook stand": 0.95,
    "computer stand": 0.70,

    # Resistance Bands
    "fitness resistance bands": 1.05,
    "workout bands": 0.95,
    "home gym equipment": 0.65,

    # Travel Organizer
    "packing organizer": 1.00,
    "packing cubes": 1.05,
    "travel accessories": 0.65,
}


PRODUCT_TARGET_RELEVANCE = {
    "PRODUCT": 0.95,
    "CATEGORY": 0.75,
}