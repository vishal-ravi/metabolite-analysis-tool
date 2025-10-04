import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

def smiles_to_formula(smiles: str) -> str:
    """Convert SMILES to chemical formula"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            return rdMolDescriptors.CalcMolFormula(mol)
        else:
            return "Invalid"
    except:
        return "Error"

# Input/Output Excel filenames
input_file = "swissadmet 92.xlsx"    # change to your file
output_file = "output_with_formulas.xlsx"

# Read all sheets
xls = pd.ExcelFile(input_file)
sheet_names = xls.sheet_names

# Dictionary to store updated DataFrames
updated_sheets = {}

for sheet in sheet_names:
    df = pd.read_excel(input_file, sheet_name=sheet)

    # Check for SMILES column (case-insensitive)
    smiles_column = None
    for col in df.columns:
        if col.lower() == 'smiles':
            smiles_column = col
            break
    
    if smiles_column:
        df["Formula"] = df[smiles_column].apply(smiles_to_formula)
        print(f"Sheet '{sheet}': Added Formula column using '{smiles_column}' column.")
    else:
        print(f"Sheet '{sheet}' does not have a 'SMILES' column. Skipping.")

    updated_sheets[sheet] = df

# Create a mapping from chemical_formula to Metabolite name from Sheet1
sheet1_df = updated_sheets.get('Sheet1')
formula_to_metabolite = {}

if sheet1_df is not None and 'chemical_formula' in sheet1_df.columns and 'Metabolite name' in sheet1_df.columns:
    # Create mapping dictionary, handling potential duplicates by taking the first occurrence
    for idx, row in sheet1_df.iterrows():
        formula = row['chemical_formula']
        metabolite = row['Metabolite name']
        if pd.notna(formula) and pd.notna(metabolite) and formula not in formula_to_metabolite:
            formula_to_metabolite[formula] = metabolite
    print(f"Created mapping for {len(formula_to_metabolite)} unique formulas from Sheet1")

# Add Metabolite name column to other sheets based on Formula matching
for sheet_name, df in updated_sheets.items():
    if sheet_name != 'Sheet1' and 'Formula' in df.columns:
        # Add Metabolite name column by matching Formula with chemical_formula from Sheet1
        df['Metabolite name'] = df['Formula'].map(formula_to_metabolite)
        
        # Count matches
        matches = df['Metabolite name'].notna().sum()
        total = len(df)
        print(f"Sheet '{sheet_name}': Added Metabolite name column with {matches}/{total} matches")
        
        updated_sheets[sheet_name] = df

# Save back to Excel with all sheets
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for sheet, df in updated_sheets.items():
        df.to_excel(writer, sheet_name=sheet, index=False)

print(f"Updated Excel saved as: {output_file}")
