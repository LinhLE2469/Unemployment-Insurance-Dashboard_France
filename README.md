# Unemployment Insurance Dashboard – France (2020–2025)

This project is a data storytelling dashboard built with Streamlit.  
It analyzes unemployment insurance indicators across French departments from 2020 to 2025.  
The goal is to transform a raw public dataset into an interactive, visual narrative that helps users explore trends, geography, and differences between departments.

---
### Data input

- By default, the app loads `data/raw_data.csv` included in the repository so that users can test the dashboard immediately.
- Users can also upload their own CSV file from the sidebar. In that case, the file is cleaned on the fly using the same preprocessing pipeline.

## 1. Overview

The dashboard guides the user through a clear story:

1. Upload raw data  
2. Automatic data cleaning  
3. Key indicators (latest month)  
4. Trends over time  
5. Department rankings  
6. Geographic comparison  
7. Interactive exploration using filters  
8. Download filtered data  

This structure allows users to answer questions such as:
- How is unemployment insurance evolving over time?
- Which departments contribute most to spending?
- Where are the geographic hotspots?
- How do indicators change across regions or periods?

---

## 2.Dataset

The dataset contains monthly unemployment insurance indicators for all French departments between 2020 and 2025.

Key fields include:
- `allocataires_total` — number of beneficiaries  
- `ouvertures_droit` — new rights opened  
- `fins_droit` — rights ending  
- `depense_mensuelle` — total spending  
- `part_trav_mois` — share of beneficiaries who worked during the month  
- `region`, `departement`, `code_dep`  
- `mois` — month (YYYY-MM)  

The raw dataset required cleaning before use.

---

## Data Cleaning Summary

The project includes a full cleaning pipeline:

- Renamed long column names to shorter, consistent English names  
- Converted dates from text to datetime format  
- Removed duplicate rows  
- Converted selected columns to category for efficiency  
- Standardized department codes (e.g., “01”, “2A”, “2B”)  
- Removed unnecessary geographic columns  
- Handled missing values using:
  - drop rows for minor missing columns  
  - interpolation + median fill for heavily missing columns  

The cleaned dataset is saved as `data_cleaned.csv`.

---

## 4. Dashboard Features

### Key Indicators (latest month)
Shows:
- number of beneficiaries  
- number of new rights  
- number of rights ending  
- total monthly spending  
+ month-over-month change  

### Time Series
Trend over time for the selected indicator.

### Ranking
Top N departments for the latest month in the selected period.

### Choropleth Map
Geographic comparison for the latest month in the selected period.

### Sidebar Filters
Users can filter by:
- Region  
- Department  
- Time range  
- Indicator  

All charts update instantly.

### Download
Users can export the filtered dataset as CSV.

## 6. How to Run the App

### Install dependencies
pip install -r requirements.txt

streamlit run app.py

### **Demo**
demo.mov
https://unemployment-insurance-dashboardfrancegit-avjjkmaxgigzalrl5nqn.streamlit.app/
