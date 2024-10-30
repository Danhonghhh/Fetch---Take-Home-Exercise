#!/usr/bin/env python
# coding: utf-8

# # Fetch - Take Home Exercise

# - By: Danhong Huang  
# - Date: October 28th 2024

# In[96]:


# import necesary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from pandasql import sqldf


# ## 1. Explore Data Analysis
# Review the unstructured csv files and answer the following questions with code that supports your conclusions:
# - Are there any data quality issues present?
# - Are there any fields that are challenging to understand?

# ### 1.1 Load and Explore Products Data

# In[60]:


#load products data
pdt = pd.read_csv('PRODUCTS_TAKEHOME.csv')
pdt.head(20)


# In[11]:


# Number of rows and columns
print(pdt.shape)

# Column data types and non-null values
print(pdt.info())

# Descriptive statistics for numerical columns
print(pdt.describe())

# Basic statistics for categorical columns
print(pdt.describe(include='object'))


# #### Findings
# - **Missing Value**: There are some missing values present in the dataset, which require further investigation to determine the extent and potential impact on analysis.
# 
# 
# - **BARCODE Data Type**: The data type of the `BARCODE` field is currently set as an integer, causing it to be automatically displayed in scientific notation due to its length. To address this, it may be beneficial to convert the data type to `VARCHAR` to ensure readability and preserve accuracy.
# 
# 
# - **Column Name Confusion**: The column name `BARCODE` could also be reconsidered, as it may not fully capture the nature of the identifier. Renaming it to something more descriptive, such as `PRODUCT_ID`, could help make the data more intuitive and easier to understand.
# 

# In[36]:


# plot null rate

# Calculate null rate as a percentage
null_rate = pdt.isnull().mean() * 100

# Create bar plot for null rate
plt.figure(figsize=(10, 6))
ax = sns.barplot(x=null_rate.index, y=null_rate.values, hue=null_rate.index, palette="plasma_r")

plt.ylabel('Percentage of Null Rate')
plt.xlabel('Columns')
plt.title('Null Rate per Column')
plt.ylim(0, 100)  # Limit the y-axis from 0 to 100 for better readability
plt.xticks(rotation=45)

# Add numerical values on each bar
for p in ax.patches:
    ax.annotate(f'{p.get_height():.2f}%', 
                (p.get_x() + p.get_width() / 2, p.get_height()), 
                ha='center', va='bottom', fontsize=10, color='black')

plt.show()


# In[43]:


# check NONE value
pdt_1 = pdt[pdt['MANUFACTURER'] == 'NONE']
# pdt_2 = pdt[pdt['CATEGORY_2'] == 'NONE']

display(pdt_1)
# display(pdt_2)


# (Assuming we are looking at a subset of the data, so we do not care about the potential category bias)
# 
# #### Findings
# - **There are missing values across several fields, Specifically**:      
#   
#   **1) Product Barcode**: Approximately 0.5% of the `BARCODE` values are missing, which is significant since this field serves as the unique identifier for a product.  
#   **2) Manufacturer and Brand**: Around 27% of both `MANUFACTURER` and `BRAND` fields are missing. This is concerning as manufacturer and brand information is crucial for marketing, product, transaction, and user behavior analysis.  
#   **3) CATEGORY_4**: Although about 92% of `CATEGORY_4` values are missing, this is less critical since most product category information is captured by `CATEGORY_1` and `CATEGORY_2`, which have null rates of less than 1%.  
#   
# 
# - **Inconsistent Null Values:**
# There are inconsistencies in how null values are represented, particularly in the `MANUFACTURER` field, where some null values are populated as "NONE". This inconsistency could lead to inaccuracies when assessing the null rate and requires standardization.
# 
#     

# In[64]:


# fix the data type issue and inconsistent null value
# Convert BARCODE to string (VARCHAR equivalent)
pdt['BARCODE'] = pdt['BARCODE'].astype('Int64').astype('str')

# Replace 'None' (result of converting NaN to string) with NaN
pdt['MANUFACTURER'] = pdt['MANUFACTURER'].replace('NONE', 'NaN')


# In[65]:


# check null value in MANUFACTURER column
pdt_3 = pdt[pdt['MANUFACTURER'] == 'NONE']

display(pdt.head(20))


# In[69]:


# Check for duplicate BARCODE values
duplicated_rows = pdt[pdt.duplicated(subset='BARCODE', keep=False)]

# Find distinct duplicated BARCODE values
duplicate_barcodes = barcode_duplicates['BARCODE'].unique()

# Print the number of duplicated rows and distinct duplicate barcodes if any
if barcode_duplicates.empty:
    print("No duplicate BARCODE values found.")
else:
    print("Duplicate BARCODE values found:")
    print(f'There are {len(duplicated_rows)} rows of duplication, with {len(duplicate_barcodes)} distinct barcodes.')


# #### Finding:
#  - **Duplication:**  
# The product table contains approximately 4,000 duplicate entries, though we would expect each product entry to be unique. It may be worth considering the removal of these duplicates.

# ### 1.2 Load and Explore Transaction Data

# In[44]:


#load transaction data
txn = pd.read_csv('TRANSACTION_TAKEHOME.csv')
txn.head(20)


# In[74]:


# Number of rows and columns
print(txn.shape)

# Column data types and non-null values
print(txn.info())

# Descriptive statistics for numerical columns
print(txn.describe())

# Basic statistics for categorical columns
print(txn.describe(include='object'))


# In[86]:


# Check for duplicate RECEIPT_ID values
duplicated_rows = txn[txn.duplicated(subset='RECEIPT_ID', keep=False)]

# Find distinct duplicated RECEIPT_ID values
duplicate_RECEIPT_ID = duplicated_rows['RECEIPT_ID'].unique()

# Print the number of duplicated rows and distinct duplicate RECEIPT_IDs if any
if duplicated_rows.empty:
    print("No duplicate RECEIPT_ID values found.")
else:
    print("Duplicate RECEIPT_ID values found:")
    print(f'There are {len(duplicated_rows)} rows of duplication, with {len(duplicate_RECEIPT_ID)} distinct RECEIPT_IDs.')


# #### Findings
# 
# - **Missing Values**: There are missing values in the `BARCODE` field, which could impact analyses reliant on product-level identification.
# 
# 
# - **Inconsistent Field Format**: The `FINAL_QUANTITY` field contains mixed data types, including numeric values (e.g., `1.00`) and text entries (e.g., "zero"). Standardizing this field to a consistent numeric format would improve data usability.
# 
# 
# - **Data Type Issues**: 
#     - `PURCHASE_DATE` and `SCAN_DATE` should be of date type.
#     - `FINAL_QUANTITY` and `FINAL_SALE` should be numeric.
#     - `BARCODE` should be of type object (varchar).
# 
# - **Potential Data Anomalies**: Both `FINAL_QUANTITY` and `FINAL_SALE` fields contain numerous zero values, which is unusual for transaction data. This may indicate data entry errors or missing information and warrants further investigation.
# 

# ### 1.3 Load and Explore User Data

# In[73]:


#load user data
user = pd.read_csv('USER_TAKEHOME.csv')
user.head(20)


# In[76]:


# Number of rows and columns
print(user.shape)

# Column data types and non-null values
print(user.info())

# Basic statistics for categorical columns
print(user.describe(include='object'))


# In[82]:


# plot null rate

# Calculate null rate as a percentage
null_rate = user.isnull().mean() * 100

# Create bar plot for null rate
plt.figure(figsize=(10, 6))
ax = sns.barplot(x=null_rate.index, y=null_rate.values, hue=null_rate.index, palette="plasma_r")

plt.ylabel('Percentage of Null Rate')
plt.xlabel('Columns')
plt.title('Null Rate per Column')
plt.ylim(0, 100)  # Limit the y-axis from 0 to 100 for better readability
plt.xticks(rotation=45)

# Add numerical values on each bar
for p in ax.patches:
    ax.annotate(f'{p.get_height():.2f}%', 
                (p.get_x() + p.get_width() / 2, p.get_height()), 
                ha='center', va='bottom', fontsize=10, color='black')

plt.show()


# In[81]:


# Plot gender distribution
gender_counts = user['GENDER'].value_counts()

# Plotting a pie chart using Matplotlib with a Seaborn color palette (plasma)
plt.figure(figsize=(8, 6))
plt.pie(gender_counts, labels=None, autopct='%1.1f%%', 
        colors=sns.color_palette("plasma_r", len(gender_counts)))

# Add a legend on the right side
plt.legend(gender_counts.index, title="Gender", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.title("Gender Distribution")
plt.show()


# #### Findings
# 
# - **Missing Values**: Missing data is present in several fields, including `LANGUAGE`, `BIRTH_DATE`, `GENDER`, and `STATE`.
# 
# 
# - **Data Type Issues**: 
#     - Both `CREATED_DATE` and `BIRTH_DATE` should ideally be in date format for accurate time-based analysis.
# 
# 
# - **Panel User Bias**: Assuming this sample represents all Fetch users, it’s possible the data skews female, as 68% of users are women. This could be like listening to a conversation with more voices from one group than another, which might tilt insights unless accounted for.
# 

# ### Findings Summary
# 
# #### Transaction Table
# 
# - **Missing Values**: 
#   - Some missing values are present in the transaction table. Further investigation is needed to assess the extent and potential impact of these missing values on analysis.
# 
# - **BARCODE Data Type**: 
#   - The `BARCODE` field is currently set as an integer, which causes it to display in scientific notation due to its length. Converting this field to `VARCHAR` would enhance readability and accuracy.
# 
# - **Column Name Confusion**: 
#   - The `BARCODE` column name might be reconsidered, as it may not fully describe the identifier’s purpose. Renaming it to something more descriptive, like `PRODUCT_ID`, could improve clarity.
# 
# - **Duplication**: 
#   - The transaction table contains approximately half duplicate entries, which might affect analysis accuracy. 
#   
#   (Assuming this is a subset of the data, we may not need to account for potential category bias.)
# 
# ---
# 
# #### Product Table
# 
# - **Missing Values**:
#   - **Product Barcode**: Approximately 0.5% of `BARCODE` values are missing. This is significant because `BARCODE` serves as the unique product identifier.
#   - **Manufacturer and Brand**: Around 27% of values in the `MANUFACTURER` and `BRAND` fields are missing. This is concerning, as these fields are essential for marketing, product, transaction, and user behavior analyses.
#   - **CATEGORY_4**: Although 92% of `CATEGORY_4` values are missing, this is less critical since category details are largely captured in `CATEGORY_1` and `CATEGORY_2`, both of which have null rates below 1%.
# 
# - **Inconsistent Null Values**:
#   - Inconsistencies are present in how null values are represented, especially in the `MANUFACTURER` field where some nulls are recorded as `"NONE"`. Standardizing this representation is recommended to avoid inaccuracies in null rate assessments.
# 
# - **Duplication**: 
#   - The product table contains duplicate entries. Given that each product entry should ideally be unique, it may be beneficial to remove these duplicates.
# 
# ---
# 
# #### User Table
# 
# - **Missing Values**: 
#   - Missing data exists in several fields, including `LANGUAGE`, `BIRTH_DATE`, `GENDER`, and `STATE`, which could affect demographic and behavioral analyses.
# 
# - **Data Type Issues**: 
#   - The `CREATED_DATE` and `BIRTH_DATE` fields should ideally be in date format to enable accurate time-based analyses.
# 
# - **Panel User Bias**: 
#   - Assuming this dataset represents all Fetch users, there may be a gender bias, as 68% of users are female. This imbalance could influence insights and should be accounted for in any generalized conclusions.
# 

# ## 2. SQL queries

# ### 2.1 What are the top 5 brands by receipts scanned among users 21 and over?
# 
# **Assumptions:**
# 
# We assume that "scanned receipts" refers to entries in the transaction table, where each receipt is identified by a unique RECEIPT_ID.

# In[103]:


sqldf('''
SELECT 
    p.BRAND, 
    COUNT(t.RECEIPT_ID) AS receipt_count
FROM txn t
    JOIN pdt p ON t.BARCODE = p.BARCODE
    JOIN user u ON t.USER_ID = u.ID
WHERE 
    (strftime('%Y', 'now') - strftime('%Y', u.BIRTH_DATE)) >= 21
GROUP BY 
    p.BRAND
ORDER BY 
    receipt_count DESC
LIMIT 5;
''')


# ### 2.2 What is the percentage of sales in the Health & Wellness category by generation?
# 
# **Assumptions:**  
# 
# - We define generations based on user age groups: Gen Z (18-24), Millennials (25-40), Gen X (41-56), and Baby Boomers (57+).
# - "Health & Wellness" is identified in CATEGORY_1
# 

# In[101]:


sqldf('''
SELECT 
    CASE 
        WHEN (strftime('%Y', 'now') - strftime('%Y', u.BIRTH_DATE)) BETWEEN 18 AND 24 THEN 'Gen Z'
        WHEN (strftime('%Y', 'now') - strftime('%Y', u.BIRTH_DATE)) BETWEEN 25 AND 40 THEN 'Millennials'
        WHEN (strftime('%Y', 'now') - strftime('%Y', u.BIRTH_DATE)) BETWEEN 41 AND 56 THEN 'Gen X'
        ELSE 'Baby Boomers' 
    END AS generation,
    SUM(t.FINAL_SALE) * 100.0 / (SELECT SUM(FINAL_SALE) FROM txn ) AS health_wellness_sales_percentage
FROM 
    txn t
    JOIN pdt p ON t.BARCODE = p.BARCODE
    JOIN user u ON t.USER_ID = u.ID
WHERE 
    p.CATEGORY_1 = 'Health & Wellness'
GROUP BY 
    generation
''')


# ### 2.3 Who are Fetch’s power users?
# 
# **Assumptions:**
# 
# We define "power users" as those who frequently make transactions, say, more than a specific threshold of transactions per month, or those who have the highest cumulative FINAL_SALE.

# In[105]:


sqldf('''
SELECT 
    t.USER_ID, 
    COUNT(t.RECEIPT_ID) AS transaction_count, 
    SUM(t.FINAL_SALE) AS total_spent
FROM 
    txn t
GROUP BY 
    t.USER_ID
HAVING 
    COUNT(t.RECEIPT_ID) > 10 OR SUM(t.FINAL_SALE) > 1000
ORDER BY 
    total_spent DESC;
''')


# ## 3. Communicate with Stakeholders

# Hi [Product/Business Leader’s Name],
# 
# After analyzing the recent data sample, I wanted to share some observations that may help guide our next steps. Here are the key takeaways:
# 
# ### Data Quality Issues:
# 1. **Transaction Data**: We noticed missing values in the transaction table and duplication across roughly half the entries, which could affect the reliability of any analyses.
# 2. **Product Table**: Critical fields, such as `MANUFACTURER` and `BRAND`, have around 27% missing values. The `BARCODE` field is also occasionally missing (0.5%) and is currently set as an integer, which creates display issues (e.g., scientific notation) due to its length. Converting it to a `VARCHAR` format would improve readability.
# 3. **User Data**: Missing demographic fields, including `LANGUAGE`, `BIRTH_DATE`, `GENDER`, and `STATE`, could impact segmentation or demographic insights. Additionally, our user base skews heavily female (68%), suggesting potential gender bias if this sample represents the full user population.
# 
# ### Key Insight:
# An interesting finding from our analysis is that Baby Boomers have the highest percentage of sales in the Health & Wellness category (at 0.06% of total sales), surpassing other generations. This may indicate a unique interest in wellness products among this age group, which could inform targeted marketing strategies.
# 
# ### Next Steps:
# To fully leverage this data, we need further clarification on a few points:
# 1. **Data Completeness**: Could we confirm if this data sample is representative of all users? Understanding this will help us assess the potential impact of demographic bias.
# 2. **Missing Values**: Additional context on missing values (e.g., why certain fields are consistently blank) would aid in determining if we should exclude or estimate these values in analysis.
# 3. **Duplication**: Are duplicate entries expected within the transaction table, or should they be cleaned out for accurate reporting?
# 
# These insights and next steps will allow us to conduct more accurate, representative analyses. Let me know if there’s someone I can connect with for more details.
# 
# Thank you,  
# Danhong
# 
