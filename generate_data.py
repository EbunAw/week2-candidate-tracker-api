import pandas as pd
import numpy as np

# Make the results reproducible
np.random.seed(42)

# Number of customers
n = 500

# Generate customer information
tenure = np.random.randint(1, 61, n)
monthly_charges = np.random.randint(30, 121, n)

contract_type = np.random.choice(
    [0, 1],
    size=n,
    p=[0.6, 0.4]
)

payment_method = np.random.choice(
    [0, 1],
    size=n
)

# Calculate churn probability
churn_probability = (
    0.45
    - (tenure * 0.005)
    + (monthly_charges * 0.002)
    - (contract_type * 0.15)
    + np.random.normal(0, 0.12, n)
)

# Convert probability into churn outcome
churn = (churn_probability > 0.45).astype(int)

# Create DataFrame
df = pd.DataFrame({
    "tenure": tenure,
    "monthly_charges": monthly_charges,
    "contract_type": contract_type,
    "payment_method": payment_method,
    "churn": churn
})

# Save dataset
df.to_csv("data/customer_churn.csv", index=False)

print("Dataset created successfully.")
print("\nDataset shape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nChurn distribution:")
print(df["churn"].value_counts())

print("\nDuplicate rows:")
print(df.duplicated().sum())