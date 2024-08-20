import os
import pickle
import json
import time
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def execute_sparql(query, retries=5, backoff_factor=1.0):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    for attempt in range(retries):
        try:
            return sparql.query().convert()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))  # Exponential backoff
            else:
                return None  # Re-raise the last exception if all retries fail


def get_links():
    query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?link ?label
        WHERE {
            <http://dbpedia.org/resource/Video_game> dbo:wikiPageWikiLink ?link .
            ?link rdfs:label ?label .
            FILTER (LANG(?label) = "en")
        }
        
    """
    return execute_sparql(query)

def get_sublinks(link):
    query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?innerSubLink ?label
        WHERE {{
            <{link}> dbo:wikiPageWikiLink ?innerSubLink .
            ?innerSubLink rdfs:label ?label .
            FILTER (LANG(?label) = "en")
        }}
        LIMIT 100
        
    """
    return execute_sparql(query)

def get_subsublinks(sublink):
    query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?innerSubSubLink ?label
        WHERE {{
            <{sublink}> dbo:wikiPageWikiLink ?innerSubSubLink .
            ?innerSubSubLink rdfs:label ?label .
            FILTER (LANG(?label) = "en")
        }}
        LIMIT 50
    """
    return execute_sparql(query)

def save_state(state, filename="state.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(state, f)

def load_state(filename="state.pkl"):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return None

def save_links_json(data, filename="links.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def load_links_json(filename="links.json"):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Load the previous state if available
state = load_state()
if state:
    start_link_index = state
else:
    start_link_index = 0

# Load the links JSON if available
links_json = load_links_json()
if links_json:
    links = links_json
else:
    links = get_links()
    save_links_json(links)

try:
    total_links = len(links["results"]["bindings"])
    print(f"Total links to process: {total_links}")

    for i, link in enumerate(links["results"]["bindings"], start=1):
        if i < start_link_index:
            continue
        link_url = link["link"]["value"]
        link_label = link["label"]["value"]
        
        labels = [link_label]
        print(f"Processing link {i} of {total_links}: {link_url}")

        sublinks = get_sublinks(link_url)
        if sublinks is None:
            print(f"  Skipping link {i} due to repeated failures.")
            continue

        total_sublinks = len(sublinks["results"]["bindings"])
        print(f"  Total sublinks to process for link {i}: {total_sublinks}")

        for j, sublink in enumerate(sublinks["results"]["bindings"], start=1):
            sublink_url = sublink["innerSubLink"]["value"]
            sublink_label = sublink["label"]["value"]
            labels.append(sublink_label)  # Save the sublink label to the list
            print(f"  Processing sublink {j} of {total_sublinks} for link {i}")

            subsublinks = get_subsublinks(sublink_url)
            if subsublinks is None:
                print(f"    Skipping sublink {j} due to repeated failures.")
                continue

            total_subsublinks = len(subsublinks["results"]["bindings"])

            for k, subsublink in enumerate(subsublinks["results"]["bindings"], start=1):
                subsublink_label = subsublink["label"]["value"]
                labels.append(subsublink_label)  # Save the subsublink label to the list

        # Write the labels to the file after processing each link and its sublinks
        with open('labels_videogame.txt', 'a', encoding='utf-8') as f:
            for label in labels:
                f.write(label + '\n')

        # Save the current state after processing each link
        print(i)
        save_state(i)
        
except Exception as e:
    print(f"An error occurred: {e}")
    save_state(i)

print("Processing complete.")
