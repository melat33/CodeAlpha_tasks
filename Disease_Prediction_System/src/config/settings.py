"""
Centralized configuration management for the entire project.
Supports multiple environments, model versions, and datasets.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import yaml
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    username: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "disease_prediction")
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class ModelConfig:
    """Model-specific configuration"""
    name: str
    version: str = "1.0.0"
    algorithms: List[str] = field(default_factory=lambda: ['lr', 'svm', 'rf', 'xgb'])
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    cv_folds: int = 5
    test_size: float = 0.2
    random_state: int = 42
    scoring_metric: str = "f1"

@dataclass
class DataConfig:
    """Data processing configuration"""
    raw_data_path: Path
    processed_data_path: Path
    missing_threshold: float = 0.3
    outlier_method: str = "iqr"
    scaling_method: str = "robust"
    handle_imbalance: bool = True
    imbalance_method: str = "smote"
    
    def __post_init__(self):
        self.raw_data_path = Path(self.raw_data_path)
        self.processed_data_path = Path(self.processed_data_path)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)

@dataclass
class ProjectConfig:
    """Main configuration class"""
    
    dataset_name: str
    root_dir: Path = Path(__file__).parent.parent.parent
    
    # Model settings
    model: ModelConfig = field(default_factory=lambda: ModelConfig(name="default"))
    
    # Data settings
    data: DataConfig = None
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5
    
    # Paths
    raw_data_path: Path = None
    processed_data_path: Path = None
    
    def __post_init__(self):
        if self.raw_data_path is None:
            self.raw_data_path = self.root_dir / "data" / "raw" / f"{self.dataset_name}.csv"
        if self.processed_data_path is None:
            self.processed_data_path = self.root_dir / "data" / "processed" / self.dataset_name
            self.processed_data_path.mkdir(parents=True, exist_ok=True)
        if self.data is None:
            self.data = DataConfig(
                raw_data_path=self.raw_data_path,
                processed_data_path=self.processed_data_path
            )
    
    @classmethod
    def load(cls, dataset_name: str, env: str = "development") -> "ProjectConfig":
        """Load configuration for specific dataset"""
        return cls(dataset_name=dataset_name)
    
    def get_model_save_path(self, version: Optional[str] = None) -> Path:
        """Get path to save model"""
        version = version or self.model.version
        path = self.root_dir / "models" / self.dataset_name / version
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_report_path(self, report_type: str) -> Path:
        """Get path to save reports"""
        path = self.root_dir / "reports" / report_type / self.dataset_name
        path.mkdir(parents=True, exist_ok=True)
        return path