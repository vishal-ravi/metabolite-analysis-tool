# Metabolite Analysis Tool

A comprehensive Python tool for processing SMILES (Simplified Molecular Input Line Entry System) data and mapping metabolite names in Excel files. This tool automatically generates molecular formulas from SMILES strings and maps metabolite names based on chemical formula matching.

## 🌟 Features

- **SMILES to Formula Conversion**: Convert SMILES notation to molecular formulas using RDKit
- **Metabolite Name Mapping**: Map metabolite names across sheets based on chemical formula matching
- **Excel File Processing**: Read, process, and save Excel files with multiple sheets
- **Case-Insensitive Column Detection**: Automatically finds SMILES columns regardless of case
- **Robust Error Handling**: Gracefully handles invalid SMILES and missing data
- **Comprehensive Logging**: Detailed logging with configurable verbosity
- **Backup Creation**: Automatically creates backups of input files
- **Statistical Reporting**: Detailed success rate statistics and processing summaries

## 📋 Requirements

- Python 3.8+
- pandas
- openpyxl
- rdkit
- logging (built-in)
- pathlib (built-in)

## 🚀 Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Command Line Interface

```bash
# Basic usage
python process_metabolites.py input_file.xlsx

# Specify output file
python process_metabolites.py input_file.xlsx output_file.xlsx

# Use different reference sheet
python process_metabolites.py input_file.xlsx --reference "Sheet2"

# Verbose output
python process_metabolites.py input_file.xlsx --verbose

# Skip backup creation
python process_metabolites.py input_file.xlsx --no-backup

# Show help
python process_metabolites.py --help
```

### Python API Usage

```python
from excel_processor import ExcelProcessor
from smiles_utils import add_formula_column, find_smiles_column
from metabolite_mapper import create_formula_metabolite_mapping, apply_metabolite_mapping

# Initialize processor
processor = ExcelProcessor("input_file.xlsx")
sheets_data = processor.load_excel_file()

# Process formulas for a specific sheet
df = sheets_data['Sheet1']
smiles_col = find_smiles_column(df)
if smiles_col:
    df_with_formulas = add_formula_column(df, smiles_col)

# Create metabolite mapping
reference_df = sheets_data['Sheet1']
mapping = create_formula_metabolite_mapping(reference_df)

# Apply mapping to other sheets
target_df = sheets_data['Sheet2']
df_with_metabolites = apply_metabolite_mapping(target_df, mapping)

# Save results
processor.save_to_excel("output_file.xlsx", sheets_data)
```

## 📁 Project Structure

```
metabolite_analysis_tool/
├── process_metabolites.py    # Main application entry point
├── smiles_utils.py          # SMILES processing utilities
├── metabolite_mapper.py     # Metabolite mapping functions
├── excel_processor.py       # Excel file processing
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── example.py             # Usage examples
└── main.py               # Legacy main script (original)
```

## 🔧 Module Documentation

### `smiles_utils.py`
Handles SMILES string processing and molecular formula generation.

**Key Functions:**
- `smiles_to_formula(smiles)`: Convert single SMILES to formula
- `add_formula_column(df, smiles_column)`: Add formula column to DataFrame
- `find_smiles_column(df)`: Find SMILES column in DataFrame
- `validate_smiles(smiles)`: Validate SMILES string
- `get_formula_statistics(df)`: Get processing statistics

### `metabolite_mapper.py`
Manages metabolite name mapping based on chemical formulas.

**Key Functions:**
- `create_formula_metabolite_mapping(df)`: Create formula→metabolite mapping
- `apply_metabolite_mapping(df, mapping)`: Apply mapping to DataFrame
- `get_mapping_statistics(df)`: Get mapping success statistics
- `find_unmatched_formulas(df)`: Find unmapped formulas

### `excel_processor.py`
Handles Excel file operations and data management.

**Key Classes:**
- `ExcelProcessor`: Main class for Excel file processing
  - `load_excel_file()`: Load all sheets
  - `save_to_excel()`: Save processed data
  - `validate_reference_sheet()`: Validate reference data
  - `backup_original_file()`: Create backup

### `config.py`
Contains configuration constants and settings.

**Key Classes:**
- `ColumnNames`: Default column names
- `ProcessingSettings`: Processing configuration
- `LoggingConfig`: Logging settings
- `ValidationRules`: Data validation rules

## 📊 Input File Requirements

Your Excel file should contain:

1. **At least one sheet with SMILES data**
   - Column named `smiles`, `SMILES`, or `Smiles`

2. **Reference sheet (default: 'Sheet1') with:**
   - `chemical_formula` column: Chemical formulas
   - `Metabolite name` column: Corresponding metabolite names

### Example Input Structure:

**Sheet1 (Reference):**
| chemical_formula | Metabolite name | smiles |
|-----------------|----------------|---------|
| C8H10N4O2       | Caffeine       | Cn1cnc2c1c(=O)n(c(=O)n2C)C |
| C6H12O6         | Glucose        | C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O |

**Other Sheets:**
| SMILES | other_data |
|--------|------------|
| Cn1cnc2c1c(=O)n(c(=O)n2C)C | ... |
| C([C@@H]1[C@H]([C@@H]... | ... |

## 📈 Output

The tool generates an Excel file with:

1. **Original data preserved**
2. **Added `Formula` column** in all sheets with SMILES data
3. **Added `Metabolite name` column** in non-reference sheets (based on formula matching)

### Example Output:

**Sheet1:**
| chemical_formula | Metabolite name | smiles | Formula |
|-----------------|----------------|---------|---------|
| C8H10N4O2       | Caffeine       | Cn1cnc2c1c(=O)n(c(=O)n2C)C | C8H10N4O2 |

**Other Sheets:**
| SMILES | other_data | Formula | Metabolite name |
|--------|------------|---------|-----------------|
| Cn1cnc2c1c(=O)n(c(=O)n2C)C | ... | C8H10N4O2 | Caffeine |

## 📝 Configuration

Modify `config.py` to customize:

- Default file paths
- Column names
- Processing settings
- Logging configuration
- Validation rules

```python
# Example configuration changes
DEFAULT_INPUT_FILE = "my_data.xlsx"
DEFAULT_OUTPUT_FILE = "my_results.xlsx"

class ColumnNames:
    FORMULA = "Molecular_Formula"  # Change default formula column name
    METABOLITE_NAME = "Compound_Name"  # Change metabolite column name
```

## 🔧 Error Handling

The tool handles various error conditions:

- **Invalid SMILES**: Marked as "Invalid" in Formula column
- **Missing SMILES columns**: Sheet skipped with warning
- **Parsing errors**: Marked as "Error" in Formula column
- **Missing reference data**: Graceful failure with informative messages

## 📊 Statistics and Reporting

The tool provides comprehensive statistics:

- **Formula generation success rates**
- **Metabolite mapping success rates**
- **Per-sheet processing summaries**
- **Unmatched formulas identification**

## 🚨 Troubleshooting

### Common Issues:

1. **"ModuleNotFoundError: No module named 'rdkit'"**
   ```bash
   pip install rdkit
   # or
   conda install -c conda-forge rdkit
   ```

2. **"KeyError: 'smiles'"**
   - Check that your Excel file has a column named 'smiles', 'SMILES', or 'Smiles'

3. **"Reference sheet validation failed"**
   - Ensure Sheet1 (or specified reference sheet) has 'chemical_formula' and 'Metabolite name' columns

4. **Low mapping success rate**
   - Check that formulas in reference sheet match generated formulas
   - Verify SMILES data quality

### Debug Mode:

Run with verbose output for detailed debugging:
```bash
python process_metabolites.py input_file.xlsx --verbose
```

## 🧪 Testing

Run the example script to test functionality:
```bash
python example.py
```

This will demonstrate all major features using sample data.

## 📜 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Run with `--verbose` flag for detailed logs
3. Verify input file format and structure

## 🚀 Future Enhancements

Potential improvements:
- Support for additional molecular descriptors
- Batch processing capabilities
- GUI interface
- Additional output formats (CSV, JSON)
- Integration with chemical databases
- Support for InChI and other molecular representations

---

**Version**: 1.0.0  
**Author**: Vishal Ravi
**Date**: October 2025
