"""
machine_learning_tutorial.py - Introduction to Machine Learning with scikit-learn

This tutorial covers:
1. Loading datasets
2. Data preprocessing
3. Training models (Linear Regression, Classification)
4. Model evaluation
5. Making predictions
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.datasets import load_iris, make_regression
import matplotlib.pyplot as plt

print("=" * 60)
print("MACHINE LEARNING TUTORIAL: scikit-learn Basics")
print("=" * 60)

# =============================================
# PART 1: Regression Example
# =============================================
print("\n" + "=" * 40)
print("PART 1: Linear Regression")
print("=" * 40)

# Generate sample data
X, y = make_regression(n_samples=100, n_features=1, noise=10, random_state=42)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training data shape: {X_train.shape}")
print(f"Test data shape: {X_test.shape}")

# Create and train model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse:.2f}")
print(f"Model coefficient: {model.coef_[0]:.2f}")
print(f"Model intercept: {model.intercept_:.2f}")

# =============================================
# PART 2: Classification Example
# =============================================
print("\n" + "=" * 40)
print("PART 2: Classification with Iris Dataset")
print("=" * 40)

# Load iris dataset
iris = load_iris()
X_iris = iris.data
y_iris = iris.target

# Split data
X_train_iris, X_test_iris, y_train_iris, y_test_iris = train_test_split(
    X_iris, y_iris, test_size=0.3, random_state=42
)

print(f"Iris features: {iris.feature_names}")
print(f"Iris target names: {iris.target_names}")
print(f"Training data shape: {X_train_iris.shape}")

# Create and train classifier
clf = LogisticRegression(random_state=42, max_iter=200)
clf.fit(X_train_iris, y_train_iris)

# Make predictions
y_pred_iris = clf.predict(X_test_iris)

# Evaluate
accuracy = accuracy_score(y_test_iris, y_pred_iris)
print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test_iris, y_pred_iris, target_names=iris.target_names))

# =============================================
# PART 3: Making Predictions
# =============================================
print("\n" + "=" * 40)
print("PART 3: Making New Predictions")
print("=" * 40)

# New data for regression
new_X = np.array([[0.5], [1.5], [-0.5]])
new_predictions = model.predict(new_X)
print("New regression predictions:")
for i, pred in enumerate(new_predictions):
    print(f"Input {new_X[i][0]}: Predicted {pred:.2f}")

# New data for classification (iris measurements)
new_iris_data = np.array([[5.1, 3.5, 1.4, 0.2],  # Setosa-like
                          [6.7, 3.0, 5.2, 2.3],  # Virginica-like
                          [5.9, 3.0, 4.2, 1.5]]) # Versicolor-like

new_class_predictions = clf.predict(new_iris_data)
print("\nNew classification predictions:")
for i, pred in enumerate(new_class_predictions):
    species = iris.target_names[pred]
    print(f"Sample {i+1}: Predicted {species}")

# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
scikit-learn Workflow:
1. Load/prepare data
2. Split into train/test sets
3. Choose and train model
4. Make predictions
5. Evaluate performance

Key Functions:
- train_test_split() for data splitting
- model.fit() for training
- model.predict() for predictions
- Various metrics for evaluation

Next: Data Visualization with Matplotlib/Seaborn
""")