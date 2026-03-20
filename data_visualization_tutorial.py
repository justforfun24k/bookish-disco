"""
data_visualization_tutorial.py - Data Visualization with Matplotlib and Seaborn

This tutorial covers:
1. Basic plotting with Matplotlib
2. Statistical plots with Seaborn
3. Customizing visualizations
4. Combining plots and subplots
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris, make_regression

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=" * 60)
print("DATA VISUALIZATION TUTORIAL: Matplotlib & Seaborn")
print("=" * 60)

# =============================================
# PART 1: Matplotlib Basics
# =============================================
print("\n" + "=" * 40)
print("PART 1: Matplotlib Basics")
print("=" * 40)

# Generate sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Create figure and subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Plot sine wave
ax1.plot(x, y1, 'b-', linewidth=2, label='sin(x)')
ax1.set_title('Sine Wave')
ax1.set_xlabel('x')
ax1.set_ylabel('sin(x)')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot cosine wave
ax2.plot(x, y2, 'r--', linewidth=2, label='cos(x)')
ax2.set_title('Cosine Wave')
ax2.set_xlabel('x')
ax2.set_ylabel('cos(x)')
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig('trig_functions.png', dpi=150, bbox_inches='tight')
print("Saved trig_functions.png")

# =============================================
# PART 2: Scatter Plots and Regression
# =============================================
print("\n" + "=" * 40)
print("PART 2: Scatter Plots and Regression")
print("=" * 40)

# Generate regression data
X_reg, y_reg = make_regression(n_samples=200, n_features=1, noise=20, random_state=42)

plt.figure(figsize=(10, 6))
plt.scatter(X_reg, y_reg, alpha=0.6, color='blue', edgecolors='black', s=50)
plt.title('Scatter Plot with Regression Line', fontsize=14, fontweight='bold')
plt.xlabel('X values', fontsize=12)
plt.ylabel('Y values', fontsize=12)
plt.grid(True, alpha=0.3)

# Add regression line
from sklearn.linear_model import LinearRegression
reg = LinearRegression().fit(X_reg, y_reg)
x_line = np.linspace(X_reg.min(), X_reg.max(), 100).reshape(-1, 1)
y_line = reg.predict(x_line)
plt.plot(x_line, y_line, 'r-', linewidth=3, label=f'y = {reg.coef_[0]:.2f}x + {reg.intercept_:.2f}')
plt.legend()

plt.savefig('scatter_regression.png', dpi=150, bbox_inches='tight')
print("Saved scatter_regression.png")

# =============================================
# PART 3: Seaborn Statistical Plots
# =============================================
print("\n" + "=" * 40)
print("PART 3: Seaborn Statistical Plots")
print("=" * 40)

# Load iris dataset
iris = load_iris()
iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
iris_df['species'] = iris.target_names[iris.target]

# Pair plot
plt.figure(figsize=(12, 8))
pair_plot = sns.pairplot(iris_df, hue='species', diag_kind='kde', height=2.5)
pair_plot.fig.suptitle('Iris Dataset - Pair Plot', y=1.02, fontsize=16, fontweight='bold')
plt.savefig('iris_pairplot.png', dpi=150, bbox_inches='tight')
print("Saved iris_pairplot.png")

# Box plots
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.boxplot(data=iris_df, x='species', y='sepal length (cm)', palette='Set3')
plt.title('Sepal Length by Species')
plt.xticks(rotation=45)

plt.subplot(1, 2, 2)
sns.violinplot(data=iris_df, x='species', y='petal length (cm)', palette='Set2')
plt.title('Petal Length by Species')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('iris_box_violin.png', dpi=150, bbox_inches='tight')
print("Saved iris_box_violin.png")

# =============================================
# PART 4: Advanced Visualizations
# =============================================
print("\n" + "=" * 40)
print("PART 4: Advanced Visualizations")
print("=" * 40)

# Create sample time series data
dates = pd.date_range('2023-01-01', periods=365, freq='D')
np.random.seed(42)
sales = 100 + np.cumsum(np.random.randn(365) * 2) + np.sin(np.arange(365) * 2 * np.pi / 365) * 20
sales_df = pd.DataFrame({'date': dates, 'sales': sales})

# Time series plot
plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
plt.plot(sales_df['date'], sales_df['sales'], color='darkblue', linewidth=1.5)
plt.title('Daily Sales Over Time', fontsize=14, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

# Moving average
sales_df['MA_30'] = sales_df['sales'].rolling(window=30).mean()
plt.plot(sales_df['date'], sales_df['MA_30'], color='red', linewidth=2, label='30-day MA')
plt.legend()

# Histogram with KDE
plt.subplot(1, 2, 2)
sns.histplot(sales_df['sales'], kde=True, color='green', alpha=0.7)
plt.title('Sales Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Sales')
plt.ylabel('Frequency')
plt.axvline(sales_df['sales'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {sales_df["sales"].mean():.1f}')
plt.legend()

plt.tight_layout()
plt.savefig('sales_analysis.png', dpi=150, bbox_inches='tight')
print("Saved sales_analysis.png")

# =============================================
# PART 5: Heatmaps and Correlations
# =============================================
print("\n" + "=" * 40)
print("PART 5: Heatmaps and Correlations")
print("=" * 40)

# Correlation heatmap
plt.figure(figsize=(10, 8))
correlation_matrix = iris_df.drop('species', axis=1).corr()
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
plt.title('Iris Features Correlation Heatmap', fontsize=16, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

plt.savefig('correlation_heatmap.png', dpi=150, bbox_inches='tight')
print("Saved correlation_heatmap.png")

# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
Matplotlib:
- plt.plot() for line plots
- plt.scatter() for scatter plots
- plt.subplots() for multiple plots
- plt.savefig() to save figures

Seaborn:
- sns.pairplot() for pairwise relationships
- sns.boxplot() and sns.violinplot() for distributions
- sns.heatmap() for correlations
- Built-in statistical plotting

Best Practices:
- Use plt.style.use() for consistent styling
- Add titles, labels, and legends
- Use subplots for multiple visualizations
- Save high-quality figures with plt.savefig()

Next: Web Development with Flask/Django or Advanced ML
""")

print("\nVisualization files saved:")
print("- trig_functions.png")
print("- scatter_regression.png")
print("- iris_pairplot.png")
print("- iris_box_violin.png")
print("- sales_analysis.png")
print("- correlation_heatmap.png")