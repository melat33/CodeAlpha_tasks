"""
Simplified configuration without YAML dependencies
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ProjectConfig:
    """Simplified configuration class"""
    
    dataset_name: str
    root_dir: Path = Path(__file__).parent.parent.parent
    
    # Model settings
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5
    
    # Data settings
    missing_threshold: float = 0.3
    
    @classmethod
    def load(cls, dataset_name: str) -> "ProjectConfig":
        """Load configuration without YAML files"""
        return cls(dataset_name=dataset_name)
    
    def get_model_save_path(self) -> Path:
        """Get path to save model"""
        path = self.root_dir / "models" / self.dataset_name
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_report_path(self, report_type: str) -> Path:
        """Get path to save reports"""
        path = self.root_dir / "reports" / report_type / self.dataset_name
        path.mkdir(parents=True, exist_ok=True)
        return path