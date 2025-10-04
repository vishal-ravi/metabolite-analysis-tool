"""
Configuration Module

This module contains configuration constants and settings for the
Metabolite Analysis Tool.

Author: vishal ravi
Date: October 2024
"""

from pathlib import Path

# Application Information
APP_NAME = "Metabolite Analysis Tool"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A tool for processing SMILES data and mapping metabolite names in Excel files"

# Default File Paths
DEFAULT_INPUT_FILE = "swissadmet 92.xlsx"
DEFAULT_OUTPUT_FILE = "output_with_formulas.xlsx"
DEFAULT_BACKUP_SUFFIX = "_backup"

# Default Column Names
class ColumnNames:
    """Default column names used throughout the application."""
    
    # SMILES related columns
    SMILES_VARIATIONS = ["smiles", "SMILES", "Smiles"]
    
    # Formula related columns
    FORMULA = "Formula"
    CHEMICAL_FORMULA = "chemical_formula"
    
    # Metabolite related columns
    METABOLITE_NAME = "Metabolite name"
    
    # Reference sheet columns
    REFERENCE_FORMULA_COL = "chemical_formula"
    REFERENCE_METABOLITE_COL = "Metabolite name"

# Default Sheet Names
class SheetNames:
    """Default sheet names and reference sheet settings."""
    
    REFERENCE_SHEET = "Sheet1"
    EXCLUDED_SHEETS = []  # Sheets to exclude from processing

# Processing Settings
class ProcessingSettings:
    """Settings for data processing operations."""
    
    # SMILES processing
    HANDLE_INVALID_SMILES = True
    INVALID_SMILES_VALUE = "Invalid"
    ERROR_SMILES_VALUE = "Error"
    
    # Formula generation
    ADD_FORMULA_TO_ALL_SHEETS = True
    OVERWRITE_EXISTING_FORMULA = False
    
    # Metabolite mapping
    ADD_METABOLITE_TO_NON_REFERENCE = True
    OVERWRITE_EXISTING_METABOLITE = False
    USE_FIRST_OCCURRENCE_FOR_DUPLICATES = True
    
    # Data validation
    VALIDATE_INPUT_FILE = True
    CREATE_BACKUP = True
    PRESERVE_ORIGINAL_DATA = True

# Logging Configuration
class LoggingConfig:
    """Logging configuration settings."""
    
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Log file settings
    ENABLE_FILE_LOGGING = False
    LOG_FILE = "metabolite_analysis.log"
    MAX_LOG_SIZE_MB = 10
    MAX_LOG_FILES = 5

# Output Settings
class OutputSettings:
    """Settings for output generation."""
    
    # Excel output
    EXCEL_ENGINE = "openpyxl"
    INCLUDE_INDEX = False
    
    # Report generation
    GENERATE_SUMMARY_REPORT = True
    SHOW_STATISTICS = True
    SHOW_UNMATCHED_FORMULAS = True
    
    # Verbose output
    VERBOSE_PROCESSING = False
    SHOW_PROGRESS = True

# Error Handling
class ErrorHandling:
    """Error handling configuration."""
    
    CONTINUE_ON_SHEET_ERROR = True
    CONTINUE_ON_FORMULA_ERROR = True
    CONTINUE_ON_MAPPING_ERROR = True
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1

# Validation Rules
class ValidationRules:
    """Data validation rules and thresholds."""
    
    # Minimum success rates (as percentages)
    MIN_FORMULA_SUCCESS_RATE = 90.0
    MIN_METABOLITE_MAPPING_RATE = 80.0
    
    # File validation
    MAX_FILE_SIZE_MB = 100
    MIN_ROWS_PER_SHEET = 1
    
    # Data quality checks
    CHECK_DUPLICATE_FORMULAS = True
    CHECK_EMPTY_CELLS = True
    WARN_ON_LOW_SUCCESS_RATE = True

# Performance Settings
class PerformanceSettings:
    """Performance optimization settings."""
    
    # Memory management
    CHUNK_SIZE = 1000  # For processing large datasets
    USE_CHUNKING = False  # Enable for very large files
    
    # Parallel processing
    ENABLE_PARALLEL_PROCESSING = False
    MAX_WORKERS = 4
    
    # Caching
    CACHE_SMILES_CONVERSIONS = True
    MAX_CACHE_SIZE = 10000

# File Format Settings
class FileFormats:
    """Supported file formats and extensions."""
    
    SUPPORTED_INPUT_FORMATS = [".xlsx", ".xls"]
    SUPPORTED_OUTPUT_FORMATS = [".xlsx"]
    DEFAULT_INPUT_FORMAT = ".xlsx"
    DEFAULT_OUTPUT_FORMAT = ".xlsx"

# Messages and Templates
class Messages:
    """Standard messages and templates used in the application."""
    
    # Success messages
    SUCCESS_PROCESSING = "✓ Processing completed successfully"
    SUCCESS_FORMULA_GENERATION = "✓ Formula generation completed"
    SUCCESS_METABOLITE_MAPPING = "✓ Metabolite mapping completed"
    SUCCESS_FILE_SAVED = "✓ Output file saved successfully"
    
    # Warning messages
    WARNING_NO_SMILES = "⚠️ No SMILES column found in sheet"
    WARNING_LOW_SUCCESS_RATE = "⚠️ Low success rate detected"
    WARNING_MISSING_REFERENCE = "⚠️ Reference sheet data missing"
    
    # Error messages
    ERROR_FILE_NOT_FOUND = "❌ Input file not found"
    ERROR_INVALID_FORMAT = "❌ Invalid file format"
    ERROR_PROCESSING_FAILED = "❌ Processing failed"
    ERROR_SAVE_FAILED = "❌ Failed to save output file"
    
    # Info messages
    INFO_PROCESSING_START = "🚀 Starting metabolite analysis"
    INFO_PROCESSING_SHEET = "📊 Processing sheet"
    INFO_CREATING_BACKUP = "💾 Creating backup file"

# Development Settings
class DevelopmentSettings:
    """Settings for development and debugging."""
    
    DEBUG_MODE = False
    ENABLE_PROFILING = False
    SAVE_INTERMEDIATE_RESULTS = False
    
    # Testing
    RUN_UNIT_TESTS = False
    VALIDATE_OUTPUTS = True
    
    # Development paths
    DEV_DATA_DIR = Path("dev_data")
    TEST_DATA_DIR = Path("test_data")

# Export commonly used configurations
DEFAULT_CONFIG = {
    "input_file": DEFAULT_INPUT_FILE,
    "output_file": DEFAULT_OUTPUT_FILE,
    "reference_sheet": SheetNames.REFERENCE_SHEET,
    "formula_column": ColumnNames.FORMULA,
    "metabolite_column": ColumnNames.METABOLITE_NAME,
    "create_backup": ProcessingSettings.CREATE_BACKUP,
    "validate_input": ProcessingSettings.VALIDATE_INPUT_FILE,
    "verbose": OutputSettings.VERBOSE_PROCESSING
}

# Validation function for configuration
def validate_config(config: dict) -> tuple:
    """
    Validate configuration settings.
    
    Args:
        config (dict): Configuration dictionary to validate
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required keys
    required_keys = ["input_file", "output_file", "reference_sheet"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required configuration key: {key}")
    
    # Validate file paths
    if "input_file" in config:
        input_path = Path(config["input_file"])
        if not input_path.suffix.lower() in FileFormats.SUPPORTED_INPUT_FORMATS:
            errors.append(f"Unsupported input file format: {input_path.suffix}")
    
    # Validate success rate thresholds
    if "min_formula_success_rate" in config:
        rate = config["min_formula_success_rate"]
        if not isinstance(rate, (int, float)) or not 0 <= rate <= 100:
            errors.append("min_formula_success_rate must be a number between 0 and 100")
    
    return len(errors) == 0, errors