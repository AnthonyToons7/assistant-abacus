import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from handlers.ProgramHandler import find_app
from handlers.StorageHandler import get_user_data

def get_search_results(query, max_results=5):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=max_results)]
    return results

def search_web(prompt):
    print(f"Searching for: {prompt}...")
    results = get_search_results(prompt, max_results=3)
    data_mapping = []

    for res in results:
        try:
            response = requests.get(res['href'], timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ' '.join([p.text for p in soup.find_all('p')])
            data_mapping.append({
                "source": res['href'],
                "content": text[:1000] # Max characters, dont overload!
        except Exception:
            data_mapping.append({"source": res['href'], "content": res['body']})

    return results