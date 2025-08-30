import csv
import re

# Define input and output file paths
input_file = 'paste.txt'
output_file = 'comedy_writers.csv'

# Define the column headers for the CSV (matching your Airtable fields)
fieldnames = ['Writer Name', 'Total Ep Cnt', 'Per-Show Breakdown', 'Top 5 TV Credits (Year)', 'Prelim Sources']

# Open the output file
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Open and process the input file
    with open(input_file, 'r', encoding='utf-8') as infile:
        # Skip the header line
        next(infile)
        
        for line in infile:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Extract data using regex to handle the CSV-like format with quotes
            match = re.match(r'^\d+,"([^"]+)",(\d+),"([^"]+)","([^"]+)","([^"]+)"$', line.strip())
            
            if match:
                writer_name = match.group(1)
                ep_count = match.group(2)
                show_breakdown = match.group(3)
                tv_credits = match.group(4)
                sources = match.group(5)
                
                # Write to CSV
                writer.writerow({
                    'Writer Name': writer_name,
                    'Total Ep Cnt': ep_count,
                    'Per-Show Breakdown': show_breakdown,
                    'Top 5 TV Credits (Year)': tv_credits,
                    'Prelim Sources': sources
                })
            else:
                print(f"Could not parse line: {line.strip()}")

print(f"CSV file created successfully: {output_file}")