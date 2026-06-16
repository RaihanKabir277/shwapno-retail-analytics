# 🛒 Shwapno Retail Analytics
### End-to-End Retail Business Intelligence & Expansion Strategy Platform using Databricks

[![Databricks](https://img.shields.io/badge/Platform-Databricks-red)]()
[![Python](https://img.shields.io/badge/Python-3.x-blue)]()
[![SQL](https://img.shields.io/badge/SQL-Analytics-green)]()
[![Architecture](https://img.shields.io/badge/Architecture-Medallion-orange)]()
[![Business Analytics](https://img.shields.io/badge/Domain-Retail_Analytics-purple)]()

---

## 📌 Project Overview

This project presents a comprehensive retail analytics solution developed as part of a Business Analyst Technical Assessment for **ACI Logistics Limited (Shwapno)**.

The objective was to transform raw operational retail data into actionable business intelligence using a modern analytics stack built on **Databricks Lakehouse Architecture**.

The solution combines:

- Retail Performance Analysis
- Gap-to-Target Evaluation
- Employee KPI Analytics
- Customer Demographic Segmentation
- Geographic Demand Assessment
- Data-Driven Expansion Recommendations
- Interactive Executive Dashboards

The analysis enables business stakeholders to identify performance bottlenecks, optimize operations, improve workforce productivity, understand customer behavior, and support strategic expansion decisions.

---

# 🎯 Business Objectives

The project addresses the following strategic business questions:

### 1. Gap Analysis
- Which outlets are failing to achieve sales targets?
- What is the magnitude of performance gaps?
- Which regions require immediate intervention?

### 2. Outlet Performance Evaluation
- Which outlets are top performers?
- How does outlet age influence sales performance?
- Which stores are consistently underperforming?

### 3. Employee KPI Assessment
- Which employees exceed performance expectations?
- Which outlets require workforce improvement?
- How strongly do KPIs influence sales performance?

### 4. Customer Demographic Analysis
- Which customer segments generate the highest value?
- How does spending vary across age groups?
- What demographic patterns influence purchasing behavior?

### 5. Expansion Strategy
- Which regions demonstrate unmet customer demand?
- Where should new retail outlets be launched?
- Which locations offer the highest growth potential?

---

# 🏗️ Solution Architecture

This project follows the industry-standard **Medallion Architecture** implemented within Databricks.

```text
Raw Data Sources
        │
        ▼
 ┌─────────────┐
 │ Bronze Layer│
 │ Raw Ingest  │
 └─────────────┘
        │
        ▼
 ┌─────────────┐
 │ Silver Layer│
 │ Cleansed    │
 │ Validated   │
 └─────────────┘
        │
        ▼
 ┌─────────────┐
 │ Gold Layer  │
 │ Business    │
 │ Metrics     │
 └─────────────┘
        │
        ▼
 Executive Dashboards
 Business Insights
 Strategic Recommendations
```

---

# 📂 Repository Structure

```text
shwapno-retail-analytics/
│
├── Dataset_For_Dashboard/
│   ├── Gold Layer Datasets
│   ├── KPI Metrics
│   └── Business Aggregations
│
├── Medalion_Architecture/
│   ├── Bronze Layer
│   ├── Silver Layer
│   └── Gold Layer
│
├── Setup/
│   ├── Environment Configuration
│   ├── Data Loading
│   └── Initialization Scripts
│
├── Retail Assesment.lvdash.json
│   └── Databricks Dashboard Configuration
│
└── README.md
```

---

# 📊 Analytics Modules

## 1️⃣ Gap Analysis

Evaluates outlet performance against predefined sales targets.

### Key Metrics
- Total Sales Gap
- Gap Percentage
- Underperforming Outlet Count
- Regional Gap Distribution
- Performance Risk Classification

### Output
- Critical Outlets
- At-Risk Outlets
- Slightly Underperforming Outlets
- Regional Performance Heatmaps

---

## 2️⃣ Outlet Performance Analysis

Analyzes store-level operational effectiveness.

### Key Metrics
- Monthly Sales
- Outlet Ranking
- Sales Achievement %
- Outlet Age Performance
- Store Performance Labels

### Output
- Top Performing Stores
- Underperforming Stores
- Performance Distribution
- Trend Analysis

---

## 3️⃣ Employee KPI Analysis

Measures workforce effectiveness across locations.

### Key Metrics
- KPI Achievement %
- Employee Ranking
- KPI Status
- Position-Based Performance
- KPI vs Sales Correlation

### Output
- Top Employees
- Bottom Employees
- KPI Risk Segments
- Workforce Productivity Insights

---

## 4️⃣ Customer Demographic Analysis

Examines purchasing behavior and customer value.

### Key Metrics
- Customer Segments
- Age Group Spending
- Basket Value
- Geographic Distribution
- Gender-Based Spending

### Output
- High Value Customers
- Mid Value Customers
- Low Value Customers
- Customer Spending Patterns

---

## 5️⃣ Expansion Recommendation Engine

Identifies high-potential regions for future retail expansion.

### Evaluation Criteria

- Customers per Outlet
- Average Customer Spend
- Current Outlet Coverage
- Sales Gap Percentage
- Demand Concentration

### Recommended Expansion Locations

| Rank | Location | Business Rationale |
|--------|----------|--------------------|
| 1 | Sylhet | Highest demand concentration with limited outlet coverage |
| 2 | Mymensingh | Strong outlet performance indicating unmet demand |
| 3 | Rajshahi | High customer density with strong spending behavior |

---

# 📈 Dashboard Features

The executive dashboard delivers:

### Executive KPIs
- Revenue Performance
- Sales Achievement
- Outlet Ranking
- KPI Status Distribution

### Interactive Analysis
- Regional Filtering
- Outlet Drill-Down
- Demographic Exploration
- Trend Visualization

### Strategic Reporting
- Expansion Recommendations
- Risk Detection
- Performance Monitoring

---

# 🛠️ Technology Stack

| Category | Technology |
|-----------|------------|
| Analytics Platform | Databricks |
| Processing Engine | Apache Spark |
| Language | Python |
| Query Engine | SQL |
| Architecture | Medallion Architecture |
| Visualization | Databricks Dashboards |
| Data Modeling | Lakehouse Architecture |

---

# 💼 Business Impact

This solution demonstrates how modern analytics platforms can support retail decision-making by:

- Improving operational visibility
- Identifying underperforming outlets
- Optimizing employee performance
- Understanding customer behavior
- Supporting data-driven expansion decisions
- Enabling executive-level reporting

---

# 🚀 Key Skills Demonstrated

### Business Analysis
- KPI Design
- Retail Performance Analysis
- Expansion Strategy
- Customer Segmentation
- Executive Reporting

### Data Engineering
- Medallion Architecture
- Data Pipeline Design
- ETL Processing
- Data Quality Validation

### Data Analytics
- Exploratory Data Analysis
- Statistical Analysis
- Business Intelligence
- Dashboard Development

### Databricks
- Lakehouse Architecture
- Delta Tables
- SQL Analytics
- Interactive Dashboards

---

# 👨‍💻 Author

## Raihan Kabir

B.Sc. in Computer Science & Engineering  
Green University of Bangladesh

### Areas of Interest
- Data Analytics
- Business Intelligence
- Data Engineering
- Machine Learning
- Retail Analytics

📧 Contact: Available upon request

---

# ⭐ Project Highlights

✔ End-to-End Databricks Analytics Solution  
✔ Medallion Architecture Implementation  
✔ Retail KPI Analytics  
✔ Executive Dashboard Development  
✔ Expansion Strategy Modeling  
✔ Business-Oriented Recommendations  
✔ Industry-Style Business Intelligence Reporting

---

> Transforming retail data into actionable business decisions through modern analytics, scalable architecture, and strategic insight generation.
