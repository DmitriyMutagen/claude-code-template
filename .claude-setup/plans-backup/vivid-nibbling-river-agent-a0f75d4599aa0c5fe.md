# Plan: COO Expert Analysis - Soul Way Ozon Operations

## Goal
Generate comprehensive `expert_coo_analysis.json` at `/Users/Dmitrij/Documents/нэп мп/output/expert_coo_analysis.json` covering 5 tasks: logistics audit, FBO optimization, stock management, cancellation reduction, and 2-week supply table.

## Data Collected (Read-Only Phase Complete)

### Source Files
1. `/Users/Dmitrij/Documents/нэп мп/output/agent2_logistics_analysis.json` — route_map, cluster_overpay_summary
2. `/Users/Dmitrij/Documents/нэп мп/output/agent2_top20_supply_data.json` — supply_table (20 SKUs x 25 clusters)
3. `/Users/Dmitrij/Documents/нэп мп/output/agent3_ozon_products.json` — 124 products, stocks, warehouses
4. `/Users/Dmitrij/Documents/нэп мп/output/agent1_sales_analysis.json` — sales, ABC, cancellations, top30 products

---

## TASK 1: Logistics Audit

### Key Metrics
- **Current locality**: 16% (84% non-local routes)
- **Total routes**: 5,977
- **Period**: 12.02.2026 - 11.03.2026 (28 days)

### Cluster Overpay Summary (shipment + delivery combined)
| Cluster | Shipment Overpay | Delivery Overpay | TOTAL | Priority |
|---------|-----------------|-----------------|-------|----------|
| Москва, МО | 86,565 | 106,013 | **192,578** | CRITICAL |
| СПб и СЗО | 66,683 | 47,199 | **113,882** | CRITICAL |
| Ростов | 43,082 | 11,490 | **54,572** | HIGH |
| Казань | 39,463 | 6,599 | **46,062** | HIGH |
| Воронеж | 35,876 | 20,663 | **56,539** | HIGH |
| Екатеринбург | 26,712 | 27,387 | **54,099** | HIGH |
| Самара | 26,803 | 23,019 | **49,822** | HIGH |
| Невинномысск | 24,373 | 16,633 | **41,006** | MEDIUM |
| Тюмень | 20,664 | 17,042 | **37,706** | MEDIUM |
| Краснодар | 18,456 | 26,858 | **45,314** | HIGH |
| Уфа | 4,051 | 30,449 | **34,500** | MEDIUM |
| Красноярск | 309 | 29,821 | **30,130** | MEDIUM |
| Ярославль | 9,091 | 29,735 | **38,826** | MEDIUM |
| Пермь | 17,806 | 12,532 | **30,338** | MEDIUM |
| Саратов | 11,162 | 27,151 | **38,313** | MEDIUM |
| Новосибирск | 13,024 | 11,817 | **24,841** | LOW |
| Оренбург | 16,456 | 8,142 | **24,598** | LOW |
| Омск | 13,446 | 8,256 | **21,702** | LOW |
| Беларусь | 9,522 | 14,686 | **24,208** | LOW |
| Тверь | 7,526 | 8,545 | **16,071** | LOW |
| Махачкала | 6,127 | 11,666 | **17,793** | LOW |
| Астана | 6,933 | 5,604 | **12,537** | LOW |
| Алматы | 5,118 | 3,316 | **8,434** | LOW |
| Дальний Восток | 3,151 | 7,776 | **10,927** | LOW |
| Красноярск | 309 | 29,821 | **30,130** | MEDIUM |
| Калининград | 0 | 0 | **0** | NONE |

### Total Overpay (Top-20 products): 260,715 rubles/28 days
### Expected Savings with Redistribution: 156,429 rubles (60% reduction)

---

## TASK 2: FBO Optimization

### Current Warehouse Distribution (top warehouses by free_to_sell)
| Warehouse | Free to Sell | Items | Cluster |
|-----------|-------------|-------|---------|
| САМАРА_РФЦ | 2,028 | 16 | Самара |
| НЕВИННОМЫССК_РФЦ | 1,764 | 22 | Невинномысск |
| Новосибирск_РФЦ | 1,461 | 19 | Новосибирск |
| СПБ_КОЛПИНО_РФЦ | 1,080 | 4 | СПб |
| Санкт_Петербург_РФЦ | 1,066 | 31 | СПб |
| САРАТОВ_РФЦ | 1,052 | 13 | Саратов |
| АЛМАТЫ_2_РФЦ | 1,036 | 18 | Алматы |
| ОМСК_РФЦ | 972 | 15 | Омск |
| АСТАНА_РФЦ | 915 | 13 | Астана |
| СПБ_БУГРЫ_РФЦ | 847 | 22 | СПб |
| Екатеринбург_РФЦ | 741 | 15 | Екатеринбург |
| СОФЬИНО_РФЦ | 705 | 16 | Москва |
| АДЫГЕЙСК_РФЦ | 648 | 10 | Краснодар |
| Ростов_на_Дону_РФЦ | 640 | 13 | Ростов |
| ХАБАРОВСК_2_РФЦ | 580 | 16 | Дальний Восток |

**Total free_to_sell**: 24,461 units across 66 warehouses

### Problem: Mismatch Between Demand and Stock
- Moscow cluster demand is ~31% of total (largest), but СОФЬИНО_РФЦ has only 705 units
- Самара has 2,028 units but only ~2.6% of top-20 demand
- Алматы has 1,036 units but <1% of total demand
- Астана has 915 units but <1% of total demand

### Recommended Distribution Strategy
Priority clusters for stock increase (by combined overpay):
1. **Москва** — needs 3x more stock (demand 31%, stock ~3%)
2. **СПб** — already has 3 warehouses (2,993 total) but still 113K overpay
3. **Ростов** — 54.5K overpay, needs more local stock
4. **Воронеж** — 56.5K overpay, critical underfill
5. **Казань** — 46K overpay, needs dedicated supply
6. **Екатеринбург** — 54K overpay despite having a warehouse

### Expected Impact
- Target locality: from 16% to >50% (3x improvement)
- Overpay reduction: 156,429 rub/month (-60%)
- Annual savings projection: ~1,877,148 rubles

---

## TASK 3: Stock Management

### Critical Stock Issues
**26 zero-stock products** (need URGENT replenishment):
1. гейнер_бисквит
2. гейнер_клубничный_йогурт
3. Витамин D3_10000 (ABC: A, revenue 617K!)
4. йохимбин_60капсул
5. магний_b6_90_caps1
6. bcaa + L-карнитин (ABC: A, revenue 530K!)
7. протеин_йогурт_земляника_2
8. комбо_ваниль_креатин_300_1
9. протеин_2шт_шоколад_банан_2
10. протеин_капучино_2

**14 low-stock products** (1-9 units, will sell out in 1-3 days):
- комбо_шоколад_2: 1 unit (ABC: A, revenue 1.17M!)
- молочный_коктейль_банан: 1 unit (ABC: A, revenue 813K!)
- креатин300_маракуйя: 8 units (ABC: A, revenue 904K!)
- креатин_900: 9 units
- Морской_коллаген: 2 units (ABC: A, revenue 457K!)

### Urgency Classification
**RED (0 stock, ABC-A)**: Витамин D3_10000 (1,761 orders/28d), bcaa + L-карнитин (1,373 orders/28d)
**RED (1-2 stock, ABC-A)**: комбо_шоколад_2, молочный_коктейль_банан, Морской_коллаген
**ORANGE (1-9 stock, ABC-A)**: креатин300_маракуйя (2,182 orders/28d!), креатин_900

### Turnover & Safety Stock Calculations (for output)
For each top product, calculate:
- Daily demand = orders_28d / 28
- Lead time assumed = 7 days (FBO receiving)
- Safety stock = daily_demand * 1.5 (safety factor)
- Reorder point = (daily_demand * lead_time) + safety_stock
- 2-week supply = daily_demand * 14
- 4-week supply = daily_demand * 28

---

## TASK 4: Cancellation Analysis

### Current State
- **Overall rate**: 13.57% (9,207 cancellations / 67,856 orders)
- **Target**: <8%
- **Industry benchmark**: Ozon sports nutrition ~5-8%

### Top Cancellation Products
| Product | Orders | Cancelled | Cancel % | Revenue |
|---------|--------|-----------|----------|---------|
| протеин_3шт_шоколад_банан_клубника | 121 | 48 | **39.7%** | 800K |
| Морской_коллаген | 1,513 | 369 | **24.4%** | 457K |
| creatine_300gr | 10,954 | 2,510 | **22.9%** | 4.34M |
| молочный_коктейль_банан | 487 | 86 | **17.7%** | 813K |
| комбо_клубника_креатин_200 | 539 | 93 | **17.3%** | 1.66M |
| bcaa + L-карнитин | 1,373 | 216 | **15.7%** | 531K |
| креатин300_маракуйя | 2,182 | 303 | **13.9%** | 904K |
| протеин_пакет_банан_2 | 462 | 62 | **13.4%** | 967K |
| creatine_300g1+1 | 1,180 | 156 | **13.2%** | 1.49M |
| протеин_шокмол24 | 382 | 48 | **12.6%** | 970K |

### Root Cause Analysis
1. **Stock-outs causing delivery delays** — creatine_300gr has massive demand (10,954 orders) but non-local delivery increases wait time, leading to cancellations
2. **39.7% cancel rate on 3-pack combo** — likely pricing/impulse buy regret on expensive combo (6,608 rub avg)
3. **Морской коллаген 24.4%** — only 2 units left in stock, likely "out of stock" cancellations
4. **Low-price items with high volume** — creatine 300g at 396 rub average, impulse buys cancel more
5. **Non-local delivery delays** — 84% non-local routes mean 3-7 day extra delivery time

### Action Plan to Reduce to <8%
1. Fix stock-outs for top-cancelled items (immediate impact on collаgen, BCAA, combos)
2. Redistribute creatine_300gr to local clusters (781.8 units to Moscow alone)
3. Review pricing on 3-pack combo (39.7% cancels = pricing issue)
4. Improve delivery speed via FBO redistribution (Task 2)
5. Add "fast delivery" badge by ensuring local stock in top clusters

---

## TASK 5: 2-Week Supply Table

### Structure
Top-30 SKU x 25 clusters with quantity allocation based on demand_14d distribution from agent2_top20_supply_data.json.

For SKUs 21-30 (not in top-20 supply data), calculate proportional distribution using Moscow ~31%, SPb ~6.5%, Ростов ~5%, etc. based on observed patterns.

### Auto-Replenishment Triggers
For each SKU:
- **Reorder point** = (daily_demand * 7) + safety_stock
- **Safety stock** = daily_demand * 3 (3-day buffer)
- **Auto-replenishment quantity** = 14-day demand

### KPIs
- Locality target: >50% (from 16%)
- Cancellation target: <8% (from 13.57%)
- Stock-out products: 0 (from 26)
- Overpay reduction: >60%
- Average delivery time: <3 days (estimate from locality improvement)

---

## Execution Plan (when plan mode deactivated)

### Step 1: Write Python script
Create a Python script at `/Users/Dmitrij/Documents/нэп мп/scripts/generate_coo_analysis.py` that:
- Reads all 4 input JSON files
- Computes all metrics described above
- Generates the output JSON with the exact schema requested
- Saves to output/expert_coo_analysis.json

### Step 2: Alternative - Direct JSON generation
If simpler, directly construct the JSON output using the data already collected and write it.

### Recommended approach: Step 2 (direct JSON)
Since all data is already extracted and computations are straightforward arithmetic, generate the JSON directly. No need for a script.

### Output JSON Schema (from user request)
```json
{
  "logistics_audit": {
    "current_locality_pct": 16.0,
    "total_overpay_rub": ...,
    "top_overpay_clusters": [...],
    "top_overpay_products": [...],
    "underfilled_clusters": [...],
    "overfilled_clusters": [...]
  },
  "fbo_optimization": {
    "current_distribution": {...},
    "recommended_distribution": {...},
    "expected_locality_pct": ...,
    "expected_savings_rub": ...,
    "priority_actions": [...]
  },
  "stock_management": {
    "zero_stock_urgent": [...],
    "low_stock_warning": [...],
    "turnover_days": {...},
    "safety_stock": {...},
    "replenishment_2week": {...},
    "replenishment_4week": {...}
  },
  "cancellation_reduction": {
    "current_rate_pct": 13.57,
    "target_rate_pct": 8.0,
    "top_cancelled_products": [...],
    "root_causes": [...],
    "action_plan": [...]
  },
  "supply_table_2weeks": {
    "sku_count": 30,
    "cluster_count": 25,
    "table": [...]
  },
  "operational_kpis": {
    "locality_target": ">50%",
    "cancellation_target": "<8%",
    "stockout_target": 0,
    "overpay_reduction_target": ">60%",
    "sla_per_cluster": {...}
  }
}
```

### Estimated Size
The output JSON will be approximately 2000-3000 lines given 30 SKUs x 25 clusters in the supply table.

### Time to Execute
~5 minutes to write the complete JSON output file once plan mode is deactivated.
