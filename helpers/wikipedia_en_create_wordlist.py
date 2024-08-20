from datasets import load_dataset
from tqdm import tqdm

def extract_titles(output_file):
    # Load the Wikipedia dataset from Hugging Face
    dataset = load_dataset("wikimedia/wikipedia", "20231101.en", split='train')

    titles = set()
    print(dataset)
    # Process each example in the dataset
    for example in tqdm(dataset):
        title = example['title']
        titles.add(title.strip())

    # Save the titles to a file
    with open(output_file, 'w', encoding='utf-8') as f:
        for title in sorted(titles):
            f.write(f"{title}\n")

# Path to the output file
output_file = 'wikipedia_all_entities.txt'
extract_titles(output_file)