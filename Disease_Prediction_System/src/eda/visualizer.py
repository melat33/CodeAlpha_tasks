"""
Professional visualization module with publication-quality plots.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings

from ..config.settings import ProjectConfig

logger = logging.getLogger(__name__)

class EDAVisualizer:
    """
    Professional visualization class for comprehensive EDA plots.
    Produces publication-quality visualizations with multiple formats.
    """
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.output_dir = config.get_report_path('eda')
        self.setup_style()
        
    def setup_style(self):
        """Set up professional plotting style"""
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Custom color palette
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#4ECDC4',
            'danger': '#FF6B6B',
            'warning': '#FFE66D',
            'info': '#6C91C2',
            'light': '#F7F7F7',
            'dark': '#373737'
        }
        
        # Set color cycle
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=list(self.colors.values()))
        
        # Font settings
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['figure.titlesize'] = 16
        
    def create_dashboard(self, df: pd.DataFrame, analysis_results: Dict) -> None:
        """
        Create comprehensive visualization dashboard
        
        Args:
            df: Input DataFrame
            analysis_results: Results from EDAnalyzer
        """
        logger.info("Creating comprehensive visualization dashboard")
        
        # Create individual plots
        self.plot_target_distribution(df)
        self.plot_numeric_distributions(df)
        self.plot_categorical_distributions(df)
        self.plot_correlation_heatmap(df)
        self.plot_missing_values(df)
        self.plot_outliers(df)
        self.plot_pairplot(df)
        self.plot_feature_importance(df)
        
        # Create combined dashboard
        self.create_summary_dashboard(df)
        
        logger.info(f"All plots saved to {self.output_dir}")
    
    def plot_target_distribution(self, df: pd.DataFrame) -> None:
        """Plot target variable distribution"""
        if 'target' not in df.columns:
            return
            
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Count plot
        ax = axes[0]
        target_counts = df['target'].value_counts()
        bars = ax.bar(['No Disease', 'Disease'], target_counts.values, 
                      color=[self.colors['success'], self.colors['danger']])
        ax.set_title('Target Distribution', fontweight='bold', pad=20)
        ax.set_ylabel('Count')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        # Pie chart
        ax = axes[1]
        wedges, texts, autotexts = ax.pie(target_counts.values, 
                                          labels=['No Disease', 'Disease'],
                                          autopct='%1.1f%%',
                                          colors=[self.colors['success'], self.colors['danger']],
                                          startangle=90)
        ax.set_title('Target Distribution (%)', fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'target_distribution.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_numeric_distributions(self, df: pd.DataFrame) -> None:
        """Plot distributions of numeric features"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if 'target' in numeric_cols:
            numeric_cols = numeric_cols.drop('target')
        
        if len(numeric_cols) == 0:
            return
        
        n_cols = len(numeric_cols)
        n_rows = (n_cols + 3) // 4  # 4 plots per row
        
        fig, axes = plt.subplots(n_rows, 4, figsize=(20, n_rows * 4))
        axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols):
            ax = axes[i]
            
            if 'target' in df.columns:
                # Plot by target class
                for target in [0, 1]:
                    subset = df[df['target'] == target][col].dropna()
                    if len(subset) > 0:
                        sns.kdeplot(subset, label=f'Target {target}', ax=ax, 
                                   fill=True, alpha=0.5)
                ax.legend(['No Disease', 'Disease'])
            else:
                # Simple histogram
                ax.hist(df[col].dropna(), bins=30, alpha=0.7, 
                       color=self.colors['primary'], edgecolor='black')
            
            ax.set_title(f'{col}', fontweight='bold')
            ax.set_xlabel(col)
            ax.set_ylabel('Density')
            
            # Add statistics
            mean_val = df[col].mean()
            median_val = df[col].median()
            ax.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='--', label=f'Median: {median_val:.2f}')
        
        # Hide unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        
        plt.suptitle('Numeric Feature Distributions', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'numeric_distributions.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_categorical_distributions(self, df: pd.DataFrame) -> None:
        """Plot distributions of categorical features"""
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) == 0:
            return
        
        n_cols = len(categorical_cols)
        n_rows = (n_cols + 3) // 4
        
        fig, axes = plt.subplots(n_rows, 4, figsize=(20, n_rows * 4))
        axes = axes.flatten()
        
        for i, col in enumerate(categorical_cols):
            ax = axes[i]
            
            # Get value counts
            if 'target' in df.columns:
                # Stacked bar chart by target
                crosstab = pd.crosstab(df[col], df['target'], normalize='index') * 100
                crosstab.plot(kind='bar', stacked=True, ax=ax,
                            color=[self.colors['success'], self.colors['danger']])
                ax.set_ylabel('Percentage')
                ax.legend(['No Disease', 'Disease'], loc='upper right')
            else:
                # Simple bar chart
                value_counts = df[col].value_counts().head(10)
                value_counts.plot(kind='bar', ax=ax, color=self.colors['primary'])
                ax.set_ylabel('Count')
            
            ax.set_title(f'{col}', fontweight='bold')
            ax.set_xlabel(col)
            ax.tick_params(axis='x', rotation=45)
        
        # Hide unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        
        plt.suptitle('Categorical Feature Distributions', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'categorical_distributions.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_correlation_heatmap(self, df: pd.DataFrame) -> None:
        """Plot correlation heatmap for numeric features"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return
        
        corr = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(14, 12))
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(corr, dtype=bool))
        
        # Heatmap
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                   center=0, square=True, linewidths=0.5, ax=ax,
                   cbar_kws={"shrink": 0.8})
        
        ax.set_title('Feature Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'correlation_heatmap.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_missing_values(self, df: pd.DataFrame) -> None:
        """Plot missing value analysis"""
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        
        if len(missing) == 0:
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar plot
        ax = axes[0]
        bars = ax.bar(range(len(missing)), missing.values, color=self.colors['danger'])
        ax.set_xticks(range(len(missing)))
        ax.set_xticklabels(missing.index, rotation=45, ha='right')
        ax.set_title('Missing Values by Column', fontweight='bold')
        ax.set_ylabel('Missing Count')
        
        # Add value labels
        for bar, val in zip(bars, missing.values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val}', ha='center', va='bottom')
        
        # Pie chart of missing vs complete
        ax = axes[1]
        total_missing = missing.sum()
        total_cells = df.shape[0] * df.shape[1]
        complete = total_cells - total_missing
        
        wedges, texts, autotexts = ax.pie([total_missing, complete],
                                          labels=['Missing', 'Complete'],
                                          autopct='%1.1f%%',
                                          colors=[self.colors['danger'], self.colors['success']],
                                          startangle=90)
        ax.set_title('Overall Missing Data', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'missing_values.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_outliers(self, df: pd.DataFrame) -> None:
        """Plot outlier analysis using boxplots"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if 'target' in numeric_cols:
            numeric_cols = numeric_cols.drop('target')
        
        if len(numeric_cols) == 0:
            return
        
        n_cols = len(numeric_cols)
        n_rows = (n_cols + 3) // 4
        
        fig, axes = plt.subplots(n_rows, 4, figsize=(20, n_rows * 5))
        axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols):
            ax = axes[i]
            
            data_to_plot = [df[df['target'] == 0][col].dropna() if 'target' in df.columns else df[col].dropna(),
                           df[df['target'] == 1][col].dropna() if 'target' in df.columns else []]
            
            bp = ax.boxplot(data_to_plot, patch_artist=True,
                           labels=['No Disease', 'Disease'] if 'target' in df.columns else ['All'])
            
            # Color boxes
            if 'target' in df.columns:
                bp['boxes'][0].set_facecolor(self.colors['success'])
                bp['boxes'][1].set_facecolor(self.colors['danger'])
            
            ax.set_title(f'{col}', fontweight='bold')
            ax.set_ylabel('Value')
            ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        
        plt.suptitle('Outlier Analysis - Boxplots', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'outliers.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_pairplot(self, df: pd.DataFrame) -> None:
        """Create pairplot for selected features"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 10:  # Limit to top 10 features
            # Select top features based on correlation with target
            if 'target' in numeric_cols:
                correlations = df[numeric_cols].corr()['target'].abs().sort_values(ascending=False)
                top_features = correlations.head(6).index.tolist()  # Include target
                if 'target' in top_features:
                    top_features.remove('target')
                top_features = top_features[:5]  # Top 5 features
                if 'target' not in top_features:
                    top_features.append('target')
            else:
                top_features = numeric_cols[:6]
        else:
            top_features = numeric_cols.tolist()
        
        if len(top_features) < 2:
            return
        
        # Create pairplot
        g = sns.pairplot(df[top_features], hue='target' if 'target' in top_features else None,
                        palette=[self.colors['success'], self.colors['danger']],
                        diag_kind='kde', plot_kws={'alpha': 0.6})
        
        g.fig.suptitle('Feature Pairplot Analysis', y=1.02, fontsize=16, fontweight='bold')
        
        plt.savefig(self.output_dir / 'pairplot.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_feature_importance(self, df: pd.DataFrame) -> None:
        """Plot feature importance using correlation with target"""
        if 'target' not in df.columns:
            return
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if 'target' in numeric_cols:
            numeric_cols = numeric_cols.drop('target')
        
        if len(numeric_cols) == 0:
            return
        
        # Calculate correlation with target
        correlations = abs(df[numeric_cols].corrwith(df['target'])).sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, max(6, len(numeric_cols) * 0.3)))
        
        # Horizontal bar plot
        colors = [self.colors['primary'] if c < 0.3 else 
                 self.colors['warning'] if c < 0.5 else 
                 self.colors['success'] for c in correlations.values]
        
        bars = ax.barh(range(len(correlations)), correlations.values, color=colors)
        ax.set_yticks(range(len(correlations)))
        ax.set_yticklabels(correlations.index)
        ax.set_xlabel('Absolute Correlation with Target')
        ax.set_title('Feature Importance (Correlation with Target)', fontweight='bold')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, correlations.values)):
            width = bar.get_width()
            ax.text(width + 0.01, i, f'{val:.3f}', va='center')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'feature_importance.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_summary_dashboard(self, df: pd.DataFrame) -> None:
        """Create summary dashboard with key plots"""
        fig = plt.figure(figsize=(20, 15))
        
        # Create grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Target distribution
        ax1 = fig.add_subplot(gs[0, 0])
        if 'target' in df.columns:
            target_counts = df['target'].value_counts()
            ax1.pie(target_counts.values, labels=['No Disease', 'Disease'],
                   autopct='%1.1f%%', colors=[self.colors['success'], self.colors['danger']])
            ax1.set_title('Target Distribution', fontweight='bold')
        
        # 2. Missing values
        ax2 = fig.add_subplot(gs[0, 1])
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=False)
        if len(missing_pct) > 0:
            ax2.bar(range(len(missing_pct)), missing_pct.values, color=self.colors['danger'])
            ax2.set_xticks(range(len(missing_pct)))
            ax2.set_xticklabels(missing_pct.index, rotation=45, ha='right', fontsize=8)
            ax2.set_title('Missing Values (%)', fontweight='bold')
            ax2.set_ylabel('Percentage')
        
        # 3. Feature correlations
        ax3 = fig.add_subplot(gs[0, 2])
        if 'target' in df.columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr = df[numeric_cols].corr()['target'].drop('target').sort_values(ascending=False).head(10)
                ax3.barh(range(len(corr)), corr.values, color=self.colors['primary'])
                ax3.set_yticks(range(len(corr)))
                ax3.set_yticklabels(corr.index)
                ax3.set_title('Top 10 Feature Correlations', fontweight='bold')
                ax3.set_xlabel('Correlation')
        
        # 4-6. Top 3 numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if 'target' in numeric_cols:
            numeric_cols = numeric_cols.drop('target')
        
        for i, col in enumerate(numeric_cols[:3]):
            ax = fig.add_subplot(gs[1, i])
            if 'target' in df.columns:
                for target in [0, 1]:
                    subset = df[df['target'] == target][col].dropna()
                    if len(subset) > 0:
                        sns.kdeplot(subset, ax=ax, label=f'Target {target}', 
                                   fill=True, alpha=0.5)
                ax.legend(['No Disease', 'Disease'], fontsize=8)
            else:
                ax.hist(df[col].dropna(), bins=30, alpha=0.7, color=self.colors['primary'])
            ax.set_title(f'{col}', fontweight='bold')
            ax.set_xlabel(col)
        
        # 7-9. Boxplots
        for i, col in enumerate(numeric_cols[3:6]):
            ax = fig.add_subplot(gs[2, i])
            if 'target' in df.columns:
                data_to_plot = [df[df['target'] == 0][col].dropna(),
                               df[df['target'] == 1][col].dropna()]
                bp = ax.boxplot(data_to_plot, labels=['No', 'Yes'])
                bp['boxes'][0].set_color(self.colors['success'])
                bp['boxes'][1].set_color(self.colors['danger'])
            else:
                ax.boxplot(df[col].dropna())
            ax.set_title(f'{col}', fontweight='bold')
        
        plt.suptitle(f'{self.config.model.name.upper()} - EDA Summary Dashboard', 
                    fontsize=20, fontweight='bold', y=1.02)
        
        plt.savefig(self.output_dir / 'summary_dashboard.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()