import requests
import csv
import time
import base64

def get_all_pokemon(limit=1118, offset=0):
    """
    Obtiene la lista de todos los Pokémon desde la PokeAPI.
    """
    url = f"https://pokeapi.co/api/v2/pokemon?limit={limit}&offset={offset}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        print("Error: no se pudo obtener la lista de Pokémon")
        return []

def get_pokemon_data(url):
    """
    Dado el URL de detalles de un Pokémon, extrae la información relevante.
    Además, descarga la imagen y la codifica en base64 para incluirla en el CSV.
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data['name']
        pokemon_id = data['id']
        types = ", ".join([t['type']['name'] for t in data['types']])
        stats = ", ".join([f"{stat['stat']['name']}:{stat['base_stat']}" for stat in data['stats']])
        abilities = ", ".join([a['ability']['name'] for a in data['abilities']])
        image_url = data['sprites']['front_default']
        
        # Descargar y codificar la imagen en base64
        image_base64 = ""
        if image_url:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_base64 = base64.b64encode(image_response.content).decode('utf-8')
        
        return {
            'name': name,
            'id': pokemon_id,
            'types': types,
            'stats': stats,
            'abilities': abilities,
            'image_base64': image_base64
        }
    else:
        print(f"Error: No se pudo obtener datos desde {url}")
        return None

def export_all_to_csv(pokemon_list, filename="all_pokemon_data.csv"):
    """
    Exporta la lista de Pokémon a un archivo CSV con todos los datos,
    incluida la imagen codificada en base64.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['name', 'id', 'types', 'stats', 'abilities', 'image_base64']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for pokemon in pokemon_list:
            writer.writerow(pokemon)

if __name__ == "__main__":
    print("Obteniendo la lista de todos los Pokémon...")
    pokemon_entries = get_all_pokemon(limit=1118)
    print(f"Se encontraron {len(pokemon_entries)} Pokémon.")
    
    all_pokemon_data = []
    for i, entry in enumerate(pokemon_entries):
        print(f"Procesando {i+1}/{len(pokemon_entries)}: {entry['name']}")
        details = get_pokemon_data(entry['url'])
        if details:
            all_pokemon_data.append(details)
        time.sleep(0.2)  # Pausa para no saturar la API
    
    export_all_to_csv(all_pokemon_data)
    print("Todos los datos han sido exportados a 'all_pokemon_data.csv'")
