import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
import tkinter as tk

from core.executor import find_app
from core.storage import get_user_data, save_web_search
from core.listener import give_audio_response
from ui.popup import create_window, create_element

def get_search_results(query, max_results=5):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=max_results)]
    return results

def show_results(results):
    window = create_window('Search Results', size="600x400", topmost=False)
    
    canvas = tk.Canvas(window)
    scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    if isinstance(results, str):
        results = json.loads(results)
    
    for idx, result in enumerate(results, 1):
        result_frame = tk.Frame(scrollable_frame, relief=tk.RIDGE, borderwidth=2, padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        title_label = tk.Label(result_frame, text=f"{idx}. {result.get('title', 'No title')}", font=("Arial", 12, "bold"), wraplength=550, justify=tk.LEFT)
        title_label.pack(anchor=tk.W)
        
        body_label = tk.Label(result_frame, text=result.get('body', 'No content'), font=("Arial", 10), wraplength=550, justify=tk.LEFT)
        body_label.pack(anchor=tk.W, pady=(5, 0))
        
        source_label = tk.Label(result_frame, text=f"Source: {result.get('href', 'Unknown')}", font=("Arial", 9, "italic"), fg="blue", wraplength=550, justify=tk.LEFT)
        source_label.pack(anchor=tk.W, pady=(5, 0))
        give_audio_response(f"Result {idx}: {result.get('title', 'No title')}")
        give_audio_response(result.get('body', 'No content'))
    
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    window.mainloop()

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
            })
        except Exception:
            data_mapping.append({"source": res['href'], "content": res['body']})

    print(results)
    save_web_search(results)
    show_results(results)
    return results