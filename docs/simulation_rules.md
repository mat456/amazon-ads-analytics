# Synthetic Data Simulation Rules

## Objective

Generate realistic and internally consistent Amazon Ads performance data
for the Nexa Living portfolio.

The synthetic dataset does not reproduce real client data or Amazon
benchmarks.

## Simulation logic

Performance is generated sequentially:

Impressions
→ Clicks
→ Spend
→ Orders
→ Units sold
→ Attributed sales

Each metric therefore depends on the previous steps rather than being
generated independently.

## Main drivers

### Product-level factors

- base demand
- conversion potential
- advertising competition
- seasonality

### Target-level factors

- traffic potential
- base CTR
- conversion modifier
- semantic relevance
- match type

### Campaign-level factors

- daily budget
- campaign start date
- campaign maturity

### Time-level factors

- monthly seasonality
- daily variation

## Core relationships

Clicks are generated from impressions and CTR.

Advertising spend is derived from clicks and CPC.

Orders are generated from clicks and conversion rate.

Units sold are derived from orders.

Attributed sales are calculated from units sold and product price.

## Budget constraint

Daily campaign spend cannot materially exceed the configured campaign
daily budget. When theoretical traffic would generate excessive spend,
traffic is reduced to reflect a budget-constrained campaign.

## Data quality

The initial simulation generates logically consistent data.

Data quality issues will be injected separately in a later step so that
business simulation and data quality testing remain independent.