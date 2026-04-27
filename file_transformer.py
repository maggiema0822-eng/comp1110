import csv
import json
from pathlib import Path


def convert_csv_to_json(input_path, output_path):
    """
    Convert a CSV file to JSON format.

    Args:
        input_path (str): Path to the input CSV file
        output_path (str): Path where the JSON file will be saved

    Returns:
        list: List of dictionaries representing the converted data
    """
    data = []

    # Open CSV file with UTF-8 encoding (handling BOM if present)
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            converted = {}
            for key, value in row.items():
                key = key.strip()
                if value == '' or value is None:
                    converted[key] = ""
                else:
                    # Attempt to convert numeric strings to int or float
                    try:
                        if '.' in value:
                            converted[key] = float(value)
                        else:
                            converted[key] = int(value)
                    except (ValueError, AttributeError):
                        converted[key] = value
            data.append(converted)

    # Write JSON file with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully altered {input_path} → {output_path} ({len(data)} in total)")
    return data


def convert_excel_to_json(input_path, output_path):
    """
    Convert an Excel file (.xlsx or .xls) to JSON format.

    Args:
        input_path (str): Path to the input Excel file
        output_path (str): Path where the JSON file will be saved

    Returns:
        list: List of dictionaries representing the converted data, or None if pandas is not installed
    """
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        print("Please install pandas")
        return None

    # Read Excel file into DataFrame
    df = pd.read_excel(input_path)

    # Replace NaN values with empty strings
    df = df.fillna("")

    data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            value = row[col]

            # Handle different data types appropriately
            if value == "":
                record[col] = ""
            elif pd.isna(value):
                record[col] = ""
            elif isinstance(value, pd.Timestamp):
                # Convert datetime to ISO format string
                record[col] = value.strftime('%Y-%m-%d')
            elif isinstance(value, (np.int64, np.int32)):
                record[col] = int(value)
            elif isinstance(value, (np.float64, np.float32)):
                record[col] = float(value)
            elif isinstance(value, (int, float, str, bool)):
                record[col] = value
            elif value is None:
                record[col] = ""
            else:
                record[col] = str(value)

        data.append(record)

    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully altered {input_path} → {output_path} ({len(data)} in total)")
    return data


def detect_file_type(file_path):
    """
    Detect the file type based on extension.

    Args:
        file_path (str): Path to the file

    Returns:
        str: 'csv' for CSV files, 'excel' for Excel files, None for unsupported types
    """
    ext = Path(file_path).suffix.lower()
    if ext == '.csv':
        return 'csv'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'
    else:
        return None


def get_fields(file_path):
    """
    Extract column/field names from a CSV or Excel file.

    Args:
        file_path (str): Path to the file

    Returns:
        list: List of field names, or None if extraction fails
    """
    ext = Path(file_path).suffix.lower()

    try:
        if ext == '.csv':
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                return reader.fieldnames
        elif ext in ['.xlsx', '.xls']:
            try:
                import pandas as pd
                # Read only the header row to get column names
                df = pd.read_excel(file_path, nrows=0)
                return list(df.columns)
            except ImportError:
                return None
    except Exception:
        return None
    return None


def convert_file(input_path, output_path):
    """
    Convert a file to JSON based on its detected type.

    Args:
        input_path (str): Path to the input file
        output_path (str): Path where the JSON file will be saved

    Returns:
        list: Converted data, or None if conversion fails
    """
    file_type = detect_file_type(input_path)

    if file_type == 'csv':
        return convert_csv_to_json(input_path, output_path)
    elif file_type == 'excel':
        return convert_excel_to_json(input_path, output_path)
    else:
        print(f"Do not support: {input_path}")
        return None


def find_and_convert():
    """
    Automatically find CSV and Excel files in the current directory,
    identify budget rules and transactions files based on column names,
    and convert them to JSON format.

    Budget rule files are identified by containing 'category', 'period', and 'threshold' columns.
    Transaction files are identified by containing 'date', 'amount', and 'category' columns.
    """
    # Find all CSV and Excel files in current directory
    csv_files = list(Path('.').glob('*.csv'))
    excel_files = list(Path('.').glob('*.xlsx')) + list(Path('.').glob('*.xls'))
    all_files = csv_files + excel_files

    if not all_files:
        print("Could not find any files to transform")
        return

    print(f"Found {len(all_files)} files（CSV: {len(csv_files)}, Excel: {len(excel_files)}）\n")

    budget_file = None
    transaction_file = None

    # Analyze each file's column structure to identify its type
    for file_path in all_files:
        fields = get_fields(file_path)

        if fields:
            fields_lower = [f.lower() for f in fields]
            # Check for budget rule file signature
            if 'category' in fields_lower and 'period' in fields_lower and 'threshold' in fields_lower:
                budget_file = file_path
            # Check for transaction file signature
            elif 'date' in fields_lower and 'amount' in fields_lower and 'category' in fields_lower:
                transaction_file = file_path

    # Fallback: identify budget file by filename if signature detection failed
    if budget_file is None:
        for f in all_files:
            if 'budget' in f.name.lower() or 'rule' in f.name.lower():
                budget_file = f
                break
        # If still not found, use the first file as budget file
        if budget_file is None and len(all_files) >= 1:
            budget_file = all_files[0]

    # Fallback: identify transaction file by filename if signature detection failed
    if transaction_file is None:
        for f in all_files:
            if 'transaction' in f.name.lower() or 'data' in f.name.lower():
                transaction_file = f
                break
        # If still not found, use the second file or first if only one exists
        if transaction_file is None and len(all_files) >= 2:
            transaction_file = all_files[1] if len(all_files) > 1 else all_files[0]

    # Ensure budget and transaction files are not the same if multiple files exist
    if transaction_file == budget_file and len(all_files) > 1:
        for f in all_files:
            if f != budget_file:
                transaction_file = f
                break

    # Perform conversions
    if budget_file:
        convert_file(budget_file, 'budget_rules.json')
    else:
        print("Could not find budget file")

    if transaction_file and transaction_file != budget_file:
        convert_file(transaction_file, 'transactions.json')
    else:
        print("Could not find transaction file")


if __name__ == "__main__":
    """Entry point: run the file conversion when script is executed directly."""
    print("Start to transform\n")
    find_and_convert()
    print("\nTransformation complete\n")