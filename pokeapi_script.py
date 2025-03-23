import requests
import csv

def get_pokemon_data(identifier):
    """
    Conecta con la PokeAPI y extrae información básica de un Pokémon.
    Parámetro:
      identifier: nombre o número del Pokémon.
    Retorna:
      Diccionario con los datos extraídos o None si no se encuentra el Pokémon.
    """
    url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data['name']
        pokemon_id = data['id']
        types = ", ".join([t['type']['name'] for t in data['types']])
        stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
        abilities = ", ".join([a['ability']['name'] for a in data['abilities']])
        image_url = data['sprites']['front_default']  # Imagen principal
        return {
            'name': name,
            'id': pokemon_id,
            'types': types,
            'stats': stats,
            'abilities': abilities,
            'image_url': image_url
        }
    else:
        print("Error: Pokémon no encontrado")
        return None

def export_to_csv(data, filename="pokemon_data.csv"):
    """
    Exporta la información de un Pokémon a un archivo CSV.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['name', 'id', 'types', 'stats', 'abilities', 'image_url']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    pokemon_identifier = input("Introduce el nombre o número del Pokémon: ")
    data = get_pokemon_data(pokemon_identifier)
    if data:
        print("Datos del Pokémon:")
        print(data)
        export_to_csv(data)
        print("Datos exportados a pokemon_data.csv")
