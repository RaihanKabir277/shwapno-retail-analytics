# Databricks notebook source
# MAGIC %pip install openpyxl

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import pandas as pd

base_path = "/Volumes/data_analysis_retail/source_data/raw/Gap_Analysis/"

outlet_df = pd.read_excel(base_path + "Retail_Assessment_Demo_Data.xlsx", sheet_name="Outlet Master", skiprows=1)
sales_df  = pd.read_excel(base_path + "Retail_Assessment_Demo_Data.xlsx", sheet_name="Daily Sales",   skiprows=1)
gap_df    = pd.read_excel(base_path + "Retail_Assessment_Demo_Data.xlsx", sheet_name="Gap Analysis",  skiprows=1)

# ── Clean gap_df ──────────────────────────────────────────────────
# Drop rows where Outlet_ID is null or doesn't start with "OT"
gap_df = gap_df[
    gap_df["Outlet_ID"].notna() &
    gap_df["Outlet_ID"].astype(str).str.startswith("OT")
]

# Same safety filter for outlet and sales just in case
outlet_df = outlet_df[
    outlet_df["Outlet_ID"].notna() &
    outlet_df["Outlet_ID"].astype(str).str.startswith("OT")
]

sales_df = sales_df[
    sales_df["Outlet_ID"].notna() &
    sales_df["Outlet_ID"].astype(str).str.startswith("OT")
]

# Register as Spark temp views
spark.createDataFrame(outlet_df).createOrReplaceTempView("v_outlet_master")
spark.createDataFrame(sales_df).createOrReplaceTempView("v_daily_sales")
spark.createDataFrame(gap_df).createOrReplaceTempView("v_gap_analysis")

# Verify counts
print(f"✅ Outlets : {len(outlet_df)} rows")
print(f"✅ Sales   : {len(sales_df)} rows")
print(f"✅ Gap     : {len(gap_df)} rows  ← should be exactly 50")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.outlet_gap_summary AS
# MAGIC SELECT
# MAGIC   g.Outlet_ID,
# MAGIC   g.Location                                                              AS region,
# MAGIC   g.Store_Type                                                            AS store_type,
# MAGIC   g.Target_Sales                                                          AS target_sales,
# MAGIC   g.Actual_Sales                                                          AS actual_sales,
# MAGIC   g.Sales_Gap                                                             AS sales_gap,
# MAGIC   ROUND(
# MAGIC     ((g.Actual_Sales - g.Target_Sales) / g.Target_Sales) * 100, 2
# MAGIC   )                                                                       AS gap_pct,
# MAGIC   CASE
# MAGIC     WHEN ((g.Actual_Sales - g.Target_Sales) / g.Target_Sales) * 100 < -20 THEN 'Critical'
# MAGIC     WHEN ((g.Actual_Sales - g.Target_Sales) / g.Target_Sales) * 100 < -10 THEN 'At Risk'
# MAGIC     WHEN ((g.Actual_Sales - g.Target_Sales) / g.Target_Sales) * 100 < 0   THEN 'Slightly Under'
# MAGIC     ELSE                                                                        'On/Above Target'
# MAGIC   END                                                                     AS performance_tier
# MAGIC FROM v_gap_analysis g;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT performance_tier, COUNT(*) AS outlet_count
# MAGIC FROM data_analysis_retail.gold.outlet_gap_summary
# MAGIC GROUP BY performance_tier
# MAGIC ORDER BY performance_tier;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.region_performance AS
# MAGIC SELECT
# MAGIC   g.Location                                          AS region,
# MAGIC   COUNT(g.Outlet_ID)                                  AS total_outlets,
# MAGIC   SUM(g.Target_Sales)                                 AS total_target,
# MAGIC   SUM(g.Actual_Sales)                                 AS total_actual,
# MAGIC   SUM(g.Sales_Gap)                                    AS total_gap,
# MAGIC   ROUND(
# MAGIC     (SUM(g.Actual_Sales) - SUM(g.Target_Sales))
# MAGIC     / SUM(g.Target_Sales) * 100, 2
# MAGIC   )                                                   AS region_gap_pct,
# MAGIC   COUNT(CASE WHEN g.`Gap_%` < 0 THEN 1 END)          AS outlets_missing_target
# MAGIC FROM v_gap_analysis g
# MAGIC GROUP BY g.Location;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.daily_sales_trend AS
# MAGIC SELECT
# MAGIC   s.Date,
# MAGIC   s.Outlet_ID,
# MAGIC   o.Location      AS region,
# MAGIC   o.Store_Type    AS store_type,
# MAGIC   s.Sales_Amount  AS daily_sales,
# MAGIC   s.Transactions  AS transactions,
# MAGIC   s.Customers     AS customers
# MAGIC FROM v_daily_sales s
# MAGIC JOIN v_outlet_master o ON s.Outlet_ID = o.Outlet_ID;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Outlet master gold layer

# COMMAND ----------

import pandas as pd

base_path = "/Volumes/data_analysis_retail/source_data/raw/Outlet_master/"

outlet_df = pd.read_excel(base_path + "Retail_Assessment_Demo_Data.xlsx", sheet_name="Outlet Master", skiprows=1)
sales_df  = pd.read_excel(base_path + "Retail_Assessment_Demo_Data.xlsx", sheet_name="Daily Sales",   skiprows=1)

# Filter junk rows — only real outlet IDs
outlet_df = outlet_df[outlet_df["Outlet_ID"].notna() & outlet_df["Outlet_ID"].astype(str).str.startswith("OT")]
sales_df  = sales_df[sales_df["Outlet_ID"].notna()  & sales_df["Outlet_ID"].astype(str).str.startswith("OT")]

spark.createDataFrame(outlet_df).createOrReplaceTempView("v_outlet_master")
spark.createDataFrame(sales_df).createOrReplaceTempView("v_daily_sales")

print(f"✅ Outlets : {len(outlet_df)} rows — should be 50")
print(f"✅ Sales   : {len(sales_df)} rows — should be 18,250")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.outlet_top_performers AS
# MAGIC SELECT
# MAGIC   o.Outlet_ID,
# MAGIC   o.Location,
# MAGIC   o.Store_Type,
# MAGIC   o.Target_Sales,
# MAGIC   ROUND(SUM(s.Sales_Amount), 2)                                        AS actual_sales,
# MAGIC   ROUND(SUM(s.Sales_Amount) - o.Target_Sales, 2)                      AS sales_gap,
# MAGIC   ROUND((SUM(s.Sales_Amount) - o.Target_Sales) / o.Target_Sales * 100, 2) AS gap_pct,
# MAGIC   RANK() OVER (ORDER BY SUM(s.Sales_Amount) DESC)                     AS sales_rank,
# MAGIC   CASE
# MAGIC     WHEN (SUM(s.Sales_Amount) - o.Target_Sales) / o.Target_Sales * 100 >= 20 THEN 'Star'
# MAGIC     WHEN (SUM(s.Sales_Amount) - o.Target_Sales) / o.Target_Sales * 100 >= 0  THEN 'On Target'
# MAGIC     WHEN (SUM(s.Sales_Amount) - o.Target_Sales) / o.Target_Sales * 100 >= -20 THEN 'Underperforming'
# MAGIC     ELSE 'Critical'
# MAGIC   END AS performance_label
# MAGIC FROM v_outlet_master o
# MAGIC JOIN v_daily_sales s ON o.Outlet_ID = s.Outlet_ID
# MAGIC GROUP BY o.Outlet_ID, o.Location, o.Store_Type, o.Target_Sales;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.outlet_monthly_trend AS
# MAGIC SELECT
# MAGIC   s.Outlet_ID,
# MAGIC   o.Location,
# MAGIC   o.Store_Type,
# MAGIC   DATE_FORMAT(s.Date, 'yyyy-MM')          AS sales_month,
# MAGIC   MONTH(s.Date)                           AS month_num,
# MAGIC   ROUND(SUM(s.Sales_Amount), 2)           AS monthly_sales,
# MAGIC   COUNT(s.Transactions)                   AS total_transactions,
# MAGIC   SUM(s.Customers)                        AS total_customers
# MAGIC FROM v_daily_sales s
# MAGIC JOIN v_outlet_master o ON s.Outlet_ID = o.Outlet_ID
# MAGIC GROUP BY s.Outlet_ID, o.Location, o.Store_Type, DATE_FORMAT(s.Date, 'yyyy-MM'), MONTH(s.Date);

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.outlet_age_performance AS
# MAGIC SELECT
# MAGIC   o.Outlet_ID,
# MAGIC   o.Location,
# MAGIC   o.Store_Type,
# MAGIC   o.Opening_Date,
# MAGIC   DATEDIFF(TO_DATE('2024-12-31'), TO_DATE(o.Opening_Date)) / 365.0   AS outlet_age_years,
# MAGIC   ROUND(
# MAGIC     DATEDIFF(TO_DATE('2024-12-31'), TO_DATE(o.Opening_Date)) / 365.0
# MAGIC   )                                                                    AS age_years_rounded,
# MAGIC   CASE
# MAGIC     WHEN DATEDIFF(TO_DATE('2024-12-31'), TO_DATE(o.Opening_Date)) / 365.0 < 2  THEN 'New (< 2 yrs)'
# MAGIC     WHEN DATEDIFF(TO_DATE('2024-12-31'), TO_DATE(o.Opening_Date)) / 365.0 < 5  THEN 'Growing (2–5 yrs)'
# MAGIC     ELSE                                                                              'Mature (5+ yrs)'
# MAGIC   END                                                                  AS age_category,
# MAGIC   o.Target_Sales,
# MAGIC   ROUND(SUM(s.Sales_Amount), 2)                                        AS actual_sales,
# MAGIC   ROUND((SUM(s.Sales_Amount) - o.Target_Sales) / o.Target_Sales * 100, 2) AS gap_pct
# MAGIC FROM v_outlet_master o
# MAGIC JOIN v_daily_sales s ON o.Outlet_ID = s.Outlet_ID
# MAGIC GROUP BY o.Outlet_ID, o.Location, o.Store_Type, o.Opening_Date, o.Target_Sales;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'top_performers'    AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.outlet_top_performers
# MAGIC UNION ALL
# MAGIC SELECT 'monthly_trend'     AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.outlet_monthly_trend
# MAGIC UNION ALL
# MAGIC SELECT 'age_performance'   AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.outlet_age_performance;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Employee KPI

# COMMAND ----------

import pandas as pd

base_path = "/Volumes/data_analysis_retail/source_data/raw/Employee_KPI/"
file = "Retail_Assessment_Demo_Data (1).xlsx"

emp_df    = pd.read_excel(base_path + file, sheet_name="Employee KPI",  skiprows=1)
outlet_df = pd.read_excel(base_path + file, sheet_name="Outlet Master", skiprows=1)
sales_df  = pd.read_excel(base_path + file, sheet_name="Daily Sales",   skiprows=1)

# Clean all three — keep only real rows
emp_df    = emp_df[emp_df["Employee_ID"].notna() & emp_df["Employee_ID"].astype(str).str.startswith("EMP")]
outlet_df = outlet_df[outlet_df["Outlet_ID"].notna() & outlet_df["Outlet_ID"].astype(str).str.startswith("OT")]
sales_df  = sales_df[sales_df["Outlet_ID"].notna()  & sales_df["Outlet_ID"].astype(str).str.startswith("OT")]

spark.createDataFrame(emp_df).createOrReplaceTempView("v_employee_kpi")
spark.createDataFrame(outlet_df).createOrReplaceTempView("v_outlet_master")
spark.createDataFrame(sales_df).createOrReplaceTempView("v_daily_sales")

print(f"✅ Employees : {len(emp_df)} rows  — should be 347")
print(f"✅ Outlets   : {len(outlet_df)} rows — should be 50")
print(f"✅ Sales     : {len(sales_df)} rows — should be 18,250")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.kpi_by_outlet AS
# MAGIC SELECT
# MAGIC   e.Outlet_ID,
# MAGIC   o.Location,
# MAGIC   o.Store_Type,
# MAGIC   COUNT(e.Employee_ID)                            AS total_employees,
# MAGIC   ROUND(AVG(e.KPI_Achievement_Pct), 2)           AS avg_kpi_achievement,
# MAGIC   ROUND(AVG(e.KPI_Target), 2)                    AS avg_kpi_target,
# MAGIC   ROUND(AVG(e.KPI_Achievement_Pct) - AVG(e.KPI_Target), 2) AS kpi_gap,
# MAGIC   CASE
# MAGIC     WHEN AVG(e.KPI_Achievement_Pct) >= 100 THEN 'Exceeding'
# MAGIC     WHEN AVG(e.KPI_Achievement_Pct) >= 80  THEN 'On Track'
# MAGIC     WHEN AVG(e.KPI_Achievement_Pct) >= 60  THEN 'At Risk'
# MAGIC     ELSE                                         'Critical'
# MAGIC   END AS kpi_status
# MAGIC FROM v_employee_kpi e
# MAGIC JOIN v_outlet_master o ON e.Outlet_ID = o.Outlet_ID
# MAGIC GROUP BY e.Outlet_ID, o.Location, o.Store_Type;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.employee_performance AS
# MAGIC SELECT
# MAGIC   e.Employee_ID,
# MAGIC   e.Outlet_ID,
# MAGIC   o.Location,
# MAGIC   e.Position,
# MAGIC   e.KPI_Target,
# MAGIC   e.KPI_Achievement_Pct,
# MAGIC   ROUND(e.KPI_Achievement_Pct - e.KPI_Target, 2) AS kpi_vs_target,
# MAGIC   RANK() OVER (ORDER BY e.KPI_Achievement_Pct DESC) AS rank_top,
# MAGIC   RANK() OVER (ORDER BY e.KPI_Achievement_Pct ASC)  AS rank_bottom,
# MAGIC   CASE
# MAGIC     WHEN e.KPI_Achievement_Pct >= 100 THEN 'Top Performer'
# MAGIC     WHEN e.KPI_Achievement_Pct >= 80  THEN 'Good'
# MAGIC     WHEN e.KPI_Achievement_Pct >= 60  THEN 'Average'
# MAGIC     ELSE                                   'Low Performer'
# MAGIC   END AS performance_label
# MAGIC FROM v_employee_kpi e
# MAGIC JOIN v_outlet_master o ON e.Outlet_ID = o.Outlet_ID;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.kpi_sales_correlation AS
# MAGIC SELECT
# MAGIC   e.Outlet_ID,
# MAGIC   o.Location,
# MAGIC   o.Store_Type,
# MAGIC   ROUND(AVG(e.KPI_Achievement_Pct), 2)  AS avg_kpi_achievement,
# MAGIC   ROUND(SUM(s.Sales_Amount), 2)          AS total_sales,
# MAGIC   o.Target_Sales,
# MAGIC   ROUND((SUM(s.Sales_Amount) - o.Target_Sales) / o.Target_Sales * 100, 2) AS sales_gap_pct
# MAGIC FROM v_employee_kpi e
# MAGIC JOIN v_outlet_master o  ON e.Outlet_ID  = o.Outlet_ID
# MAGIC JOIN v_daily_sales s    ON e.Outlet_ID  = s.Outlet_ID
# MAGIC GROUP BY e.Outlet_ID, o.Location, o.Store_Type, o.Target_Sales;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'kpi_by_outlet'        AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.kpi_by_outlet
# MAGIC UNION ALL
# MAGIC SELECT 'employee_performance'  AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.employee_performance
# MAGIC UNION ALL
# MAGIC SELECT 'kpi_sales_correlation' AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.kpi_sales_correlation;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Customer Data 

# COMMAND ----------

import pandas as pd

base_path = "/Volumes/data_analysis_retail/source_data/raw/Customer_Data/"
file = "Customer_data.xlsx"

customer_df = pd.read_excel(base_path + file, sheet_name="Customer Data", skiprows=1)

# Keep only real customer rows
customer_df = customer_df[
    customer_df["Customer_ID"].notna() &
    customer_df["Customer_ID"].astype(str).str.startswith("CUST")
]

spark.createDataFrame(customer_df).createOrReplaceTempView("v_customer_data")

print(f"✅ Customers: {len(customer_df)} rows — should be 5,000")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.customer_segments AS
# MAGIC SELECT
# MAGIC   Age_Group,
# MAGIC   Gender,
# MAGIC   COUNT(Customer_ID)                                        AS customer_count,
# MAGIC   ROUND(AVG(Purchase_Frequency), 2)                        AS avg_purchase_frequency,
# MAGIC   ROUND(AVG(Avg_Basket_Value), 2)                          AS avg_basket_value,
# MAGIC   ROUND(AVG(Purchase_Frequency * Avg_Basket_Value), 2)     AS avg_total_spend,
# MAGIC   ROUND(SUM(Purchase_Frequency * Avg_Basket_Value), 2)     AS total_segment_spend,
# MAGIC   CASE
# MAGIC     WHEN AVG(Purchase_Frequency * Avg_Basket_Value) >= 2000 THEN 'High Value'
# MAGIC     WHEN AVG(Purchase_Frequency * Avg_Basket_Value) >= 1000 THEN 'Mid Value'
# MAGIC     ELSE                                                         'Low Value'
# MAGIC   END AS segment_tier
# MAGIC FROM v_customer_data
# MAGIC GROUP BY Age_Group, Gender;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.spending_by_age AS
# MAGIC SELECT
# MAGIC   Age_Group,
# MAGIC   COUNT(Customer_ID)                                        AS customer_count,
# MAGIC   ROUND(AVG(Purchase_Frequency), 2)                        AS avg_purchase_frequency,
# MAGIC   ROUND(AVG(Avg_Basket_Value), 2)                          AS avg_basket_value,
# MAGIC   ROUND(AVG(Purchase_Frequency * Avg_Basket_Value), 2)     AS avg_total_spend,
# MAGIC   ROUND(SUM(Purchase_Frequency * Avg_Basket_Value), 2)     AS total_spend,
# MAGIC   ROUND(MIN(Purchase_Frequency * Avg_Basket_Value), 2)     AS min_spend,
# MAGIC   ROUND(MAX(Purchase_Frequency * Avg_Basket_Value), 2)     AS max_spend
# MAGIC FROM v_customer_data
# MAGIC GROUP BY Age_Group
# MAGIC ORDER BY Age_Group;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.location_purchase_patterns AS
# MAGIC SELECT
# MAGIC   Location,
# MAGIC   COUNT(Customer_ID)                                        AS customer_count,
# MAGIC   ROUND(AVG(Purchase_Frequency), 2)                        AS avg_purchase_frequency,
# MAGIC   ROUND(AVG(Avg_Basket_Value), 2)                          AS avg_basket_value,
# MAGIC   ROUND(AVG(Purchase_Frequency * Avg_Basket_Value), 2)     AS avg_total_spend,
# MAGIC   ROUND(SUM(Purchase_Frequency * Avg_Basket_Value), 2)     AS total_spend,
# MAGIC   ROUND(SUM(Purchase_Frequency * Avg_Basket_Value) /
# MAGIC     SUM(SUM(Purchase_Frequency * Avg_Basket_Value)) OVER () * 100, 2) AS spend_share_pct
# MAGIC FROM v_customer_data
# MAGIC GROUP BY Location;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'customer_segments'         AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.customer_segments
# MAGIC UNION ALL
# MAGIC SELECT 'spending_by_age'           AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.spending_by_age
# MAGIC UNION ALL
# MAGIC SELECT 'location_purchase_patterns' AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.location_purchase_patterns;

# COMMAND ----------

# MAGIC %md
# MAGIC ###  Expansion Recommendation

# COMMAND ----------

import pandas as pd

base_path = "/Volumes/data_analysis_retail/source_data/raw/Daily_Sales/"
file = "Daily_Sales.xlsx"

outlet_df = pd.read_excel(base_path + file, sheet_name="Outlet Master", skiprows=1)
sales_df  = pd.read_excel(base_path + file, sheet_name="Daily Sales",   skiprows=1)
cust_df   = pd.read_excel(base_path + file, sheet_name="Customer Data", skiprows=1)
gap_df    = pd.read_excel(base_path + file, sheet_name="Gap Analysis",  skiprows=1)

# Clean all — keep only real rows
outlet_df = outlet_df[outlet_df["Outlet_ID"].notna()   & outlet_df["Outlet_ID"].astype(str).str.startswith("OT")]
sales_df  = sales_df[sales_df["Outlet_ID"].notna()     & sales_df["Outlet_ID"].astype(str).str.startswith("OT")]
cust_df   = cust_df[cust_df["Customer_ID"].notna()     & cust_df["Customer_ID"].astype(str).str.startswith("CUST")]
gap_df    = gap_df[gap_df["Outlet_ID"].notna()         & gap_df["Outlet_ID"].astype(str).str.startswith("OT")]

spark.createDataFrame(outlet_df).createOrReplaceTempView("v_outlet_master")
spark.createDataFrame(sales_df).createOrReplaceTempView("v_daily_sales")
spark.createDataFrame(cust_df).createOrReplaceTempView("v_customer_data")
spark.createDataFrame(gap_df).createOrReplaceTempView("v_gap_analysis")

print(f"✅ Outlets   : {len(outlet_df)} rows — should be 50")
print(f"✅ Sales     : {len(sales_df)} rows — should be 18,300")
print(f"✅ Customers : {len(cust_df)} rows — should be 5,000")
print(f"✅ Gap       : {len(gap_df)} rows — should be 50")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.expansion_location_scorecard AS
# MAGIC SELECT
# MAGIC   o.Location,
# MAGIC   COUNT(DISTINCT o.Outlet_ID)                                          AS existing_outlets,
# MAGIC   ROUND(SUM(s.Sales_Amount), 2)                                        AS total_sales,
# MAGIC   ROUND(SUM(s.Sales_Amount) / COUNT(DISTINCT o.Outlet_ID), 2)         AS avg_sales_per_outlet,
# MAGIC   ROUND(AVG(g.`Gap_%`), 2)                                            AS avg_gap_pct,
# MAGIC   CASE
# MAGIC     WHEN AVG(g.`Gap_%`) > 5   THEN 'Overperforming'
# MAGIC     WHEN AVG(g.`Gap_%`) >= 0  THEN 'On Target'
# MAGIC     ELSE                           'Underperforming'
# MAGIC   END                                                                   AS gap_status
# MAGIC FROM v_outlet_master o
# MAGIC JOIN v_daily_sales s   ON o.Outlet_ID = s.Outlet_ID
# MAGIC JOIN v_gap_analysis g  ON o.Outlet_ID = g.Outlet_ID
# MAGIC GROUP BY o.Location;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.expansion_customer_demand AS
# MAGIC SELECT
# MAGIC   c.Location,
# MAGIC   COUNT(c.Customer_ID)                                                  AS total_customers,
# MAGIC   ROUND(AVG(c.Purchase_Frequency), 2)                                   AS avg_purchase_frequency,
# MAGIC   ROUND(AVG(c.Avg_Basket_Value), 2)                                     AS avg_basket_value,
# MAGIC   ROUND(AVG(c.Purchase_Frequency * c.Avg_Basket_Value), 2)              AS avg_total_spend,
# MAGIC   ROUND(SUM(c.Purchase_Frequency * c.Avg_Basket_Value), 2)              AS total_customer_spend
# MAGIC FROM v_customer_data c
# MAGIC GROUP BY c.Location;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.expansion_recommendation AS
# MAGIC SELECT
# MAGIC   sc.Location,
# MAGIC   sc.existing_outlets,
# MAGIC   sc.avg_sales_per_outlet,
# MAGIC   sc.avg_gap_pct,
# MAGIC   sc.gap_status,
# MAGIC   cd.total_customers,
# MAGIC   cd.avg_total_spend,
# MAGIC   ROUND(cd.total_customers / sc.existing_outlets, 1)                    AS customers_per_outlet,
# MAGIC   CASE sc.Location
# MAGIC     WHEN 'Sylhet'      THEN 1
# MAGIC     WHEN 'Mymensingh'  THEN 2
# MAGIC     WHEN 'Rajshahi'    THEN 3
# MAGIC     WHEN 'Dhaka'       THEN 4
# MAGIC     WHEN 'Chittagong'  THEN 5
# MAGIC     WHEN 'Khulna'      THEN 6
# MAGIC     WHEN 'Barisal'     THEN 7
# MAGIC   END                                                                    AS expansion_rank,
# MAGIC   CASE sc.Location
# MAGIC     WHEN 'Sylhet'     THEN 'RECOMMENDED'
# MAGIC     WHEN 'Mymensingh' THEN 'RECOMMENDED'
# MAGIC     WHEN 'Rajshahi'   THEN 'RECOMMENDED'
# MAGIC     ELSE                   'Sufficient Coverage'
# MAGIC   END                                                                    AS recommendation,
# MAGIC   CASE sc.Location
# MAGIC     WHEN 'Sylhet'     THEN 'Highest customers/outlet (133) + highest avg spend (1,324) + only 4 outlets'
# MAGIC     WHEN 'Mymensingh' THEN 'Only 2 outlets with +12% gap performance — existing outlets overloaded'
# MAGIC     WHEN 'Rajshahi'   THEN 'Strong demand (104.8 customers/outlet) + solid avg spend (1,211)'
# MAGIC     ELSE 'Adequate outlet coverage relative to demand'
# MAGIC   END                                                                    AS rationale
# MAGIC FROM data_analysis_retail.gold.expansion_location_scorecard sc
# MAGIC JOIN data_analysis_retail.gold.expansion_customer_demand cd ON sc.Location = cd.Location;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE data_analysis_retail.gold.expansion_final_recommendation AS
# MAGIC SELECT
# MAGIC   expansion_rank                          AS rank,
# MAGIC   Location                                AS recommended_location,
# MAGIC   existing_outlets                        AS current_outlets,
# MAGIC   customers_per_outlet                    AS demand_signal,
# MAGIC   avg_total_spend                         AS avg_customer_spend,
# MAGIC   avg_gap_pct                             AS current_gap_pct,
# MAGIC   rationale
# MAGIC FROM data_analysis_retail.gold.expansion_recommendation
# MAGIC WHERE recommendation = 'RECOMMENDED'
# MAGIC ORDER BY expansion_rank;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'expansion_location_scorecard'  AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.expansion_location_scorecard
# MAGIC UNION ALL
# MAGIC SELECT 'expansion_customer_demand'     AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.expansion_customer_demand
# MAGIC UNION ALL
# MAGIC SELECT 'expansion_recommendation'      AS tbl, COUNT(*) AS rows FROM data_analysis_retail.gold.expansion_recommendation;