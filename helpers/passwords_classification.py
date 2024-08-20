# code used for zxcvbn classification for the matched passwords against the target database 

import json
from zxcvbn import zxcvbn
from tqdm import tqdm

def classify_passwords_in_files(filenames):
    password_strength_counts = {filename: {score: 0 for score in range(5)} for filename in filenames}

    # Read passwords from each file and classify them using zxcvbn
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            passwords = [password.strip() for password in file.readlines()]
            for password in tqdm(passwords):
                analysis = zxcvbn(password)
                score = analysis['score']
                password_strength_counts[filename][score] += 1

    return password_strength_counts

# List of your password files
password_files = [
                  'matching_passwords_manga_ignis.txt'
                  ]

# Classify passwords in each file
password_strength_counts = classify_passwords_in_files(password_files)

# Print the results
for filename, counts in password_strength_counts.items():
    print(f"Password strength counts for {filename}:")
    for score, count in counts.items():
        print(f"  Score {score}: {count} passwords")