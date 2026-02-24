"""
Outlier detection utilities.
"""

import numpy as np
import pandas as pd

def detect_outliers_iqr(df, columns=None, factor=1.5):
    """
    Detect outliers using IQR method
    
    Args:
        df: Input DataFrame
        columns: List of columns to check
        factor: IQR multiplier
    
    Returns:
        dict: Outlier information for each column
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    
    results = {}
    
    for col in columns:
        if col in df.columns:
            data = df[col].dropna()
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - factor * IQR
            upper = Q3 + factor * IQR
            
            outliers = data[(data < lower) | (data > upper)]
            
            results[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(data)) * 100 if len(data) > 0 else 0,
                'lower_bound': lower,
                'upper_bound': upper,
                'min': data.min(),
                'max': data.max()
            }
    
    return results