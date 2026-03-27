# SEO Expert Analysis Plan - Soul Way Ozon

## Status: READY TO EXECUTE

## Data Sources Read
- `/Users/Dmitrij/Documents/нэп мп/output/agent6_seo_analysis.json` - SEO positions, hidden potential, top products
- `/Users/Dmitrij/Documents/нэп мп/output/agent1_sales_analysis.json` - Sales ABC analysis, revenue, orders
- `/Users/Dmitrij/Documents/нэп мп/artifacts/cards.json` - WB card data (22,919 lines, detailed cards with characteristics)
- `/Users/Dmitrij/Documents/нэп мп/artifacts/all_cards_data_ooo.json` - OOO Bionovacia card data (10,010 lines)
- XLSX duplicates files exist at `/Users/Dmitrij/Documents/нэп мп/output/НЭП_Дубли_SoulWay+OOO_v8.xlsx`

## Execution Plan

### Step 1: Position Analysis (from agent6_seo_analysis.json)
Generate `position_analysis` section:

**Key Findings Already Extracted:**
- 221 total products, 178 with position data
- Position distribution: top10=25, 11-20=7, 21-50=46, 51-100=77, 100+=23, no_data=43
- CRITICAL: 25 products show position=1 but have 0 orders and minimal impressions (1-27). This means position=1 is ANOMALOUS -- likely low-competition long-tail queries, not real top positions
- Real high-performers by orders are at positions 51-96 (hidden_potential section)

**Top 20 Products by Revenue and Their Positions:**
1. Протеин шоколад 900г -- revenue 9.27M, position DATA NEEDED (not in top20_best_positions because position>1)
2. Креатин моногидрат 300г -- revenue 4.34M, position ~31 (category avg for Креатин)
3. Протеин банан 900г -- revenue 3.83M
4. Протеин клубника 900г -- revenue 3.61M
5. Протеин черничный йогурт 900г -- revenue 3.39M
6. Протеин ваниль 900г -- revenue 2.67M
7. Набор клубника+креатин200 -- revenue 1.66M
8. Креатин 300г 3 банки -- revenue 1.49M
9. Комбо шоколад+креатин200 -- revenue 1.17M
10. Протеин шоколад молочный 24г -- revenue 0.97M

From hidden_potential section, revenue-generating items positions:
- Stress Protect: pos 55, 1600 orders, 572K
- Коллаген+гиалуроновая: pos 54, 1513 orders, 457K
- Beauty Complex: pos 53, 1180 orders, 465K
- Витамин D3+K2: pos 76, 846 orders, 328K
- Цинк цитрат: pos 72, 802 orders, 203K
- Магний B6: pos 96, 735 orders, 176K
- Brain Booster: pos 54, 717 orders, 276K
- Multi Complex: pos 70, 688 orders, 244K
- Омега 3 (bionordiq): pos 74, 657 orders, 258K
- Only Women's: pos 61, 653 orders, 237K

**Correlation Analysis:**
- Category "Креатин" (avg pos 31.3) = 18,196 orders -- BEST ratio
- "Витаминно-минеральный комплекс" (avg pos 50.9) = 11,529 orders
- "Протеин" (avg pos 54.6) = 14,735 orders
- "Витамины" (avg pos 86.4) = 5,446 orders -- high position, moderate orders
- "Витаминный комплекс" (avg pos 86.9) = 4,245 orders
- Pattern: every 10 positions closer to top = ~20-30% more orders

**Uplift Potential:**
- Moving avg position from 55 to 20 for "Витаминно-мин. комплекс" (18 products, 11,529 orders) could yield ~2x orders = +11,500 orders
- Moving "Протеин" from 55 to 25 could yield ~1.5-2x = +7,000-14,000 orders
- Moving "Витамины" from 86 to 30 could yield ~3x = +10,000 orders
- Total potential uplift: 28,000-36,000 additional orders per month

**Products at 100+ positions:**
- БАД для иммунитета (pos 120.5) -- 47 orders, low potential, niche
- Магний (pos 144) -- 28 orders, consider deprioritizing
- Препарат для суставов (pos 157.7) -- 359 orders, worth optimizing
- БАД для костей и суставов (pos 172.7) -- 938 orders! HIGH PRIORITY to optimize
- B-комплекс (pos 100) -- 334 orders, worth optimizing
- Витамин D3 2000ME duplicate (pos 116) -- 243 orders, duplicate issue

### Step 2: Card Quality Audit (from cards.json)
- Title analysis: many titles are SHORT and miss key SEO words
  - Example: "Протеин для похудения сывороточный без сахара" -- good length, has commercial intent keywords
  - Example: "Протеин сывороточный Soul Way со вкусом бисквита / 1020 гр 34 порций" -- too template-like
- Descriptions: range from 500 to 2000+ chars. Most are adequate length
- Photos: 8-14 photos per card -- GOOD
- Characteristics: filled but some missing "Назначение спортивного питания" on key items
- ISSUE: Brand name "Soul Way" takes up title space that could be used for SEO keywords

### Step 3: NEP Coverage Scoring
For top 10 products by revenue, scoring:
- Decompose each title/characteristics/description into word tokens
- Match against likely search queries for the category
- Score 0-10 per zone
- Identify Camp A (photo coverage >=7) vs Camp B (<7)

Key semantic queries for ПРОТЕИН category:
"протеин сывороточный", "whey protein", "протеин для набора массы", "протеин для похудения", "белковый коктейль", "протеиновый коктейль", "спортивное питание", "wpc 80", "без сахара", "для мышц"

Key queries for КРЕАТИН:
"креатин моногидрат", "creatine monohydrate", "креатин порошок", "для набора массы", "спортивное питание", "для силы", "для выносливости"

### Step 4: Anti-Duplicate Analysis
Based on sales data, clear internal duplicate clusters:
- **Протеин шоколад cluster:** SKU 1846387711 (9.27M) + 2543624387 (970K) + 1781111189 (433K) + 1735645775 (416K) -- 4 SKUs competing
- **Протеин банан cluster:** SKU 1846387589 (3.83M) + 1845272577 (967K)
- **Протеин клубника cluster:** SKU 1852787684 (3.61M) + комбо items
- **Креатин 300г cluster:** SKU 1804654137 (4.34M) + flavored variants (маракуйя 903K, клубника 245K, лимон 243K, апельсин)
- **Витамин D3 duplicates:** 10000ME + 5000ME + 2000ME (two SKUs!) + D3+K2
- **Омега 3 duplicates:** Soul Way 90 caps + 300 caps + bionordiq Omega

### Step 5: SEO Action Plan (Priority Order)
1. **P1 - Креатин 300г (pos ~31, 4.34M revenue)** -- already decent position, optimize title for broader keywords
2. **P2 - Протеин шоколад 900г (est pos ~45-55, 9.27M revenue)** -- TOP revenue, moderate position, highest ROI
3. **P3 - БАД для костей и суставов (pos 172.7, 938 orders)** -- massive gap between orders and position
4. **P4 - Витамины cluster (pos 86-96)** -- 10,000+ orders at bad positions
5. **P5 - Stress Protect (pos 55, 1600 orders)** -- high orders, needs title & description SEO push
6. **P6 - Resolve duplicates** -- Протеин шоколад has 4 competing SKUs, cannibalization
7. **P7 - Beauty Complex/Brain Booster** -- well-selling bionordiq items at pos 53-54
8. **P8 - Протеин комбо наборы** -- differentiate from single protеин cards

## Output File Structure
Write to `/Users/Dmitrij/Documents/нэп мп/output/expert_seo_analysis.json` with full JSON structure as specified in the task.

## Execution Steps
1. Parse all position data from agent6 and match with revenue from agent1
2. Calculate position-revenue correlation coefficient
3. Score top 10 products on НЭП coverage (title/chars/desc/photo)
4. Build duplicate clusters from product names and categories
5. Create prioritized action plan with specific title recommendations
6. Write final JSON output
