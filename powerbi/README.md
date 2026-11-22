# Power BI handoff

The working dashboard is the Streamlit app. This folder supplies an additional
Power BI implementation specification, executable Power Query M, DAX measures
and a theme. No `.pbix` or `.pbit` file is claimed or fabricated.

## Import the fact table

1. Run `portfolio build --source full`.
2. In Power BI Desktop, create a text parameter `RetailParquetPath` pointing to the
   absolute path of `artifacts/full/retail_lines.parquet` on your computer.
3. Create a blank query, name it `FactRetail`, open Advanced Editor and paste
   `FactRetail.pq`. The query adds a date column while preserving line timestamps.
4. Create the `Date` calculated table from `measures.dax`. Mark it as the date table.
5. Relate `Date[Date]` one-to-many to `FactRetail[OrderDate]`, single direction.
6. Add the measures from `measures.dax`. Import `theme.json`.

Power Query M is provided as a Desktop handoff. It has not been executed in Power
BI Desktop in this environment. The underlying Parquet/CSV data and Python/SQL
metrics have been executed and checked.

## Alternative: CSV marts

Import the daily, monthly, products, RFM and cohorts CSVs from `artifacts/full/`
using Get Data > Text/CSV. These are independent aggregates. Do not join all marts
directly together or sum repeated cohort sizes. The fact-table model above is
preferred for cross-filtered invoice counts and customer measures.

## Report pages

| Page | Visuals | Slicers |
| --- | --- | --- |
| Trading overview | Net revenue, gross sales, credit ratio, positive orders, monthly line | Date, country |
| Product review | Net revenue / credits by stock code, top items table | Date, country, stock code |
| Customer activity | RFM segment counts, cohort matrix | Whole-run analysis, explicit snapshot |
| Data quality | Input/excluded/retained rows and unidentified sales share | Source run |

## Reconciliation checklist

- Clear all filters and compare full-run totals against `retail_summary.json`.
- Gross minus credits must equal net. Do not silently drop negative quantities.
- Format currency to two decimals, percentages to one or two decimal places.
- Do not use a simple average of monthly ratios for a whole-period ratio.
- Month-level comparisons exclude the final observed month or use matched dates.
- RFM/cohort files are whole-run snapshots and are not recomputed by fact-table slicers.
- Net revenue is a source-recorded measure, not profit or VAT-adjusted accounting revenue.
