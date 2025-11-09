# Disaster Incident and Rescue Management System - NIC

The *Disaster Incident and Rescue Management System* is a web-application dashboard developed at NIC to analyze disaster data at multiple levels. It supports effective decision-making by providing real-time, interactive visualizations that improve disaster monitoring, coordination, and rescue operations. Built using Python, Pandas, NumPy, and SQL for robust data processing, and Plotly with Streamlit for intuitive dashboard presentations, this system enables data-driven insights for enhancing public safety during emergencies.

The project has been **officially adopted and actively used by the Government of Bihar**, reflecting its critical role in disaster and incident management.

**Author**: ARYAN N K ARYA

---

## Project Overview

This repository contains multiple analytical dashboards designed to address distinct aspects of disaster management:

1. **ColdWave Incident Dashboard**  
   This dashboard facilitates monitoring of cold wave incidents, focusing on affected population, deaths, shelter provisions, and financial expenditures. It connects to a SQL Server database for dynamic data loading and provides KPIs and time-series visualizations using Plotly and Streamlit.  
   **Core Snippet:** Demonstrates setup of database connection, data extraction, preprocessing, and KPI display logic that form the backbone of the dashboard.

2. **Disaster Incident Dashboard**  
   This dashboard aggregates detailed incident reports, including hazard types, casualty counts, and verification status, spanning several years. It includes efficient data pipeline caching and real-time UI elements for filtering and metrics summary.  
   **Core Snippet:** Highlights database integration, advanced SQL querying with aggregation, and cleaned data presentation for interactive exploration of incident data.

3. **Bihar Flood Disaster Dashboard**  
   This component is designed for flood-related disaster monitoring showing critical metrics such as affected population, deaths, relief center stats, and resource distribution. It implements structured data loading from multiple table joins, extensive data cleaning, and effective KPI visualization cards.  
   **Core Snippet:** Focuses on data extraction from complex queries, column-wise typing and cleaning, and succinct key metric presentation on the Streamlit dashboard.

---

## How to Use

The provided code snippets illustrate the essential functionality underlying each major dashboard application in this system. They include:

- Initialization and caching of secure database connections via SQLAlchemy and `.toml` configuration files.
- Smart data loading with SQL queries that join production tables and perform pre-aggregation.
- Data cleaning steps such as datetime conversion, string trimming, and numeric coercion to ensure data integrity.
- Creation of concise and interactive KPI cards and plots using Streamlit and Plotly for immediate insight delivery.

These snippets are intended to give a clear view of the technical depth and practical capabilities implemented to enable disaster responders and policymakers to make timely and well-informed decisions.

---

## Repository Content

- `ColdWave_Dashboard_Snippet.py`: Core data fetch and dashboard rendering logic for cold wave incidents.
- `Disaster_Incident_Dashboard_Snippet.py`: SQL data retrieval and incident overview visualization setup.
- `Flood_Disaster_Dashboard_Snippet.py`: Flood-specific data pipeline and KPI display code.

---

