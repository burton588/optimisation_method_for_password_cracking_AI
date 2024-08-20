import string
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from unidecode import unidecode
from tqdm import tqdm
import ahocorasick
import json
from collections import OrderedDict

# Use stopwords from sklearn
stop_words = set(ENGLISH_STOP_WORDS)
MAXCHARS = 16

# Define the reverse mappings
reverse_mappings = {
    '@': 'a',
    '4': 'a',
    '6': 'b',
    '<': 'c',
    '{': 'c',
    '3': 'e',
    '9': 'g',
    '1': 'i',
    '!': 'i',
    '0': 'o',
    '9': 'q',
    '5': 's',
    '$': 's',
    '7': 't',
    '+': 't',
    '%': 'x'
}

def reverse_map(input_string):
    """
    Function to reverse map special characters to their original alphabetic characters
    based on predefined rules.
    
    Args:
    input_string (str): The string to be reverse mapped.
    
    Returns:
    str: The reverse mapped string.
    """
    output_string = []
    for char in input_string:
        if char in reverse_mappings:
            output_string.append(reverse_mappings[char])
        else:
            output_string.append(char)
    return ''.join(output_string)

def gather_possible_phrases(entry):
    # Transliterate to ASCII
    entry = unidecode(entry)
    # Remove words in parentheses
    entry = re.sub(r'\(.*?\)', '', entry)
    # Remove special characters
    cleaned_entry = entry.translate(str.maketrans('', '', string.punctuation))
    # Split entry into words
    cleaned_entry = cleaned_entry.lower()
    words = cleaned_entry.split()
    
    possible_phrases = []
    
    filtered_words = [word for word in words if word not in stop_words]
    filtered_words_concat = ''.join(filtered_words)
    possible_phrases += filtered_words
    if len(filtered_words) != 1:
        possible_phrases.append(filtered_words_concat)
    possible_phrases = [phrase for phrase in possible_phrases if (3 <= len(phrase) <= 16 and not phrase.isnumeric())]

    return possible_phrases

def remove_duplicates_preserve_order(entries):
    seen = set()
    result = []
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            result.append(entry)
    return result

def build_and_search_automaton(password_file, phrases):
    # Initialize a dictionary to store the counts

    counts = OrderedDict((entry, (0, [])) for entry in phrases)

    # Initialize the Aho-Corasick automaton
    A = ahocorasick.Automaton()

    # Add phrases to the automaton
    for phrase in phrases:
        A.add_word(phrase, phrase)

    A.make_automaton()

    # First, count the total number of lines in the file for progress tracking
    total_lines = sum(1 for _ in open(password_file, 'r', encoding='utf-8', errors='ignore'))

    # Process the file with a progress bar
    with open(password_file, 'r', encoding='utf-8', errors='ignore') as file:
        for line in tqdm(file, total=total_lines, desc="Processing passwords"):
            password_original= line.strip()
            if len(password_original) > 16:
                continue
            password = password_original.lower()
            password = reverse_map(password)
            for end_index, phrase in A.iter(password):
                count, passwords = counts[phrase]
                counts[phrase] = (count + 1, passwords + [password_original])

    # Collect all phrases that have at least one hit
        # Collect all phrases that have at least one hit
    phrases_with_hits = OrderedDict((phrase, (count, passwords)) for phrase, (count, passwords) in counts.items() if count > 0)
    del A

    # Save the results to a JSON file
    with open("dictionary_ignis_10m.json", 'w', encoding='utf-8') as f:
        json.dump(phrases_with_hits, f, ensure_ascii=False, indent=4)

    return phrases_with_hits

# File paths
#input_file_path = 'manga/labels_manga_sorted.txt'
#output_file_path = 'manga/manga_passwords_ready.txt'
#password_file_path = 'rockyou.txt'

input_file_path = 'wikipedia_all_entities.txt'
output_file_path = ''
password_file_path = 'ignis-10M.txt'

# Read entries from input file
with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as file:
    entries = file.readlines()

# Gather all possible phrases from entries
all_possible_phrases = []
for idx, entry in enumerate(entries):
    print(f"Processing entry {idx + 1}/{len(entries)}")
    all_possible_phrases.extend(gather_possible_phrases(entry.strip()))

# Remove duplicates while preserving order
all_possible_phrases = remove_duplicates_preserve_order(all_possible_phrases)

# Search for all phrases in the password file
phrases_with_hits = build_and_search_automaton(password_file_path, all_possible_phrases)

# Write phrases with hits to the output file
""" with open(output_file_path, 'w', encoding='utf-8', errors='ignore') as file:
    for phrase in phrases_with_hits:
        file.write(phrase + '\n')

print(f"Phrases with hits have been written to {output_file_path}") """
