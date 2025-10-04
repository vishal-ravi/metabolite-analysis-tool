"""
SMILES Molecular Formula Utilities

This module provides functions for converting SMILES (Simplified Molecular Input Line Entry System)
strings to molecular formulas using RDKit chemistry toolkit.

Author: Metabolite Analysis Tool
Date: October 2025
"""

from typing import Optional, Union
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
import logging

# Set up logging
logger = logging.getLogger(__name__)


def smiles_to_formula(smiles: str) -> str:
    """
    Convert a SMILES string to a molecular formula.
    
    Args:
        smiles (str): SMILES notation string representing a molecule
        
    Returns:
        str: Molecular formula (e.g., 'C8H10N4O2' for caffeine)
             Returns 'Invalid' if SMILES cannot be parsed
             Returns 'Error' if an exception occurs during conversion
             
    Examples:
        >>> smiles_to_formula('CCO')
        'C2H6O'
        >>> smiles_to_formula('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
        'C8H10N4O2'
        >>> smiles_to_formula('invalid_smiles')
        'Invalid'
    """
    try:
        # Handle NaN or None values
        if pd.isna(smiles) or smiles is None:
            return "Error"
            
        # Convert to string if not already
        smiles_str = str(smiles).strip()
        
        # Check for empty string
        if not smiles_str:
            return "Error"
            
        # Parse SMILES using RDKit
        mol = Chem.MolFromSmiles(smiles_str)
        
        if mol is not None:
            # Calculate molecular formula
            formula = rdMolDescriptors.CalcMolFormula(mol)
            logger.debug(f"Converted SMILES '{smiles_str}' to formula '{formula}'")
            return formula
        else:
            logger.warning(f"Could not parse SMILES: '{smiles_str}'")
            return "Invalid"
            
    except Exception as e:
        logger.error(f"Error converting SMILES '{smiles}': {e}")
        return "Error"


def batch_smiles_to_formula(smiles_list: list) -> list:
    """
    Convert a list of SMILES strings to molecular formulas.
    
    Args:
        smiles_list (list): List of SMILES notation strings
        
    Returns:
        list: List of molecular formulas corresponding to input SMILES
        
    Examples:
        >>> batch_smiles_to_formula(['CCO', 'O', 'C'])
        ['C2H6O', 'H2O', 'CH4']
    """
    return [smiles_to_formula(smiles) for smiles in smiles_list]


def add_formula_column(df: pd.DataFrame, smiles_column: str, 
                      formula_column: str = 'Formula') -> pd.DataFrame:
    """
    Add a molecular formula column to a DataFrame based on SMILES column.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing SMILES data
        smiles_column (str): Name of the column containing SMILES strings
        formula_column (str): Name for the new formula column (default: 'Formula')
        
    Returns:
        pd.DataFrame: DataFrame with added formula column
        
    Raises:
        ValueError: If the specified SMILES column doesn't exist in the DataFrame
        
    Examples:
        >>> df = pd.DataFrame({'smiles': ['CCO', 'O']})
        >>> result = add_formula_column(df, 'smiles')
        >>> print(result['Formula'].tolist())
        ['C2H6O', 'H2O']
    """
    if smiles_column not in df.columns:
        raise ValueError(f"Column '{smiles_column}' not found in DataFrame")
    
    # Create a copy to avoid modifying the original DataFrame
    result_df = df.copy()
    
    # Add formula column
    result_df[formula_column] = result_df[smiles_column].apply(smiles_to_formula)
    
    logger.info(f"Added formula column '{formula_column}' based on '{smiles_column}'")
    return result_df


def find_smiles_column(df: pd.DataFrame) -> Optional[str]:
    """
    Find a SMILES column in a DataFrame (case-insensitive search).
    
    Args:
        df (pd.DataFrame): DataFrame to search
        
    Returns:
        Optional[str]: Name of the SMILES column if found, None otherwise
        
    Examples:
        >>> df = pd.DataFrame({'SMILES': ['CCO'], 'other': [1]})
        >>> find_smiles_column(df)
        'SMILES'
        >>> df = pd.DataFrame({'smiles': ['CCO'], 'other': [1]})
        >>> find_smiles_column(df)
        'smiles'
    """
    for col in df.columns:
        if col.lower() == 'smiles':
            logger.debug(f"Found SMILES column: '{col}'")
            return col
    
    logger.warning("No SMILES column found in DataFrame")
    return None


def validate_smiles(smiles: str) -> bool:
    """
    Validate if a SMILES string is chemically valid.
    
    Args:
        smiles (str): SMILES notation string to validate
        
    Returns:
        bool: True if SMILES is valid, False otherwise
        
    Examples:
        >>> validate_smiles('CCO')
        True
        >>> validate_smiles('invalid_smiles')
        False
    """
    try:
        if pd.isna(smiles) or not str(smiles).strip():
            return False
        
        mol = Chem.MolFromSmiles(str(smiles).strip())
        return mol is not None
        
    except Exception:
        return False


def get_formula_statistics(df: pd.DataFrame, formula_column: str = 'Formula') -> dict:
    """
    Get statistics about formula generation success rate.
    
    Args:
        df (pd.DataFrame): DataFrame containing formula column
        formula_column (str): Name of the formula column
        
    Returns:
        dict: Statistics including total, valid, invalid, and error counts
        
    Examples:
        >>> df = pd.DataFrame({'Formula': ['C2H6O', 'Invalid', 'Error', 'CH4']})
        >>> stats = get_formula_statistics(df)
        >>> print(stats['success_rate'])
        50.0
    """
    if formula_column not in df.columns:
        raise ValueError(f"Column '{formula_column}' not found in DataFrame")
    
    total = len(df)
    invalid_count = (df[formula_column] == 'Invalid').sum()
    error_count = (df[formula_column] == 'Error').sum()
    valid_count = total - invalid_count - error_count
    
    stats = {
        'total': total,
        'valid': valid_count,
        'invalid': invalid_count,
        'error': error_count,
        'success_rate': (valid_count / total * 100) if total > 0 else 0
    }
    
    logger.info(f"Formula statistics: {valid_count}/{total} valid ({stats['success_rate']:.1f}%)")
    return stats