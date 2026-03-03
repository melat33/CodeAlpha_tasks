import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_german_credit_data(file_path):
    """Load and inspect German Credit dataset"""
    df = pd.read_csv(file_path)
    logger.info(f"German Credit dataset loaded successfully")
    logger.info(f"Shape: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")
    return df

def map_german_credit_columns(df):
    """Map German Credit columns to standard names based on typical column patterns"""
    
    # Common column names in German Credit datasets
    column_mapping = {}
    
    # Try to identify target column (usually 'Creditability', 'default', 'Risk', etc.)
    target_keywords = ['creditability', 'default', 'risk', 'class', 'target', 'bad']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in target_keywords):
            column_mapping[col] = 'default_payment'
            logger.info(f"Mapped '{col}' to target variable 'default_payment'")
            break
    
    # If no target found, assume first or last column might be target
    if 'default_payment' not in column_mapping.values():
        column_mapping[df.columns[-1]] = 'default_payment'
        logger.info(f"Assuming last column '{df.columns[-1]}' is target variable")
    
    # Common feature mappings
    feature_keywords = {
        'age': ['age', 'alter'],
        'income': ['income', 'einkommen', 'salary'],
        'debt': ['debt', 'schulden', 'debt_ratio'],
        'credit_lines': ['credit_lines', 'num_credits', 'existing_credits'],
        'late_payments': ['late_payments', 'delinquent', 'default_history'],
        'credit_history': ['credit_history', 'history'],
        'employment': ['employment', 'employed', 'job'],
        'education': ['education', 'bildung'],
        'marital': ['marital', 'status', 'married']
    }
    
    # Rename columns based on keywords
    df_renamed = df.rename(columns=column_mapping)
    
    return df_renamed

def clean_german_credit_data(df):
    """Clean and preprocess German Credit data"""
    
    # Handle missing values
    initial_shape = df.shape
    df = df.dropna()
    logger.info(f"Dropped {initial_shape[0] - df.shape[0]} rows with missing values")
    
    # Convert target to binary if needed
    if 'default_payment' in df.columns:
        # Check if target is already binary
        unique_vals = df['default_payment'].unique()
        if len(unique_vals) > 2:
            # If target has more than 2 values, try to binarize
            # Usually in German Credit: 1=Good, 2=Bad
            if set(unique_vals).issubset({1, 2}):
                df['default_payment'] = (df['default_payment'] == 2).astype(int)
                logger.info("Converted target: 1=Good(0), 2=Bad(1)")
    
    # Remove outliers in numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'default_payment' in numeric_cols:
        numeric_cols.remove('default_payment')
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    
    logger.info(f"Data after cleaning: {df.shape}")
    return df

def engineer_german_features(df):
    """Create additional features from German Credit data"""
    
    # Create derived features based on common German Credit attributes
    
    # Debt-to-income proxy (if we have both)
    if 'debt' in df.columns and 'income' in df.columns:
        df['debt_to_income'] = df['debt'] / df['income'].clip(lower=1)
    
    # Credit utilization proxy
    if 'amount' in df.columns and 'income' in df.columns:
        df['credit_utilization_proxy'] = df['amount'] / df['income'].clip(lower=1)
    
    # Age groups
    if 'age' in df.columns:
        df['age_group'] = pd.cut(df['age'], 
                                  bins=[0, 25, 35, 50, 65, 100],
                                  labels=['Young', 'Early Career', 'Mid Career', 'Pre-Retirement', 'Retirement'])
    
    # Risk score based on available features
    risk_factors = []
    
    if 'credit_history' in df.columns:
        # Assuming categorical with "good" history = lower risk
        pass
    
    if 'duration' in df.columns:
        # Longer duration might indicate higher risk
        df['duration_risk'] = pd.qcut(df['duration'], q=4, labels=False, duplicates='drop')
        risk_factors.append('duration_risk')
    
    # Composite risk score (if we have multiple factors)
    if len(risk_factors) > 0:
        df['composite_risk'] = df[risk_factors].mean(axis=1)
    
    return df

def prepare_features_german(df):
    """Prepare features for modeling"""
    
    # Separate features and target
    if 'default_payment' in df.columns:
        y = df['default_payment']
        X = df.drop('default_payment', axis=1)
    else:
        raise ValueError("Target column 'default_payment' not found")
    
    # Handle categorical variables
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    le_dict = {}
    
    for col in categorical_cols:
        le = LabelEncoder()
        X[col + '_encoded'] = le.fit_transform(X[col].astype(str))
        le_dict[col] = le
        # Drop original categorical column
        X = X.drop(col, axis=1)
    
    # Select only numeric columns for modeling
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    X = X[numeric_cols]
    
    feature_names = numeric_cols
    
    logger.info(f"Prepared {len(feature_names)} features for modeling")
    logger.info(f"Features: {feature_names}")
    
    return X, y, feature_names, le_dict

def split_and_scale_german(X, y, test_size=0.2, random_state=42):
    """Split and scale the data"""
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    logger.info(f"Training set: {X_train.shape[0]} samples")
    logger.info(f"Test set: {X_test.shape[0]} samples")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler