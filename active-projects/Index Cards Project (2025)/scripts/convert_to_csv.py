import csv
import sys

def convert_psv_to_csv(input_file, output_file):
    """
    Converts a pipe-separated values (PSV) file to a comma-separated values (CSV) file.

    Args:
        input_file (str): The path to the input PSV file.
        output_file (str): The path to the output CSV file.
    """
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as psv_file:
            # Use the CSV reader with the pipe delimiter
            reader = csv.reader(psv_file, delimiter='|')

            with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
                # Use the standard CSV writer
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

                # Read from the PSV and write to the CSV row by row
                for row in reader:
                    writer.writerow(row)

        print(f"Successfully converted '{input_file}' to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_to_csv.py <input_psv_file> <output_csv_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    convert_psv_to_csv(input_path, output_path)
