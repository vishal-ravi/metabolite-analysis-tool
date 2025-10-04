#!/usr/bin/env python3
"""
Example Usage Script for Metabolite Analysis Tool

This script demonstrates how to use the various modules of the Metabolite Analysis Tool
for processing SMILES data and mapping metabolite names.

Author: Metabolite Analysis Tool
Date: October 2025
"""

import pandas as pd
import logging
from pathlib import Path

# Import our modules
from smiles_utils import (
    smiles_to_formula, 
    add_formula_column, 
    find_smiles_column,
    get_formula_statistics,
    validate_smiles
)
from metabolite_mapper import (
    create_formula_metabolite_mapping,
    apply_metabolite_mapping,
    get_mapping_statistics,
    find_unmatched_formulas
)
from excel_processor import ExcelProcessor, validate_excel_file
from config import DEFAULT_CONFIG, ColumnNames


def setup_example_logging():
    """Set up logging for the example script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def example_1_basic_smiles_processing():
    """
    Example 1: Basic SMILES to formula conversion
    """
    print("\n" + "="*60)
    print("Example 1: Basic SMILES Processing")
    print("="*60)
    
    # Sample SMILES data
    sample_smiles = [
        'CCO',                                    # Ethanol
        'Cn1cnc2c1c(=O)n(c(=O)n2C)C',            # Caffeine
        'C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O',  # Glucose
        'O',                                      # Water
        'C[N+](C)(C)CCOP(=O)([O-])OC[C@H](O)CO', # Choline phosphate
        'invalid_smiles'                          # Invalid SMILES
    ]
    
    compound_names = [
        'Ethanol', 'Caffeine', 'Glucose', 'Water', 'Choline phosphate', 'Invalid'
    ]
    
    print("Converting SMILES to molecular formulas:")
    print("-" * 40)
    
    for smiles, name in zip(sample_smiles, compound_names):
        formula = smiles_to_formula(smiles)
        valid = validate_smiles(smiles)
        print(f"{name:15} | {smiles:30} | {formula:10} | Valid: {valid}")


def example_2_dataframe_processing():
    """
    Example 2: DataFrame processing with formula addition
    """
    print("\n" + "="*60)
    print("Example 2: DataFrame Processing")
    print("="*60)
    
    # Create sample DataFrame
    data = {
        'smiles': [
            'CCO',
            'Cn1cnc2c1c(=O)n(c(=O)n2C)C',
            'C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O',
            'O',
            'invalid_smiles'
        ],
        'compound_name': [
            'Ethanol',
            'Caffeine', 
            'Glucose',
            'Water',
            'Invalid compound'
        ],
        'concentration': [10.5, 25.3, 15.7, 100.0, 0.0]
    }
    
    df = pd.DataFrame(data)
    print("Original DataFrame:")
    print(df)
    
    # Find SMILES column
    smiles_col = find_smiles_column(df)
    print(f"\nFound SMILES column: '{smiles_col}'")
    
    # Add formula column
    df_with_formulas = add_formula_column(df, smiles_col)
    print("\nDataFrame with formulas:")
    print(df_with_formulas)
    
    # Get statistics
    stats = get_formula_statistics(df_with_formulas)
    print(f"\nFormula generation statistics:")
    print(f"Total: {stats['total']}")
    print(f"Valid: {stats['valid']}")
    print(f"Invalid: {stats['invalid']}")
    print(f"Error: {stats['error']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")


def example_3_metabolite_mapping():
    """
    Example 3: Metabolite name mapping between sheets
    """
    print("\n" + "="*60)
    print("Example 3: Metabolite Name Mapping")
    print("="*60)
    
    # Create reference DataFrame (like Sheet1)
    reference_data = {
        'chemical_formula': ['C2H6O', 'C8H10N4O2', 'C6H12O6', 'H2O'],
        'Metabolite name': ['Ethanol', 'Caffeine', 'Glucose', 'Water'],
        'smiles': [
            'CCO',
            'Cn1cnc2c1c(=O)n(c(=O)n2C)C',
            'C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O',
            'O'
        ]
    }
    reference_df = pd.DataFrame(reference_data)
    
    print("Reference DataFrame:")
    print(reference_df)
    
    # Create target DataFrame (like other sheets)
    target_data = {
        'SMILES': [
            'CCO',
            'Cn1cnc2c1c(=O)n(c(=O)n2C)C',
            'O',
            'CC(C)C'  # Different compound not in reference
        ],
        'measurement_value': [1.2, 3.4, 5.6, 7.8]
    }
    target_df = pd.DataFrame(target_data)
    
    # Add formulas to target DataFrame first
    smiles_col = find_smiles_column(target_df)
    target_df_with_formulas = add_formula_column(target_df, smiles_col)
    
    print("\nTarget DataFrame with formulas:")
    print(target_df_with_formulas)
    
    # Create mapping from reference
    mapping = create_formula_metabolite_mapping(reference_df)
    print(f"\nCreated mapping for {len(mapping)} formulas:")
    for formula, metabolite in mapping.items():
        print(f"  {formula} -> {metabolite}")
    
    # Apply mapping to target
    target_with_metabolites = apply_metabolite_mapping(
        target_df_with_formulas, 
        mapping
    )
    
    print("\nTarget DataFrame with metabolite names:")
    print(target_with_metabolites)
    
    # Get mapping statistics
    stats = get_mapping_statistics(target_with_metabolites)
    print(f"\nMapping statistics:")
    print(f"Total: {stats['total']}")
    print(f"Matched: {stats['matched']}")
    print(f"Unmatched: {stats['unmatched']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    
    # Find unmatched formulas
    unmatched = find_unmatched_formulas(target_with_metabolites)
    print(f"\nUnmatched formulas: {unmatched}")


def example_4_excel_file_processing():
    """
    Example 4: Complete Excel file processing workflow
    """
    print("\n" + "="*60)
    print("Example 4: Excel File Processing")
    print("="*60)
    
    # Check if the example input file exists
    input_file = "swissadmet 92.xlsx"
    
    if not Path(input_file).exists():
        print(f"⚠️  Input file '{input_file}' not found.")
        print("This example requires the actual input file to demonstrate Excel processing.")
        print("You can run this example with your own Excel file by modifying the input_file variable.")
        return
    
    try:
        # Validate input file
        print(f"🔍 Validating input file: {input_file}")
        is_valid, issues = validate_excel_file(input_file)
        
        if not is_valid:
            print("❌ File validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            return
        
        print("✅ File validation passed")
        
        # Initialize processor
        processor = ExcelProcessor(input_file)
        
        # Get file information
        print("\n📊 Sheet Information:")
        sheet_info = processor.get_sheet_info()
        for sheet_name, info in sheet_info.items():
            print(f"  {sheet_name}:")
            print(f"    Shape: {info['shape']}")
            print(f"    Has SMILES: {info['has_smiles']}")
            print(f"    SMILES column: {info['smiles_column']}")
        
        # Load data
        sheets_data = processor.load_excel_file()
        
        # Validate reference sheet
        is_valid, error_msg = processor.validate_reference_sheet()
        if is_valid:
            print("\n✅ Reference sheet validation passed")
        else:
            print(f"\n❌ Reference sheet validation failed: {error_msg}")
            return
        
        # Process a sample sheet (just show the first few rows)
        sample_sheet = list(sheets_data.keys())[0]
        sample_df = sheets_data[sample_sheet].head()
        
        print(f"\n📋 Sample data from '{sample_sheet}':")
        print(sample_df)
        
        print(f"\n✅ Excel file processing demonstration completed")
        print(f"💡 Use the main application to process the complete file:")
        print(f"    python process_metabolites.py {input_file}")
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {e}")


def example_5_configuration_usage():
    """
    Example 5: Using configuration settings
    """
    print("\n" + "="*60)
    print("Example 5: Configuration Usage")
    print("="*60)
    
    # Show default configuration
    print("Default configuration:")
    for key, value in DEFAULT_CONFIG.items():
        print(f"  {key}: {value}")
    
    # Show column name constants
    print(f"\nDefault column names:")
    print(f"  Formula column: {ColumnNames.FORMULA}")
    print(f"  Metabolite column: {ColumnNames.METABOLITE_NAME}")
    print(f"  Chemical formula column: {ColumnNames.CHEMICAL_FORMULA}")
    
    # Show SMILES variations
    print(f"\nSupported SMILES column variations:")
    for variation in ColumnNames.SMILES_VARIATIONS:
        print(f"  - {variation}")


def run_all_examples():
    """
    Run all example functions
    """
    print("🧪 Metabolite Analysis Tool - Examples")
    print("="*60)
    
    setup_example_logging()
    
    try:
        example_1_basic_smiles_processing()
        example_2_dataframe_processing()
        example_3_metabolite_mapping()
        example_4_excel_file_processing()
        example_5_configuration_usage()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
        print("\n📚 Next steps:")
        print("1. Try the main application: python process_metabolites.py your_file.xlsx")
        print("2. Modify these examples for your specific use case")
        print("3. Check the README.md for detailed documentation")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()