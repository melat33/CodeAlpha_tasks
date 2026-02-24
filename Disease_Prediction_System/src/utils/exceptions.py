"""
Custom exceptions for the project.
"""

class DataLoadError(Exception):
    """Raised when data loading fails"""
    pass

class DataValidationError(Exception):
    """Raised when data validation fails"""
    pass

class ModelTrainingError(Exception):
    """Raised when model training fails"""
    pass

class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass