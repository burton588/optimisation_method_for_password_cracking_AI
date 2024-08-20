import json
from zxcvbn import zxcvbn
from tqdm import tqdm

def load_passwords_from_file(filename):
    """Load passwords from a file and return a set of unique passwords."""
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        return set(password.strip() for password in file.readlines())

def classify_passwords_in_files(filenames, exclusion_set):
    password_strength_counts = {filename: {score: 0 for score in range(5)} for filename in filenames}

    # Read passwords from each file and classify them using zxcvbn
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            passwords = {password.strip() for password in file.readlines()}  # Using a set to ensure uniqueness
            unique_passwords = passwords - exclusion_set  # Only classify passwords not in the exclusion set
            
            for password in tqdm(unique_passwords):
                analysis = zxcvbn(password)
                score = analysis['score']
                password_strength_counts[filename][score] += 1

    return password_strength_counts

# File containing the passwords to exclude
exclusion_file = '../../rockyou.txt'

# Load exclusion passwords into a set
exclusion_passwords = load_passwords_from_file(exclusion_file)

# List of your password files to classify
password_files = [
                  'matching_passwords_mangaFox_250m_manga.txt'
                  ]

# Classify passwords in each file, excluding those found in the exclusion list
password_strength_counts = classify_passwords_in_files(password_files, exclusion_passwords)

# Print the results
for filename, counts in password_strength_counts.items():
    print(f"Password strength counts for {filename}:")
    for score, count in counts.items():
        print(f"  Score {score}: {count} passwords")
