import pandas as pd
import numpy as np
from datetime import datetime

def create_financial_features(df):
    """Create advanced financial features"""
    
    # Debt-to-income ratio (if not present)
    if 'debt_ratio' not in df.columns:
        df['debt_ratio'] = df['total_debt'] / df['income']
    
    # Payment history score
    df['payment_history_score'] = (
        (df['on_time_payments'] / df['total_payments']) * 100
    ).fillna(0)
    
    # Credit utilization trend
    df['utilization_trend'] = (
        df['current_utilization'] - df['avg_utilization_6m']
    ) / df['avg_utilization_6m'].replace(0, 1)
    
    # Risk indicators
    df['high_risk_flag'] = (
        (df['late_payments_12m'] > 3) | 
        (df['credit_utilization'] > 0.9)
    ).astype(int)
    
    # Credit age categories
    df['credit_age_category'] = pd.cut(
        df['credit_history_years'],
        bins=[0, 2, 5, 10, 20, 100],
        labels=['very_short', 'short', 'medium', 'long', 'very_long']
    )
    
    # Income stability score
    df['income_stability'] = 1 / (1 + df['income_volatility'].fillna(0.1))
    
    # Composite risk score
    df['composite_risk_score'] = (
        df['late_payments_12m'] * 0.3 +
        df['credit_utilization'] * 0.2 +
        df['debt_ratio'] * 0.2 +
        (1 - df['payment_history_score']/100) * 0.3
    )
    
    return df

def calculate_credit_metrics(df):
    """Calculate credit-related metrics"""
    
    # Credit mix score
    credit_types = ['mortgage', 'auto_loan', 'credit_card', 'personal_loan']
    df['credit_mix_score'] = df[credit_types].sum(axis=1) / len(credit_types)
    
    # Recent inquiries impact
    df['inquiry_impact'] = np.where(
        df['recent_inquiries'] > 5, -20,
        np.where(df['recent_inquiries'] > 2, -10, 0)
    )
    
    # Balance growth rate
    df['balance_growth_rate'] = (
        (df['current_balance'] - df['balance_6m_ago']) / 
        df['balance_6m_ago'].replace(0, 1)
    ).clip(-1, 2)
    
    return df