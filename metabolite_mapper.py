"""
Metabolite Mapping Utilities

This module provides functions for mapping metabolite names based on chemical formula matching.
It creates lookup tables from reference data and applies them to target datasets.

Author: Metabolite Analysis Tool
Date: October 2025
"""

from typing import Dict, Optional, Tuple, List
import pandas as pd
import logging

# Set up logging
logger = logging.getLogger(__name__)


def create_formula_metabolite_mapping(reference_df: pd.DataFrame, 
                                     formula_column: str = 'chemical_formula',
                                     metabolite_column: str = 'Metabolite name') -> Dict[str, str]:
    """
    Create a mapping dictionary from chemical formulas to metabolite names.
    
    Args:
        reference_df (pd.DataFrame): Reference DataFrame containing formula and metabolite data
        formula_column (str): Name of the column containing chemical formulas
        metabolite_column (str): Name of the column containing metabolite names
        
    Returns:
        Dict[str, str]: Mapping from chemical formula to metabolite name
        
    Raises:
        ValueError: If required columns are not found in the DataFrame
        
    Examples:
        >>> df = pd.DataFrame({
        ...     'chemical_formula': ['C6H12O6', 'C8H10N4O2'], 
        ...     'Metabolite name': ['Glucose', 'Caffeine']
        ... })
        >>> mapping = create_formula_metabolite_mapping(df)
        >>> print(mapping['C6H12O6'])
        'Glucose'
    """
    # Validate required columns
    if formula_column not in reference_df.columns:
        raise ValueError(f"Formula column '{formula_column}' not found in reference DataFrame")
    
    if metabolite_column not in reference_df.columns:
        raise ValueError(f"Metabolite column '{metabolite_column}' not found in reference DataFrame")
    
    # Create mapping dictionary
    formula_to_metabolite = {}
    
    for idx, row in reference_df.iterrows():
        formula = row[formula_column]
        metabolite = row[metabolite_column]
        
        # Skip rows with missing data
        if pd.isna(formula) or pd.isna(metabolite):
            continue
            
        # Convert to string and clean
        formula_str = str(formula).strip()
        metabolite_str = str(metabolite).strip()
        
        # Skip empty values
        if not formula_str or not metabolite_str:
            continue
            
        # Use first occurrence for duplicate formulas
        if formula_str not in formula_to_metabolite:
            formula_to_metabolite[formula_str] = metabolite_str
        else:
            logger.debug(f"Duplicate formula '{formula_str}' found, keeping first occurrence")
    
    logger.info(f"Created mapping for {len(formula_to_metabolite)} unique formulas")
    return formula_to_metabolite


def apply_metabolite_mapping(target_df: pd.DataFrame,
                            mapping: Dict[str, str],
                            formula_column: str = 'Formula',
                            new_metabolite_column: str = 'Metabolite name') -> pd.DataFrame:
    """
    Apply metabolite name mapping to a target DataFrame based on chemical formulas.
    
    Args:
        target_df (pd.DataFrame): Target DataFrame to add metabolite names to
        mapping (Dict[str, str]): Mapping from chemical formula to metabolite name
        formula_column (str): Name of the column containing formulas in target DataFrame
        new_metabolite_column (str): Name for the new metabolite column
        
    Returns:
        pd.DataFrame: DataFrame with added metabolite name column
        
    Raises:
        ValueError: If the formula column is not found in the target DataFrame
        
    Examples:
        >>> df = pd.DataFrame({'Formula': ['C6H12O6', 'C8H10N4O2']})
        >>> mapping = {'C6H12O6': 'Glucose', 'C8H10N4O2': 'Caffeine'}
        >>> result = apply_metabolite_mapping(df, mapping)
        >>> print(result['Metabolite name'].tolist())
        ['Glucose', 'Caffeine']
    """
    if formula_column not in target_df.columns:
        raise ValueError(f"Formula column '{formula_column}' not found in target DataFrame")
    
    # Create a copy to avoid modifying the original DataFrame
    result_df = target_df.copy()
    
    # Apply mapping using pandas map function
    result_df[new_metabolite_column] = result_df[formula_column].map(mapping)
    
    # Count successful mappings
    matches = result_df[new_metabolite_column].notna().sum()
    total = len(result_df)
    
    logger.info(f"Applied metabolite mapping: {matches}/{total} matches ({matches/total*100:.1f}%)")
    return result_df


def get_mapping_statistics(target_df: pd.DataFrame, 
                          metabolite_column: str = 'Metabolite name') -> Dict[str, int]:
    """
    Get statistics about metabolite mapping success rate.
    
    Args:
        target_df (pd.DataFrame): DataFrame with metabolite mapping results
        metabolite_column (str): Name of the metabolite column
        
    Returns:
        Dict[str, int]: Statistics including total, matched, and unmatched counts
        
    Examples:
        >>> df = pd.DataFrame({'Metabolite name': ['Glucose', None, 'Caffeine']})
        >>> stats = get_mapping_statistics(df)
        >>> print(stats['success_rate'])
        66.7
    """
    if metabolite_column not in target_df.columns:
        raise ValueError(f"Metabolite column '{metabolite_column}' not found in DataFrame")
    
    total = len(target_df)
    matched = target_df[metabolite_column].notna().sum()
    unmatched = total - matched
    
    stats = {
        'total': total,
        'matched': matched,
        'unmatched': unmatched,
        'success_rate': (matched / total * 100) if total > 0 else 0
    }
    
    return stats


def find_unmatched_formulas(target_df: pd.DataFrame,
                           formula_column: str = 'Formula',
                           metabolite_column: str = 'Metabolite name') -> List[str]:
    """
    Find chemical formulas that couldn't be mapped to metabolite names.
    
    Args:
        target_df (pd.DataFrame): DataFrame with mapping results
        formula_column (str): Name of the formula column
        metabolite_column (str): Name of the metabolite column
        
    Returns:
        List[str]: List of unmatched chemical formulas
        
    Examples:
        >>> df = pd.DataFrame({
        ...     'Formula': ['C6H12O6', 'C8H10N4O2', 'C10H16N2'],
        ...     'Metabolite name': ['Glucose', 'Caffeine', None]
        ... })
        >>> unmatched = find_unmatched_formulas(df)
        >>> print(unmatched)
        ['C10H16N2']
    """
    if formula_column not in target_df.columns:
        raise ValueError(f"Formula column '{formula_column}' not found in DataFrame")
    
    if metabolite_column not in target_df.columns:
        raise ValueError(f"Metabolite column '{metabolite_column}' not found in DataFrame")
    
    # Find rows where metabolite name is missing but formula exists
    unmatched_mask = (target_df[metabolite_column].isna()) & (target_df[formula_column].notna())
    unmatched_formulas = target_df.loc[unmatched_mask, formula_column].unique().tolist()
    
    logger.info(f"Found {len(unmatched_formulas)} unmatched formulas")
    return unmatched_formulas


def validate_mapping_columns(df: pd.DataFrame, 
                            formula_column: str = 'chemical_formula',
                            metabolite_column: str = 'Metabolite name') -> bool:
    """
    Validate that required columns exist in the DataFrame for mapping.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        formula_column (str): Expected formula column name
        metabolite_column (str): Expected metabolite column name
        
    Returns:
        bool: True if both columns exist, False otherwise
        
    Examples:
        >>> df = pd.DataFrame({'chemical_formula': ['C6H12O6'], 'Metabolite name': ['Glucose']})
        >>> validate_mapping_columns(df)
        True
    """
    has_formula = formula_column in df.columns
    has_metabolite = metabolite_column in df.columns
    
    if not has_formula:
        logger.warning(f"Formula column '{formula_column}' not found")
    
    if not has_metabolite:
        logger.warning(f"Metabolite column '{metabolite_column}' not found")
    
    return has_formula and has_metabolite


def merge_metabolite_data(reference_df: pd.DataFrame,
                         target_dfs: List[pd.DataFrame],
                         sheet_names: List[str],
                         reference_formula_col: str = 'chemical_formula',
                         reference_metabolite_col: str = 'Metabolite name',
                         target_formula_col: str = 'Formula') -> List[pd.DataFrame]:
    """
    Merge metabolite data from reference sheet to multiple target sheets.
    
    Args:
        reference_df (pd.DataFrame): Reference DataFrame with metabolite data
        target_dfs (List[pd.DataFrame]): List of target DataFrames
        sheet_names (List[str]): Names of the target sheets (for logging)
        reference_formula_col (str): Formula column name in reference DataFrame
        reference_metabolite_col (str): Metabolite column name in reference DataFrame
        target_formula_col (str): Formula column name in target DataFrames
        
    Returns:
        List[pd.DataFrame]: List of target DataFrames with added metabolite names
        
    Examples:
        >>> ref_df = pd.DataFrame({'chemical_formula': ['C6H12O6'], 'Metabolite name': ['Glucose']})
        >>> target_df = pd.DataFrame({'Formula': ['C6H12O6']})
        >>> result = merge_metabolite_data(ref_df, [target_df], ['Sheet1'])
        >>> print(result[0]['Metabolite name'].iloc[0])
        'Glucose'
    """
    # Create mapping from reference data
    mapping = create_formula_metabolite_mapping(
        reference_df, 
        reference_formula_col, 
        reference_metabolite_col
    )
    
    # Apply mapping to each target DataFrame
    result_dfs = []
    
    for i, (target_df, sheet_name) in enumerate(zip(target_dfs, sheet_names)):
        if target_formula_col in target_df.columns:
            # Apply metabolite mapping
            updated_df = apply_metabolite_mapping(target_df, mapping, target_formula_col)
            
            # Log statistics
            stats = get_mapping_statistics(updated_df)
            logger.info(f"Sheet '{sheet_name}': {stats['matched']}/{stats['total']} metabolite matches")
            
            result_dfs.append(updated_df)
        else:
            logger.warning(f"Sheet '{sheet_name}': No formula column '{target_formula_col}' found")
            result_dfs.append(target_df)
    
    return result_dfs