# Databricks notebook source
# MAGIC %sql
# MAGIC create catalog if not exists Data_Analysis_Retail;

# COMMAND ----------

# MAGIC %sql
# MAGIC use catalog Data_Analysis_Retail;

# COMMAND ----------

# MAGIC %sql
# MAGIC create schema if not exists Data_Analysis_Retail.gold;

# COMMAND ----------

# MAGIC %sql
# MAGIC show databases from Data_Analysis_Retail;

# COMMAND ----------

# MAGIC %sql
# MAGIC create schema if not exists Data_Analysis_Retail.source_data;

# COMMAND ----------

