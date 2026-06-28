import csv
import sys
def replace_pipe_with_br(input_file, output_file):
    """
    Replace all pipe (|) characters with <br> in a CSV file.
    """
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                
                for row in reader:
                    # Replace | with <br> in each field
                    new_row = [field.replace('|', '<br>') for field in row]
                    writer.writerow(new_row)
                    
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python ex2.py input_file.csv output_file.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    replace_pipe_with_br(input_file, output_file)

if __name__ == "__main__":
    main()