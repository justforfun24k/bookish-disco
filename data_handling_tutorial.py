"""
data_handling_tutorial.py - Data Handling with NumPy and Pandas

This tutorial covers:
1. NumPy: Arrays, operations, indexing
2. Pandas: DataFrames, Series, data manipulation
"""

import numpy as np
import pandas as pd

print("=" * 60)
print("DATA HANDLING TUTORIAL: NumPy and Pandas")
print("=" * 60)

# =============================================
# PART 1: NumPy Basics
# =============================================
print("\n" + "=" * 40)
print("PART 1: NumPy Arrays")
print("=" * 40)

# Creating arrays
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([[1, 2], [3, 4]])
zeros = np.zeros((3, 3))
ones = np.ones((2, 4))
random_arr = np.random.rand(3, 2)

print(f"1D array: {arr1}")
print(f"2D array:\n{arr2}")
print(f"Zeros array:\n{zeros}")
print(f"Ones array:\n{ones}")
print(f"Random array:\n{random_arr}")

# Array operations
print("\nArray Operations:")
print(f"arr1 + 10: {arr1 + 10}")
print(f"arr1 * 2: {arr1 * 2}")
print(f"arr1 squared: {arr1 ** 2}")
print(f"Sum: {np.sum(arr1)}, Mean: {np.mean(arr1)}, Max: {np.max(arr1)}")

# Indexing and slicing
print("\nIndexing and Slicing:")
print(f"arr1[0]: {arr1[0]}")
print(f"arr1[1:4]: {arr1[1:4]}")
print(f"arr2[0, 1]: {arr2[0, 1]}")
print(f"arr2[:, 0]: {arr2[:, 0]}")

# =============================================
# PART 2: Pandas Basics
# =============================================
print("\n" + "=" * 40)
print("PART 2: Pandas DataFrames")
print("=" * 40)

# Creating DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'Age': [25, 30, 35, 28],
    'City': ['NYC', 'LA', 'Chicago', 'Houston'],
    'Salary': [50000, 60000, 70000, 55000]
}

df = pd.DataFrame(data)
print("Sample DataFrame:")
print(df)

# Basic operations
print("\nBasic Operations:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Index: {list(df.index)}")

# Selecting data
print("\nSelecting Data:")
print(f"df['Name']: {df['Name'].tolist()}")
print(f"df.loc[0]: {df.loc[0].to_dict()}")
print(f"df.iloc[1:3]:\n{df.iloc[1:3]}")

# Filtering
print("\nFiltering:")
high_salary = df[df['Salary'] > 55000]
print(f"High salary (>55000):\n{high_salary}")

# Adding columns
df['Bonus'] = df['Salary'] * 0.1
print(f"\nAfter adding Bonus column:\n{df}")

# Group by
print("\nGroup by City - Average Salary:")
city_avg = df.groupby('City')['Salary'].mean()
print(city_avg.to_dict())

# =============================================
# PART 3: Reading/Writing Data
# =============================================
print("\n" + "=" * 40)
print("PART 3: Reading and Writing Data")
print("=" * 40)

# Create sample CSV data
csv_data = """Name,Age,City,Department
John,28,NYC,Engineering
Sarah,32,LA,Marketing
Mike,45,Chicago,Sales
Emma,29,Houston,HR"""

# Write to CSV
with open('sample_data.csv', 'w') as f:
    f.write(csv_data)

print("Created sample_data.csv")

# Read CSV
df_csv = pd.read_csv('sample_data.csv')
print("\nRead from CSV:")
print(df_csv)

# Basic statistics
print("\nStatistics:")
print(df_csv.describe())

# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
NumPy:
- np.array() for creating arrays
- Mathematical operations: +, -, *, /, **
- Statistical functions: np.sum(), np.mean(), np.max()
- Indexing: arr[0], arr[1:3], arr[:, 0]

Pandas:
- pd.DataFrame() for tabular data
- df['column'] for column access
- df.loc[] and df.iloc[] for row access
- df[df['col'] > value] for filtering
- df.groupby() for aggregation
- pd.read_csv() for reading data

Next: Machine Learning with scikit-learn
""")