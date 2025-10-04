#!/usr/bin/env python3
"""
Metabolite Analysis Tool - Main Application

This is the main entry point for the metabolite analysis tool that processes
SMILES data and maps metabolite names in Excel files.

Author: Metabolite Analysis Tool
Date: October 2025

Usage:
    python process_metabolites.py input_file.xlsx [output_file.xlsx]
    python process_metabolites.py --help
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Import our custom modules
from smiles_utils import find_smiles_column, add_formula_column, get_formula_statistics
from metabolite_mapper import create_formula_metabolite_mapping, apply_metabolite_mapping, get_mapping_statistics
from excel_processor import ExcelProcessor, validate_excel_file
from config import (
    DEFAULT_CONFIG, ColumnNames, SheetNames, ProcessingSettings, 
    Messages, LoggingConfig, APP_NAME, APP_VERSION
)


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose (bool): Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else getattr(logging, LoggingConfig.LOG_LEVEL)
    
    logging.basicConfig(
        level=log_level,
        format=LoggingConfig.LOG_FORMAT,
        datefmt=LoggingConfig.LOG_DATE_FORMAT
    )
    
    # Suppress some verbose logs from external libraries
    logging.getLogger('openpyxl').setLevel(logging.WARNING)
    logging.getLogger('rdkit').setLevel(logging.WARNING)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{APP_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.xlsx                    # Process data.xlsx, save as output_with_formulas.xlsx
  %(prog)s data.xlsx results.xlsx       # Process data.xlsx, save as results.xlsx
  %(prog)s data.xlsx --no-backup        # Process without creating backup
  %(prog)s data.xlsx --verbose          # Show detailed processing information
  %(prog)s data.xlsx --reference Sheet2 # Use Sheet2 as reference instead of Sheet1
        """
    )
    
    # Required arguments
    parser.add_argument(
        'input_file',
        help='Input Excel file containing SMILES data'
    )
    
    # Optional arguments
    parser.add_argument(
        'output_file',
        nargs='?',
        default=DEFAULT_CONFIG['output_file'],
        help=f'Output Excel file (default: {DEFAULT_CONFIG["output_file"]})'
    )
    
    parser.add_argument(
        '--reference',
        default=DEFAULT_CONFIG['reference_sheet'],
        help=f'Reference sheet name for metabolite mapping (default: {DEFAULT_CONFIG["reference_sheet"]})'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup of input file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'{APP_NAME} {APP_VERSION}'
    )
    
    return parser.parse_args()


def process_formulas(processor: ExcelProcessor, sheets_data: dict) -> dict:
    """
    Process SMILES data and add molecular formulas to sheets.
    
    Args:
        processor (ExcelProcessor): Excel processor instance
        sheets_data (dict): Dictionary of sheet data
        
    Returns:
        dict: Updated sheets data with formulas
    """
    logger = logging.getLogger(__name__)
    logger.info("🧪 Starting formula generation from SMILES data")
    
    updated_sheets = {}
    smiles_columns = processor.find_smiles_columns()
    
    total_sheets_processed = 0
    total_formulas_generated = 0
    
    for sheet_name, df in sheets_data.items():
        smiles_column = smiles_columns.get(sheet_name)
        
        if smiles_column:
            try:
                # Add formula column
                updated_df = add_formula_column(df, smiles_column, ColumnNames.FORMULA)
                
                # Get statistics
                stats = get_formula_statistics(updated_df, ColumnNames.FORMULA)
                
                logger.info(f"Sheet '{sheet_name}': Generated {stats['valid']}/{stats['total']} formulas "
                           f"({stats['success_rate']:.1f}% success rate)")
                
                total_sheets_processed += 1
                total_formulas_generated += stats['valid']
                updated_sheets[sheet_name] = updated_df
                
            except Exception as e:
                logger.error(f"Error processing formulas for sheet '{sheet_name}': {e}")
                updated_sheets[sheet_name] = df
        else:
            logger.warning(f"Sheet '{sheet_name}': {Messages.WARNING_NO_SMILES}")
            updated_sheets[sheet_name] = df
    
    logger.info(f"✓ Formula generation completed: {total_sheets_processed} sheets processed, "
               f"{total_formulas_generated} formulas generated")
    
    return updated_sheets


def process_metabolite_mapping(sheets_data: dict, reference_sheet: str) -> dict:
    """
    Process metabolite name mapping based on chemical formulas.
    
    Args:
        sheets_data (dict): Dictionary of sheet data
        reference_sheet (str): Name of the reference sheet
        
    Returns:
        dict: Updated sheets data with metabolite names
    """
    logger = logging.getLogger(__name__)
    logger.info("🏷️ Starting metabolite name mapping")
    
    # Validate reference sheet
    if reference_sheet not in sheets_data:
        logger.error(f"Reference sheet '{reference_sheet}' not found")
        return sheets_data
    
    reference_df = sheets_data[reference_sheet]
    
    # Validate reference sheet columns
    if (ColumnNames.REFERENCE_FORMULA_COL not in reference_df.columns or 
        ColumnNames.REFERENCE_METABOLITE_COL not in reference_df.columns):
        logger.error(f"Reference sheet missing required columns: "
                    f"{ColumnNames.REFERENCE_FORMULA_COL}, {ColumnNames.REFERENCE_METABOLITE_COL}")
        return sheets_data
    
    # Create mapping
    try:
        mapping = create_formula_metabolite_mapping(
            reference_df,
            ColumnNames.REFERENCE_FORMULA_COL,
            ColumnNames.REFERENCE_METABOLITE_COL
        )
        
        logger.info(f"Created mapping for {len(mapping)} unique formulas from '{reference_sheet}'")
        
    except Exception as e:
        logger.error(f"Error creating metabolite mapping: {e}")
        return sheets_data
    
    # Apply mapping to other sheets
    updated_sheets = {}
    total_mappings = 0
    
    for sheet_name, df in sheets_data.items():
        if sheet_name == reference_sheet:
            # Keep reference sheet unchanged
            updated_sheets[sheet_name] = df
            continue
        
        if ColumnNames.FORMULA in df.columns:
            try:
                # Apply metabolite mapping
                updated_df = apply_metabolite_mapping(
                    df, mapping, ColumnNames.FORMULA, ColumnNames.METABOLITE_NAME
                )
                
                # Get statistics
                stats = get_mapping_statistics(updated_df, ColumnNames.METABOLITE_NAME)
                
                logger.info(f"Sheet '{sheet_name}': Mapped {stats['matched']}/{stats['total']} metabolites "
                           f"({stats['success_rate']:.1f}% success rate)")
                
                total_mappings += stats['matched']
                updated_sheets[sheet_name] = updated_df
                
            except Exception as e:
                logger.error(f"Error mapping metabolites for sheet '{sheet_name}': {e}")
                updated_sheets[sheet_name] = df
        else:
            logger.warning(f"Sheet '{sheet_name}': No formula column found for metabolite mapping")
            updated_sheets[sheet_name] = df
    
    logger.info(f"✓ Metabolite mapping completed: {total_mappings} total mappings applied")
    return updated_sheets


def generate_summary_report(processor: ExcelProcessor, final_sheets: dict) -> None:
    """
    Generate and display a summary report of the processing results.
    
    Args:
        processor (ExcelProcessor): Excel processor instance
        final_sheets (dict): Final processed sheets data
    """
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print(f"  {APP_NAME} - Processing Summary")
    print("="*60)
    
    # Get processing summary
    summary = processor.get_processing_summary(final_sheets)
    
    # Overall statistics
    total_rows = sum(sheet['total_rows'] for sheet in summary.values())
    sheets_with_formulas = sum(1 for sheet in summary.values() if sheet['has_formula'])
    sheets_with_metabolites = sum(1 for sheet in summary.values() if sheet['has_metabolite'])
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total sheets processed: {len(final_sheets)}")
    print(f"   Total data rows: {total_rows:,}")
    print(f"   Sheets with formulas: {sheets_with_formulas}")
    print(f"   Sheets with metabolite names: {sheets_with_metabolites}")
    
    # Per-sheet details
    print(f"\n📋 Sheet Details:")
    for sheet_name, sheet_summary in summary.items():
        print(f"\n   {sheet_name}:")
        print(f"     Rows: {sheet_summary['total_rows']:,}")
        
        if sheet_summary['has_formula'] and 'formula_stats' in sheet_summary:
            stats = sheet_summary['formula_stats']
            print(f"     Formulas: {stats['valid']}/{stats['total']} "
                  f"({stats['success_rate']:.1f}% success)")
        
        if sheet_summary['has_metabolite'] and 'metabolite_stats' in sheet_summary:
            stats = sheet_summary['metabolite_stats']
            print(f"     Metabolites: {stats['mapped']}/{stats['total']} "
                  f"({stats['success_rate']:.1f}% mapped)")
    
    print("\n" + "="*60)


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)
        
        # Display welcome message
        print(f"\n🚀 {APP_NAME} v{APP_VERSION}")
        print(f"📁 Input file: {args.input_file}")
        print(f"📄 Output file: {args.output_file}")
        print(f"📊 Reference sheet: {args.reference}")
        
        # Validate input file
        logger.info("🔍 Validating input file")
        is_valid, issues = validate_excel_file(args.input_file)
        if not is_valid:
            logger.error("Input file validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return 1
        
        # Initialize processor
        logger.info("📂 Loading Excel file")
        processor = ExcelProcessor(args.input_file)
        
        # Create backup if requested
        if not args.no_backup and ProcessingSettings.CREATE_BACKUP:
            try:
                backup_path = processor.backup_original_file()
                print(f"💾 Backup created: {backup_path}")
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")
        
        # Load data
        sheets_data = processor.load_excel_file()
        
        # Validate reference sheet
        is_valid, error_msg = processor.validate_reference_sheet(args.reference)
        if not is_valid:
            logger.error(f"Reference sheet validation failed: {error_msg}")
            return 1
        
        # Process formulas
        sheets_with_formulas = process_formulas(processor, sheets_data)
        
        # Process metabolite mapping
        final_sheets = process_metabolite_mapping(sheets_with_formulas, args.reference)
        
        # Save results
        logger.info("💾 Saving results")
        success = processor.save_to_excel(args.output_file, final_sheets)
        
        if not success:
            logger.error("Failed to save output file")
            return 1
        
        # Generate summary report
        generate_summary_report(processor, final_sheets)
        
        print(f"\n✅ {Messages.SUCCESS_PROCESSING}")
        print(f"📄 Results saved to: {args.output_file}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted by user")
        return 1
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error: {e}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())