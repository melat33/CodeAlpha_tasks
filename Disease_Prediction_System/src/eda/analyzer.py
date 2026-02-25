"""
Advanced Exploratory Data Analysis with statistical testing and insights.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway, kruskal
import statsmodels.api as sm
from statsmodels.formula.api import ols
import warnings

from ..config.settings import ProjectConfig
from ..utils.decorators import timer, log_execution

logger = logging.getLogger(__name__)

@dataclass
class StatisticalTest:
    """Statistical test results"""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    interpretation: str

@dataclass
class FeatureInsight:
    """Insights about a feature"""
    feature: str
    data_type: str
    missing_pct: float
    unique_values: int
    statistics: Dict[str, float]
    outliers: Dict[str, Any]
    distribution: str
    recommendations: List[str]

class EDAnalyzer:
    """
    Professional EDA analyzer with statistical tests and automated insights.
    """
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.insights = []
        
    @timer
    @log_execution
    def comprehensive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive EDA with statistical tests
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with all analysis results
        """
        logger.info("Starting comprehensive EDA analysis")
        
        results = {
            'overview': self._analyze_overview(df),
            'univariate': self._analyze_univariate(df),
            'bivariate': self._analyze_bivariate(df),
            'multivariate': self._analyze_multivariate(df),
            'statistical_tests': self._run_statistical_tests(df),
            'insights': self._generate_insights(df),
            'recommendations': self._generate_recommendations(df)
        }
        
        logger.info(f"EDA completed: {len(results['insights'])} insights generated")
        return results
    
    def _analyze_overview(self, df: pd.DataFrame) -> Dict:
        """Basic dataset overview"""
        return {
            'shape': {
                'rows': df.shape[0],
                'columns': df.shape[1]
            },
            'data_types': df.dtypes.astype(str).to_dict(),
            'memory_usage': {
                'total_mb': df.memory_usage(deep=True).sum() / 1024**2,
                'per_column': (df.memory_usage(deep=True) / 1024**2).to_dict()
            },
            'completeness': {
                'complete_rows': len(df.dropna()),
                'complete_percentage': (len(df.dropna()) / len(df)) * 100,
                'columns_with_missing': df.columns[df.isnull().any()].tolist()
            }
        }
    
    def _analyze_univariate(self, df: pd.DataFrame) -> Dict:
        """Univariate analysis for each feature"""
        results = {}
        
        for col in df.columns:
            col_data = df[col].dropna()
            
            if pd.api.types.is_numeric_dtype(df[col]):
                # Numerical feature analysis
                results[col] = {
                    'type': 'numerical',
                    'count': len(col_data),
                    'missing': df[col].isnull().sum(),
                    'missing_pct': (df[col].isnull().sum() / len(df)) * 100,
                    'statistics': {
                        'mean': float(col_data.mean()),
                        'median': float(col_data.median()),
                        'mode': float(col_data.mode()[0]) if not col_data.mode().empty else None,
                        'std': float(col_data.std()),
                        'var': float(col_data.var()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'range': float(col_data.max() - col_data.min()),
                        'q1': float(col_data.quantile(0.25)),
                        'q3': float(col_data.quantile(0.75)),
                        'iqr': float(col_data.quantile(0.75) - col_data.quantile(0.25))
                    },
                    'shape': {
                        'skewness': float(col_data.skew()),
                        'kurtosis': float(col_data.kurtosis()),
                        'is_normal': self._test_normality(col_data)
                    },
                    'outliers': self._detect_outliers_iqr(col_data)
                }
            else:
                # Categorical feature analysis
                value_counts = col_data.value_counts()
                results[col] = {
                    'type': 'categorical',
                    'count': len(col_data),
                    'missing': df[col].isnull().sum(),
                    'missing_pct': (df[col].isnull().sum() / len(df)) * 100,
                    'unique_values': col_data.nunique(),
                    'top_values': value_counts.head(10).to_dict(),
                    'value_frequencies': (value_counts / len(col_data) * 100).head(10).to_dict(),
                    'entropy': self._calculate_entropy(col_data)
                }
        
        return results
    
    def _analyze_bivariate(self, df: pd.DataFrame) -> Dict:
        """Bivariate analysis with target variable"""
        if 'target' not in df.columns:
            return {}
        
        results = {}
        target = df['target']
        
        for col in df.columns:
            if col == 'target':
                continue
                
            if pd.api.types.is_numeric_dtype(df[col]):
                # Numerical vs Target analysis
                group0 = df[df['target'] == 0][col].dropna()
                group1 = df[df['target'] == 1][col].dropna()
                
                # Statistical tests
                t_stat, t_pval = stats.ttest_ind(group0, group1)
                u_stat, u_pval = stats.mannwhitneyu(group0, group1, alternative='two-sided')
                
                # Effect size (Cohen's d)
                pooled_std = np.sqrt((group0.std()**2 + group1.std()**2) / 2)
                cohens_d = abs(group0.mean() - group1.mean()) / pooled_std if pooled_std > 0 else 0
                
                results[col] = {
                    'type': 'numerical_vs_target',
                    'group_stats': {
                        'target_0': {
                            'mean': float(group0.mean()),
                            'median': float(group0.median()),
                            'std': float(group0.std())
                        },
                        'target_1': {
                            'mean': float(group1.mean()),
                            'median': float(group1.median()),
                            'std': float(group1.std())
                        }
                    },
                    'statistical_tests': {
                        't_test': {
                            'statistic': float(t_stat),
                            'p_value': float(t_pval),
                            'significant': t_pval < 0.05
                        },
                        'mann_whitney': {
                            'statistic': float(u_stat),
                            'p_value': float(u_pval),
                            'significant': u_pval < 0.05
                        }
                    },
                    'effect_size': {
                        'cohens_d': float(cohens_d),
                        'interpretation': self._interpret_cohens_d(cohens_d)
                    }
                }
            else:
                # Categorical vs Target analysis
                contingency = pd.crosstab(df[col], df['target'])
                
                # Chi-square test
                chi2, pval, dof, expected = chi2_contingency(contingency)
                
                # Cramer's V for effect size
                n = len(df)
                min_dim = min(contingency.shape) - 1
                cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
                
                results[col] = {
                    'type': 'categorical_vs_target',
                    'contingency_table': contingency.to_dict(),
                    'statistical_tests': {
                        'chi_square': {
                            'statistic': float(chi2),
                            'p_value': float(pval),
                            'dof': int(dof),
                            'significant': pval < 0.05
                        }
                    },
                    'effect_size': {
                        'cramers_v': float(cramers_v),
                        'interpretation': self._interpret_cramers_v(cramers_v)
                    }
                }
        
        return results
    
    def _analyze_multivariate(self, df: pd.DataFrame) -> Dict:
        """Multivariate analysis"""
        results = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            # Correlation analysis
            corr_matrix = df[numeric_cols].corr()
            
            # Find highly correlated pairs
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        high_corr.append({
                            'feature1': corr_matrix.columns[i],
                            'feature2': corr_matrix.columns[j],
                            'correlation': float(corr_val)
                        })
            
            results['correlations'] = {
                'matrix': corr_matrix.to_dict(),
                'high_correlations': high_corr
            }
            
            # PCA analysis for dimensionality insight
            if len(numeric_cols) > 2:
                from sklearn.decomposition import PCA
                from sklearn.preprocessing import StandardScaler
                
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(df[numeric_cols].fillna(df[numeric_cols].mean()))
                
                pca = PCA()
                pca.fit(scaled_data)
                
                results['pca'] = {
                    'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                    'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
                    'components_needed_95': np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.95) + 1
                }
        
        return results
    
    def _run_statistical_tests(self, df: pd.DataFrame) -> Dict:
        """Run comprehensive statistical tests"""
        results = {}
        
        # Test for normality on numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        normality_tests = {}
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) >= 8:
                stat, pval = stats.normaltest(col_data)
                normality_tests[col] = {
                    'statistic': float(stat),
                    'p_value': float(pval),
                    'is_normal': pval > 0.05
                }
        
        results['normality'] = normality_tests
        
        # Test for homoscedasticity
        if 'target' in df.columns and len(numeric_cols) > 1:
            groups = [df[df['target'] == i][col].dropna() for i in df['target'].unique()]
            if all(len(g) > 0 for g in groups):
                stat, pval = stats.levene(*groups)
                results['homoscedasticity'] = {
                    'test': 'levene',
                    'statistic': float(stat),
                    'p_value': float(pval),
                    'equal_variance': pval > 0.05
                }
        
        return results
    
    def _generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate natural language insights"""
        insights = []
        
        # Dataset size insight
        insights.append(f"Dataset contains {df.shape[0]:,} patients with {df.shape[1]} features")
        
        # Missing data insight
        missing_total = df.isnull().sum().sum()
        if missing_total > 0:
            insights.append(f"Found {missing_total} missing values across the dataset")
        
        # Class balance insight
        if 'target' in df.columns:
            target_dist = df['target'].value_counts(normalize=True)
            minority_pct = target_dist.min() * 100
            if minority_pct < 30:
                insights.append(f"⚠️ Imbalanced dataset: minority class is only {minority_pct:.1f}%")
        
        # Feature insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:5]:  # Limit to top 5
            col_data = df[col].dropna()
            skew = col_data.skew()
            if abs(skew) > 1:
                insights.append(f"📊 {col} is highly skewed ({skew:.2f}) - consider transformation")
        
        return insights
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Missing value recommendations
        missing_pct = df.isnull().sum() / len(df) * 100
        high_missing = missing_pct[missing_pct > 5]
        if not high_missing.empty:
            for col, pct in high_missing.items():
                recommendations.append(f"Handle missing values in {col} ({pct:.1f}% missing)")
        
        # Outlier recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            outliers = self._detect_outliers_iqr(df[col].dropna())
            if outliers['count'] > 0:
                pct = outliers['percentage']
                if pct > 5:
                    recommendations.append(f"Consider capping outliers in {col} ({pct:.1f}% outliers)")
        
        # Scaling recommendations
        for col in numeric_cols:
            col_data = df[col].dropna()
            if col_data.std() > 100:  # Large scale difference
                recommendations.append(f"Scale {col} due to large magnitude differences")
        
        # Class imbalance recommendation
        if 'target' in df.columns:
            target_dist = df['target'].value_counts(normalize=True)
            if target_dist.min() < 0.3:
                recommendations.append("Apply SMOTE or class weights to handle imbalance")
        
        return recommendations[:10]  # Return top 10
    
    def _detect_outliers_iqr(self, data: pd.Series) -> Dict:
        """Detect outliers using IQR method"""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        
        outliers = data[(data < lower) | (data > upper)]
        
        return {
            'count': len(outliers),
            'percentage': (len(outliers) / len(data)) * 100,
            'lower_bound': float(lower),
            'upper_bound': float(upper),
            'outlier_values': outliers.tolist()[:10]  # First 10 outliers
        }
    
    def _test_normality(self, data: pd.Series) -> Dict:
        """Test if data follows normal distribution"""
        if len(data) < 8:
            return {'is_normal': None, 'reason': 'Insufficient data'}
        
        stat, pval = stats.normaltest(data)
        
        return {
            'is_normal': pval > 0.05,
            'p_value': float(pval),
            'statistic': float(stat)
        }
    
    def _calculate_entropy(self, data: pd.Series) -> float:
        """Calculate entropy for categorical data"""
        value_counts = data.value_counts(normalize=True)
        return float(-sum(value_counts * np.log2(value_counts)))
    
    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size"""
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"
    
    def _interpret_cramers_v(self, v: float) -> str:
        """Interpret Cramer's V effect size"""
        if v < 0.1:
            return "negligible"
        elif v < 0.3:
            return "small"
        elif v < 0.5:
            return "medium"
        else:
            return "large"