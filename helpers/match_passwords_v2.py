from tqdm import tqdm

# Function to read passwords from a file and return as a set (assuming passwords2 is smaller)
def read_passwords_set(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        return set(line.strip() for line in file)

# Function to find matching passwords between a large file and a set with progress bar
def find_matching_passwords(large_filename, small_set):
    matches = set()
    # Count total lines in large file for accurate progress bar
    #with open(large_filename, 'r', encoding='utf-16', errors='ignore') as file:
    #    total_lines = sum(1 for _ in file)
    total_lines = 968235432
    print(total_lines)
    with open(large_filename, 'r', encoding='utf-8', errors='ignore') as file:
        for line in tqdm(file, total=total_lines, desc="Finding matches", unit="password"):
            password = line.strip()
            if password in small_set:
                matches.add(password)
    print(len(matches))
    return matches

# Function to save matching passwords to a file with count at the first line
def save_matching_passwords(filename, matches):
    with open(filename, 'w') as file:
        file.write(f"Number of matches: {len(matches)}\n")
        for password in matches:
            file.write(f"{password}\n")

# Main script
def main():
    # File paths
    small_file = 'MangaTraders_passwords.txt'
    large_file = '../ignis-10M.txt'
    output_file = 'matching_passwords_manga_ignis.txt'
    
    # Load smaller file into memory as a set
    passwords2_set = read_passwords_set(small_file)
    
    # Find matching passwords
    matching_passwords = find_matching_passwords(large_file, passwords2_set)

    # Save matching passwords to a file
    save_matching_passwords(output_file, matching_passwords)
    
    print(f"Matching passwords saved to {output_file}")

if __name__ == "__main__":
    main()
