"""
Excel Processing Utilities

This module provides functions for reading, processing, and writing Excel files
with metabolite and molecular formula data.

Author: Metabolite Analysis Tool
Date: October 2025
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import logging
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)


class ExcelProcessor:
    """
    A class for processing Excel files containing metabolite and SMILES data.
    
    This class provides methods to read Excel files, process SMILES data,
    add molecular formulas, map metabolite names, and save results.
    """
    
    def __init__(self, input_file: str):
        """
        Initialize the Excel processor.
        
        Args:
            input_file (str): Path to the input Excel file
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
        """
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        self.sheets_data = {}
        self.sheet_names = []
        logger.info(f"Initialized ExcelProcessor with input file: {input_file}")
    
    def load_excel_file(self) -> Dict[str, pd.DataFrame]:
        """
        Load all sheets from the Excel file into memory.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping sheet names to DataFrames
            
        Raises:
            Exception: If there's an error reading the Excel file
        """
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(self.input_file)
            self.sheet_names = excel_file.sheet_names
            
            self.sheets_data = {}
            for sheet_name in self.sheet_names:
                self.sheets_data[sheet_name] = pd.read_excel(
                    self.input_file, 
                    sheet_name=sheet_name
                )
                logger.debug(f"Loaded sheet '{sheet_name}' with shape {self.sheets_data[sheet_name].shape}")
            
            logger.info(f"Successfully loaded {len(self.sheet_names)} sheets")
            return self.sheets_data.copy()
            
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            raise
    
    def get_sheet_info(self) -> Dict[str, Dict]:
        """
        Get information about all loaded sheets.
        
        Returns:
            Dict[str, Dict]: Information about each sheet including shape, columns, etc.
            
        Examples:
            >>> processor = ExcelProcessor('data.xlsx')
            >>> processor.load_excel_file()
            >>> info = processor.get_sheet_info()
            >>> print(info['Sheet1']['shape'])
            (100, 10)
        """
        if not self.sheets_data:
            self.load_excel_file()
        
        sheet_info = {}
        for sheet_name, df in self.sheets_data.items():
            sheet_info[sheet_name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'has_smiles': any(col.lower() == 'smiles' for col in df.columns),
                'smiles_column': next((col for col in df.columns if col.lower() == 'smiles'), None)
            }
        
        return sheet_info
    
    def find_smiles_columns(self) -> Dict[str, Optional[str]]:
        """
        Find SMILES columns in all sheets.
        
        Returns:
            Dict[str, Optional[str]]: Mapping of sheet names to SMILES column names
        """
        if not self.sheets_data:
            self.load_excel_file()
        
        smiles_columns = {}
        for sheet_name, df in self.sheets_data.items():
            smiles_col = None
            for col in df.columns:
                if col.lower() == 'smiles':
                    smiles_col = col
                    break
            smiles_columns[sheet_name] = smiles_col
            
            if smiles_col:
                logger.debug(f"Sheet '{sheet_name}': Found SMILES column '{smiles_col}'")
            else:
                logger.debug(f"Sheet '{sheet_name}': No SMILES column found")
        
        return smiles_columns
    
    def validate_reference_sheet(self, reference_sheet: str = 'Sheet1') -> Tuple[bool, str]:
        """
        Validate that the reference sheet has required columns for metabolite mapping.
        
        Args:
            reference_sheet (str): Name of the reference sheet
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not self.sheets_data:
            self.load_excel_file()
        
        if reference_sheet not in self.sheets_data:
            return False, f"Reference sheet '{reference_sheet}' not found"
        
        df = self.sheets_data[reference_sheet]
        
        # Check for required columns
        required_cols = ['chemical_formula', 'Metabolite name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, f"Missing required columns in '{reference_sheet}': {missing_cols}"
        
        # Check for data
        if df.empty:
            return False, f"Reference sheet '{reference_sheet}' is empty"
        
        # Check for valid data
        valid_rows = df[['chemical_formula', 'Metabolite name']].dropna()
        if valid_rows.empty:
            return False, f"No valid formula-metabolite pairs found in '{reference_sheet}'"
        
        logger.info(f"Reference sheet '{reference_sheet}' validation passed")
        return True, ""
    
    def save_to_excel(self, output_file: str, sheets_data: Optional[Dict[str, pd.DataFrame]] = None) -> bool:
        """
        Save processed data to Excel file.
        
        Args:
            output_file (str): Path for the output Excel file
            sheets_data (Optional[Dict[str, pd.DataFrame]]): Data to save (uses internal data if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data_to_save = sheets_data if sheets_data is not None else self.sheets_data
            
            if not data_to_save:
                logger.error("No data to save")
                return False
            
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to Excel
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                for sheet_name, df in data_to_save.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    logger.debug(f"Saved sheet '{sheet_name}' with shape {df.shape}")
            
            logger.info(f"Successfully saved {len(data_to_save)} sheets to '{output_file}'")
            return True
            
        except Exception as e:
            logger.error(f"Error saving Excel file: {e}")
            return False
    
    def get_processing_summary(self, sheets_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        Get a summary of processing results.
        
        Args:
            sheets_data (Dict[str, pd.DataFrame]): Processed sheets data
            
        Returns:
            Dict[str, Dict]: Summary statistics for each sheet
        """
        summary = {}
        
        for sheet_name, df in sheets_data.items():
            sheet_summary = {
                'total_rows': len(df),
                'columns': list(df.columns),
                'has_formula': 'Formula' in df.columns,
                'has_metabolite': 'Metabolite name' in df.columns
            }
            
            # Formula statistics
            if 'Formula' in df.columns:
                valid_formulas = len(df) - df['Formula'].isin(['Invalid', 'Error']).sum()
                sheet_summary['formula_stats'] = {
                    'total': len(df),
                    'valid': valid_formulas,
                    'success_rate': (valid_formulas / len(df) * 100) if len(df) > 0 else 0
                }
            
            # Metabolite mapping statistics
            if 'Metabolite name' in df.columns:
                mapped_metabolites = df['Metabolite name'].notna().sum()
                sheet_summary['metabolite_stats'] = {
                    'total': len(df),
                    'mapped': mapped_metabolites,
                    'success_rate': (mapped_metabolites / len(df) * 100) if len(df) > 0 else 0
                }
            
            summary[sheet_name] = sheet_summary
        
        return summary
    
    def backup_original_file(self, backup_suffix: str = "_backup") -> str:
        """
        Create a backup of the original Excel file.
        
        Args:
            backup_suffix (str): Suffix to add to the backup filename
            
        Returns:
            str: Path to the backup file
        """
        backup_path = self.input_file.with_name(
            f"{self.input_file.stem}{backup_suffix}{self.input_file.suffix}"
        )
        
        try:
            import shutil
            shutil.copy2(self.input_file, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise


def compare_excel_files(file1: str, file2: str) -> Dict[str, Dict]:
    """
    Compare two Excel files and return differences.
    
    Args:
        file1 (str): Path to the first Excel file
        file2 (str): Path to the second Excel file
        
    Returns:
        Dict[str, Dict]: Comparison results for each sheet
    """
    comparison = {}
    
    try:
        # Load both files
        xls1 = pd.ExcelFile(file1)
        xls2 = pd.ExcelFile(file2)
        
        # Compare sheet names
        sheets1 = set(xls1.sheet_names)
        sheets2 = set(xls2.sheet_names)
        
        comparison['sheet_comparison'] = {
            'common_sheets': list(sheets1.intersection(sheets2)),
            'only_in_file1': list(sheets1 - sheets2),
            'only_in_file2': list(sheets2 - sheets1)
        }
        
        # Compare common sheets
        for sheet in sheets1.intersection(sheets2):
            df1 = pd.read_excel(file1, sheet_name=sheet)
            df2 = pd.read_excel(file2, sheet_name=sheet)
            
            sheet_comparison = {
                'shape_file1': df1.shape,
                'shape_file2': df2.shape,
                'columns_file1': list(df1.columns),
                'columns_file2': list(df2.columns),
                'new_columns': list(set(df2.columns) - set(df1.columns)),
                'removed_columns': list(set(df1.columns) - set(df2.columns))
            }
            
            comparison[sheet] = sheet_comparison
        
        logger.info(f"Comparison completed for files: {file1} vs {file2}")
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing files: {e}")
        raise


def validate_excel_file(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate an Excel file for basic requirements.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        # Check file existence
        if not Path(file_path).exists():
            issues.append(f"File does not exist: {file_path}")
            return False, issues
        
        # Try to load the file
        excel_file = pd.ExcelFile(file_path)
        
        if not excel_file.sheet_names:
            issues.append("Excel file contains no sheets")
        
        # Check each sheet
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if df.empty:
                issues.append(f"Sheet '{sheet_name}' is empty")
            
            # Check for basic data integrity
            if df.shape[0] == 0:
                issues.append(f"Sheet '{sheet_name}' has no data rows")
        
        is_valid = len(issues) == 0
        logger.info(f"Excel file validation {'passed' if is_valid else 'failed'}: {file_path}")
        
        return is_valid, issues
        
    except Exception as e:
        issues.append(f"Error reading Excel file: {e}")
        return False, issues