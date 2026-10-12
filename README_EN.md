# Retail Store Sales Analytics

## Project Overview

**Retail Store Sales Analytics** is an end-to-end data analytics project that transforms a retail transaction dataset with data-quality issues into a validated analytical model and an interactive Power BI report.

The project demonstrates a business-oriented workflow covering data exploration, preparation and validation; dimensional modeling in PostgreSQL; business measures in DAX; and communication of findings through an interactive report.

The analysis covers sales, categories and products, customers, sales channels, payment methods, temporal trends, and—particularly—the limitations of discount analysis caused by the large number of records with an unreported discount status.

> The dataset is used for learning and analytical demonstration. Findings describe this dataset and should not be treated as evidence about an actual company.

## Objectives

- Explore the structure, quality, and limitations of the dataset.
- Clean and transform records using explicit, reproducible rules.
- Validate data integrity and the consistency of sales metrics.
- Organize the data into a dimensional model in PostgreSQL.
- Develop business measures with DAX.
- Build a Power BI report that supports exploration and commercial questions.
- Communicate findings and limitations without claiming causality that the data cannot establish.

## Tools

- **Python and pandas:** exploration, cleaning, transformation, and validation.
- **PostgreSQL and SQL:** analytical storage, star-schema modeling, and integrity checks.
- **Power BI and DAX:** business measures, interactive analysis, and visualization.
- **Jupyter Notebook:** initial exploration and analysis documentation.

## Dataset

The project uses **Retail Store Sales: Dirty for Data Cleaning**, published on Kaggle. The original dataset contains 12,575 records and 11 columns describing retail transactions.

- **Coverage period:** January 1, 2022 to January 18, 2025.
- **Transactions:** 12,575.
- **Identified customers:** 25.
- **Categories:** 8.
- **Sales channels:** Online and In-store.
- **Payment methods:** 3.
- **Discount states in the processed dataset:** `True`, `False`, and `Unknown`.

Source: [Kaggle — Retail Store Sales: Dirty for Data Cleaning](https://www.kaggle.com/datasets?search=Retail+Store+Sales%3A+Dirty+for+Data+Cleaning)

## Workflow and Validation

### 1. Data Inspection and Exploratory Analysis

The dataset dimensions, data types, missing values, potential duplicates, distributions, and relationships between variables were reviewed. Findings from this stage informed the data-preparation decisions.

### 2. Cleaning and Transformation

The preparation process included:

- Standardizing column names to `snake_case`.
- Converting `transaction_date` to a date type.
- Converting categorical variables to suitable data types.
- Using more efficient numeric types for sales metrics.
- Reconstructing the 609 missing `price_per_unit` values when possible using `total_spent / quantity`.
- Imputing the 604 missing `quantity` values with the median (6 units) and reconstructing `total_spent` from price and quantity.
- Representing missing `item` values as `Unknown`.
- Preserving unknown discount states as `Unknown` instead of arbitrarily classifying them as `False`.

### 3. Data-Quality Validation

After preparation, the following checks were completed:

- The processed dataset contains 12,575 records and 11 columns.
- No nulls remain in the processed columns; where information could not be recovered, the explicit value `Unknown` was retained.
- No duplicate transactions were found.
- The validation `total_spent = price_per_unit × quantity` showed no differences across all 12,575 processed records.
- PostgreSQL referential-integrity checks found no orphan records in the relationships tested.
- The main Power BI metrics were reconciled against PostgreSQL queries.

Arithmetic consistency between unit price, quantity, and total amount does not by itself establish whether a discount was applied or prove that unit price always represents the pre-discount list price.

### 4. Dimensional Modeling in PostgreSQL

The data was organized into a fact table and dimensions to support analysis by date, customer, product, location/channel, and payment method:

- `fact_sales`
- `dim_customer`
- `dim_product`
- `dim_date`
- `dim_payment_method`
- `dim_location`

The model supports analysis from multiple perspectives and allows aggregated results to be validated.

## Power BI Report

The final report is organized into five complementary analytical areas:

1. **Executive Overview:** presents headline indicators and overall sales evolution to establish an executive view of observed performance.
2. **Sales Performance:** compares sales, units, and category share, with additional product-level analysis.
3. **Customer & Channel Behavior:** explores aggregated customer behavior and compares results by sales channel and payment method.
4. **Discounts & Commercial Behavior:** compares sales, transactions, and average transaction value by discount status. Known and unknown statuses remain separate so missing information is not concealed.
5. **Deep Dive / Interactive Analysis:** supports exploratory analysis through filters and comparisons by category, period, channel, payment method, and discount status.

The report combines headline indicators, temporal trends, and commercial breakdowns to help users move from a high-level view to more specific questions. Results are descriptive: differences between groups do not by themselves prove that a channel, payment method, or discount caused a particular outcome.

## Validated Global Metrics

The following results were reconciled between Power BI and PostgreSQL:

| Metric | Result |
|---|---:|
| Total Sales | 1,637,367.00 |
| Total Transactions | 12,575 |
| Total Units | 69,900 |
| Average Transaction Value | 130.21 |
| Average Unit Price | 23.37 |
| Average Units per Transaction | 5.56 |

Amounts are reported in the dataset's monetary units. The source does not unambiguously specify a currency, so no currency symbol is assigned.

## Key Finding and Limitation: Discount Information

The original `Discount Applied` column contained **4,199 missing values, equivalent to 33.4% of records**. This is a substantial share and cannot be explained solely by missing unit prices or quantities, since those fields had fewer missing values.

To avoid inventing information, unknown states were retained as `Unknown`, separate from `True` and `False`. The report allows available metrics to be compared by discount status, but the unknown category limits interpretation and commercial evaluation of discounts.

Consistency between unit price, quantity, and total amount does not establish whether a discount was or was not applied. There is also insufficient evidence to guarantee that `price_per_unit` always represents the pre-discount list price. Therefore, the results should not be interpreted as a conclusive measurement of the effect of discounts.

## Other Analytical Limitations

- **Unknown products:** records whose item could not be identified are retained as `Unknown`. A category associated with that value in the model may be a technical modeling artifact and should not be interpreted as a real business category.
- **Profitability:** the dataset does not provide sufficient cost or margin information to calculate profitability.
- **Causality:** the analysis describes patterns and differences but cannot prove that discounts, channels, or other variables caused changes in sales.
- **Representativeness:** conclusions describe the dataset used and should not be generalized to a real company without additional evidence.

## Repository Structure

```text
retail-store-sales-analytics/
├── data/
│   ├── raw/
│   │   └── retail_store_sales.csv
│   └── processed/
│       └── retail_store_sales_processed.csv
├── notebooks/
│   └── 01_extraccion_eda.ipynb
├── scripts/
│   ├── 02_limpieza_enriquecimiento.py
│   └── 03_cargar_postgres.py
├── SQL/
│   ├── 01_modelo_estrella.sql
│   └── 02_validaciones_integridad.sql
├── Power_BI/
│   └── retail_store_sales.pbix
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
└── README_EN.md
```

Filenames and folders should match those actually committed to the repository.

## Reproducing the Project

1. Clone the repository.
2. Create a Python virtual environment and install the dependencies in `requirements.txt`.
3. Review and run the exploratory notebook.
4. Run the cleaning and enrichment script to generate the processed dataset.
5. Configure PostgreSQL and execute the SQL scripts in the appropriate order.
6. Run the loading script to populate the model according to the local configuration.
7. Open `Power_BI/retail_store_sales.pbix` in Power BI Desktop and configure its connection to the local database.
8. Run validation checks and reconcile the main metrics before interpreting results.

Database credentials and connection parameters must be configured locally and must not be committed to the repository.

## Author

**Marco Schroeder**  
Data Analytics and Business Intelligence Portfolio.

Repository: [retail-store-sales-analytics](https://github.com/Marco-Schroeder-Data-Scientist/retail-store-sales-analytics)
