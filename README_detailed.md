# **Reference Manual: Car Sales Dashboard**

**Subject:** Data Interpretation and Presentation (MDIP)

**Author:** Jakub Hána

**Date:** 2025

## **Table of Contents**

1. [Introduction](#1-introduction)  
2. [Technical Information](#2-technical-information)  
3. [Function and Class Descriptions](#3-function-and-class-descriptions)
4. [Testing and Validation](#4-testing-and-validation)  
5. [Handling Unexpected Situations](#5-handling-unexpected-situations)

## 1. Introduction

This document serves as a technical reference guide for the "Car Sales Dashboard" application - 
it is an interactive analytical tool developed in Python using the Dash framework and Plotly library

**Key Features:**

* Visualizes the used car sales dataset (AutoScout24)  
* Enables users (sales managers, analysts) to explore market trends, pricing and correlations  
* Integrates various visualization types from hierarchical charts (Sunburst) to distribution charts (Box Plot) and correlation matrices (Heatmap)

## 2. Technical Information

### 2.1 Dependencies

The application is built on a modern Python 3.13+ stack. Key libraries include:

* **Dash (>=3.3.0):** Web framework for the application  
* **Dash Bootstrap Components (>=2.0.4):** Responsive layout and UI components  
* **Plotly (>=6.5.0):** Interactive charts  
* **Pandas (>=2.3.3):** Data manipulation and cleaning

### 2.2 Installation

The project uses **Poetry** for dependency management and virtual environment handling

**Installation Steps:**

1. Ensure Python 3.13+ and Poetry (https://python-poetry.org/docs - `pip install poetry`) are installed  
2. Clone the project repository  
3. Run the dependency installation command in the project root: `poetry install`

4. This command automatically creates a virtual environment and installs all packages defined in pyproject.toml
5. If the virtual environment was not created automatically, run this command: `python3 -m venv .venv` and try step 4 again

### 2.3 Application Execution

The application is launched using the entry script main.py

**Run Command:**

`python main.py`

The application will be available at http://localhost:8050 (debug mode is enabled by default)

## 3. Function and Class Descriptions

This chapter details the application architecture divided into logical modules within the src/ directory

### Module: `data_loader`

Handles data loading, cleaning and preparation.

#### Class `DataLoader`

* **Location:** src/data_loader.py  
* **Purpose:** Singleton class responsible for loading the CSV file, removing erroneous data and providing filter ranges

##### Method `__init__`

* **Parameters:**  
  * filepath (str, optional): Path to CSV file. Default from constants.DATA_SET_PATH  
* **Description:**  
  * Initializes loader instance  
  * Loads data only upon first load_data call (lazy loading)

##### Method `load_data`

* **Parameters:** None  
* **Return Value:** pd.DataFrame – Cleaned dataframe  
* **Description:**  
  * Loads CSV file  
  * Removes rows with missing values in critical columns (make, model, fuel, hp, gear)  
  * Converts year column to int  
  * Filters out invalid values (price <= 100, hp <= 0)

##### Method `get_metadata`

* **Parameters:** None  
* **Return Value:** Metadata object (dataclass)  
* **Description:**  
  * Calculates global dataset statistics (min/max year, price, mileage)  
  * Used for setting filter limits (RangeSliders)  
* **Usage Example:**  
  loader = DataLoader()  
  metadata = loader.get_metadata()  
  print(f"Year range: {meta.min_year} - {meta.max_year}")

### Module: `charts`

Contains functions for generating Plotly charts. All functions return a plotly.graph_objects.Figure object.

#### Function `_update_layout`

* **Location:** src/charts.py  
* **Purpose:** Helper function for applying uniform visual style to all charts  
* **Parameters:** fig (go.Figure)  
* **Return Value:** go.Figure with applied style  
* **Description:**  
  * Sets font family and size  
  * Sets transparent background  
  * Adjusts margins

#### Function `create_sunburst_chart`

* **Location:** src/charts.py  
* **Purpose:** Creates hierarchical pie chart for market overview  
* **Parameters:** data (pd.DataFrame) – Input data  
* **Description:**  
  * Visualizes hierarchy Brand -> Model -> Fuel  
  * Aggregates less frequent brands (outside Top 10) into "Other" category for clarity

#### Function `create_scatter_chart_price_mileage`

* **Location:** src/charts.py  
* **Purpose:** Creates scatter plot for Price vs. Mileage analysis  
* **Parameters:** data (pd.DataFrame)  
* **Description:**  
  * X-Axis: Mileage, Y-Axis: Price  
  * Color differentiation (Hue) by fuel type  
  * Embeds custom_data (car index) for interactive callback details

#### `Function create_heatmap_price_mileage_hp_year`

* **Location:** src/charts.py  
* **Purpose:** Creates correlation matrix (Heatmap)  
* **Parameters:** data (pd.DataFrame)  
* **Description:**  
  * Calculates Pearson correlation coefficient for numeric columns (price, mileage, hp, year)  
  * Displays correlations using a color-scaled map

### Module: `callbacks`

Contains logic connecting UI and data (application reactivity)

#### Function `setup`

* **Location:** src/callbacks.py  
* **Purpose:** Registers all callback functions to the Dash application  
* **Parameters:**  
  * app (Dash): Application instance  
  * loader (DataLoader): Data loader instance

#### Callback `update_dashboard`

* **Location:** src/callbacks.py (inner function in setup)  
* **Purpose:** Main dashboard control function  
* **Inputs:** Values from all filters (Brand, Model, Year, Price, Mileage, Fuel, Transmission)  
* **Outputs:**  
  * KPI card values (Count, Price, Mileage)  
  * Text analysis "Smart Insight"  
  * All 6 charts (Sunburst, Line, Scatter, Box, Pie, Heatmap)  
* **Functionality:**  
  * Filters global DataFrame based on inputs  
  * Returns empty charts and message if result is empty  
  * Calculates KPIs  
  * Generates "Smart Insight" (e.g., price comparison vs market average)  
  * Calls functions from src.charts to redraw graphs

### Module: `helpers`

Helper functions for formatting and UI components

#### Function `format_number`

* **Location:** src/helpers.py  
* **Purpose:** Formats large numbers into readable string  
* **Parameters:** value (float or int)  
* **Return Value:** str (e.g., 1,200,000 -> "1.2M")

#### Function `create_kpi_card`

* **Location:** src/helpers.py  
* **Purpose:** Generates dbc.Card component for displaying key metrics  
* **Parameters:** title, icon_class, id_value, color_hex, tooltip_text  
* **Return Value:** dbc.Card (Dash component)

## 4. Testing and Validation

### 4.1 Testing

Testing combined static code analysis and manual User Acceptance Testing (UAT)

1. **Data Loading Validation:**  
   * Verified DataLoader correctly drops missing values  
   * Tested with corrupted CSV (simulation) -> ensures application logs error instead of crashing  
2. **Interactivity Testing (Callback chain):**  
   * **Scenario:** User selects "Audi" brand  
   * **Expected Behavior:** "Model" dropdown unlocks and shows only Audi models, charts redraw  
   * **Result:** Functional, ensured by cascading update_model_options callback  
3. **Cross-filter Tests:**  
   * tested combination of filters (e.g., "Year 2020+" and "Price < 5000 €")  
   * verified application does not crash when filters return empty set

## 5. Handling Unexpected Situations

### 5.1 Missing or Incorrect Data

Application robustness strategies:

* **Data Cleaning:** DataLoader automatically discards rows with NaN in critical columns at startup  
* **Outliers:** Extremely low prices (e.g., 0 or 1 €) and zero engine power are filtered in load_data to prevent skewing averages and charts

### 5.2 Empty Filter Selection

If user filters result in zero vehicles:

* Callback update_dashboard detects data_filtered.empty  
* Returns "No data available" text to smart-insight component  
* KPI cards display zeros  
* Charts render as empty objects, visually prompting user to relax filters
