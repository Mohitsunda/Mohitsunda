-- DuckDB SQL. fact_retail contains all retained positive-price financial lines.
-- Cancellation/negative lines stay in net revenue; orders count positive invoices only.
CREATE OR REPLACE VIEW mart_retail_daily AS
SELECT CAST(invoice_date AS DATE) AS order_date, country,
       SUM(CASE WHEN line_value > 0 THEN line_value ELSE 0 END) AS gross_sales_gbp,
       -SUM(CASE WHEN line_value < 0 THEN line_value ELSE 0 END) AS credits_gbp,
       SUM(line_value) AS net_revenue_gbp,
       COUNT(DISTINCT CASE WHEN line_value > 0 THEN invoice_no END) AS orders,
       SUM(CASE WHEN line_value > 0 AND customer_id IS NULL THEN line_value ELSE 0 END)
           AS unidentified_sales_gbp
FROM fact_retail
GROUP BY ALL;

CREATE OR REPLACE VIEW mart_retail_monthly AS
WITH months AS (
    SELECT DATE_TRUNC('month', order_date)::DATE AS month,
           SUM(gross_sales_gbp) AS gross_sales_gbp, SUM(credits_gbp) AS credits_gbp,
           SUM(net_revenue_gbp) AS net_revenue_gbp, SUM(orders) AS orders
    FROM mart_retail_daily GROUP BY 1
)
SELECT *,
       gross_sales_gbp / NULLIF(orders, 0) AS gross_order_value_gbp,
       net_revenue_gbp / NULLIF(LAG(net_revenue_gbp) OVER (ORDER BY month), 0) - 1
           AS net_revenue_mom,
       month < DATE_TRUNC('month', (SELECT MAX(invoice_date) FROM fact_retail))
           AS complete_month
FROM months;

CREATE OR REPLACE VIEW mart_retail_products AS
SELECT stock_code, MAX(description) AS description,
       SUM(CASE WHEN line_value > 0 THEN quantity ELSE 0 END) AS units_sold,
       SUM(line_value) AS net_revenue_gbp,
       -SUM(CASE WHEN line_value < 0 THEN line_value ELSE 0 END) AS credits_gbp
FROM fact_retail GROUP BY stock_code;

-- RFM uses identified customers' positive invoices, not credit notes.
CREATE OR REPLACE VIEW mart_retail_rfm AS
WITH snapshot AS (SELECT MAX(invoice_date)::DATE + 1 AS as_of_date FROM fact_retail),
base AS (
    SELECT customer_id,
           DATE_DIFF('day', MAX(invoice_date)::DATE, (SELECT as_of_date FROM snapshot))
               AS recency_days,
           COUNT(DISTINCT invoice_no) AS frequency,
           SUM(line_value) AS monetary_gbp
    FROM fact_retail WHERE customer_id IS NOT NULL AND line_value > 0
    GROUP BY customer_id
)
SELECT *, CASE
    WHEN recency_days <= 90 AND frequency >= 3 THEN 'Loyal active'
    WHEN recency_days <= 90 THEN 'Recent occasional'
    WHEN frequency >= 3 THEN 'Loyal lapsed'
    ELSE 'Occasional lapsed' END AS segment
FROM base;

-- This is purchase activity retention, not contractual churn.
CREATE OR REPLACE VIEW mart_retail_cohorts AS
WITH activity AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month', invoice_date)::DATE AS active_month
    FROM fact_retail WHERE customer_id IS NOT NULL AND line_value > 0
), labelled AS (
    SELECT *, MIN(active_month) OVER (PARTITION BY customer_id) AS cohort_month FROM activity
), counts AS (
    SELECT cohort_month, DATE_DIFF('month', cohort_month, active_month) AS month_index,
           COUNT(*) AS active_customers
    FROM labelled GROUP BY 1, 2
)
SELECT *, active_customers * 1.0 /
       MAX(CASE WHEN month_index = 0 THEN active_customers END)
           OVER (PARTITION BY cohort_month) AS retention
FROM counts ORDER BY cohort_month, month_index;
