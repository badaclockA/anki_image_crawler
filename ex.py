import csv
import sys

def transform_text(text):
    # First replace || with <br><br>
    text = text.replace('||', '<br><br>')
    
    # Then replace remaining single | with <br>
    text = text.replace('|', '<br>')
    
    return text

def process_csv(input_file, output_file):
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                
                for row in reader:
                    # Apply the transformation to each cell in the row
                    transformed_row = [transform_text(cell) for cell in row]
                    writer.writerow(transformed_row)
                    
        print(f"Successfully processed {input_file} and saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ex.py input.csv output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_csv(input_file, output_file)
