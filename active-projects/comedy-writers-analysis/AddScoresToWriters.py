import csv
import os

def main():
    # Input and output file paths
    writer_scores_file = 'writer_scores.csv'
    comedy_writers_file = 'comedy_writers.csv'
    output_file = 'comedy_writers_with_scores.csv'
    
    if not os.path.exists(writer_scores_file):
        print(f"Error: {writer_scores_file} not found")
        return
        
    if not os.path.exists(comedy_writers_file):
        print(f"Error: {comedy_writers_file} not found")
        return
    
    # Read writer scores into a dictionary for quick lookup
    writer_scores = {}
    with open(writer_scores_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            writer_name = row['Writer']
            writer_scores[writer_name.lower()] = {
                'Total Score': row['Total Score'],
                'Writing Points': row['Writing Points'],
                'Creator Points': row['Creator Points']
            }
    
    # Read comedy writers and add scores
    comedy_writers_with_scores = []
    
    with open(comedy_writers_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['Total Score', 'Writing Points', 'Creator Points']
        
        for row in reader:
            writer_name = row['Writer Name']
            
            # Look up writer's score
            score_data = writer_scores.get(writer_name.lower(), {})
            
            # Add score data to row
            row['Total Score'] = score_data.get('Total Score', '')
            row['Writing Points'] = score_data.get('Writing Points', '')
            row['Creator Points'] = score_data.get('Creator Points', '')
            
            comedy_writers_with_scores.append(row)
    
    # Write the updated comedy writers CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comedy_writers_with_scores)
    
    print(f"Successfully added score data to comedy writers.")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()