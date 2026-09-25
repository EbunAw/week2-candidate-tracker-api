import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


# Load the dataset
df = pd.read_csv("data/customer_churn.csv")

# Display the first 5 rows
print("First 5 rows:")
print(df.head())

# Display information about the dataset
print("\nDataset information:")
print(df.info())

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())

# Check for duplicate rows
print("\nDuplicate rows before cleaning:")
print(df.duplicated().sum())

# Remove duplicate rows
df = df.drop_duplicates()

print("\nDuplicate rows after cleaning:")
print(df.duplicated().sum())

# Separate features and target
X = df.drop("churn", axis=1)
y = df["churn"]

print("\nFeatures (X):")
print(X.head())

print("\nTarget (y):")
print(y.head())

from sklearn.model_selection import train_test_split

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining data:")
print("X_train:", X_train.shape)
print("y_train:", y_train.shape)

print("\nTesting data:")
print("X_test:", X_test.shape)
print("y_test:", y_test.shape)

# Create the model
model = RandomForestClassifier(
    random_state=42
)

# Train the model
model.fit(X_train, y_train)

print("\nModel training completed.")
# Make predictions on the test data
predictions = model.predict(X_test)

print("\nPredictions:")
print(predictions)

print("\nActual values:")
print(y_test.values)
# Calculate evaluation metrics
accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)

# Get probabilities for AUC
probabilities = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, probabilities)

print("\nEvaluation Metrics:")
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
print("AUC:", auc)

# Check training performance for overfitting
train_predictions = model.predict(X_train)

train_accuracy = accuracy_score(y_train, train_predictions)

print("\nTraining Accuracy:", train_accuracy)
print("Testing Accuracy:", accuracy)

# Save the trained model
joblib.dump(model, "models/model.pkl")

print("\nModel saved successfully to models/model.pkl")