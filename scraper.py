import feedparser
import json
import os
from datetime import datetime
from locations import SERBIA_LOCATIONS

# Spisak RSS izvora sa tvoje liste (ovde su neki od glavnih, lako ćemo dodati ostale)
SOURCES = [
    "https://n1info.rs/feed/", 
    "https://nova.rs/feed/", 
    "https://www.danas.rs/feed/",
    "https://www.juznevesti.com/rss/Srbija", 
    "https://www.021.rs/rss",
    "https://crta.rs/feed/", 
    "https://www.cins.rs/feed/", 
    "https://www.krik.rs/feed/",
    "https://birn.rs/feed/",
    "https://infovranjske.rs/feed/",
    "https://jugpress.com/feed/"
]

# Reči koje robot traži da bi znao da je reč o nepravilnosti
KEYWORDS = ["izbor", "nepravilnost", "neregularnost", "bugarski voz", "spisak", "glas", "kupovina", "ucena", "pritisak", "biračk"]

def scrape():
    # 1. Prvo pročitaj šta već imamo u svesci (data.json)
    all_data = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except:
                all_data = []

    # Napravi spisak linkova koje već imamo da ih ne bismo duplirali
    existing_links = {item['link'] for item in all_data}
    new_entries = []

    # 2. Obiđi svaki medij sa spiska
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # Ako smo tu vest već ranije zapisali, preskoči je
                if entry.link in existing_links:
                    continue
                
                # Proveri da li se u naslovu pominje neka od naših ključnih reči
                content = (entry.title + " " + getattr(entry, 'summary', '')).lower()
                if any(kw in content for kw in KEYWORDS):
                    
                    # Pokušaj da prepoznaš grad iz teksta koristeći locations.py
                    found_city = "Srbija"
                    coords = [44.0165, 21.0059] # Centar Srbije kao rezerva
                    
                    for city, loc in SERBIA_LOCATIONS.items():
                        if city.lower() in content:
                            found_city = city
                            coords = loc
                            break
                    
                    # Ako je našao ključnu reč, dodaj vest u novu listu
                    new_entries.append({
                        "title": entry.title,
                        "link": entry.link,
                        "city": found_city,
                        "lat": coords[0],
                        "lng": coords[1],
                        "source": url.split("//")[1].split("/")[0], # Ime sajta (npr. n1info.rs)
                        "date": datetime.now().strftime("%d.%m.%Y")
                    })
        except Exception as e:
            print(f"Greška prilikom čitanja {url}: {e}")

    # 3. Dodaj nove vesti na početak stare liste i sve zajedno sačuvaj u data.json
    combined_data = new_entries + all_data
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape()
