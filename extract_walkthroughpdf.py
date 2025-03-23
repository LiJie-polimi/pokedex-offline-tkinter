import os
import re
import csv
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Adjust this path if Tesseract is not on your PATH
# For example, on Windows you might need:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def pdf_to_text_ocr(pdf_path, dpi=300):
    """
    Convert a PDF to text using OCR.
    The PDF is converted into images (one per page), and pytesseract extracts text from each image.
    """
    try:
        pages = convert_from_path(pdf_path, dpi=dpi)
        full_text = ""
        for i, page in enumerate(pages):
            print(f"OCR processing page {i+1} of {len(pages)} in {pdf_path}...")
            text = pytesseract.image_to_string(page)
            full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"Error during OCR processing of {pdf_path}: {e}")
        return ""

def extract_segments(full_text):
    """
    Splits the extracted text into segments.
    Here, we try to split based on the occurrence of key words such as "Gym" or "Before Gym".
    You may need to adjust this depending on the OCR output.
    """
    # Try a simple segmentation based on the keyword "Gym"
    segments = re.split(r"(?i)(Gym\s*Battle\s*\d+|Before\s*Gym)", full_text)
    combined_segments = []
    if len(segments) < 2:
        combined_segments.append(("Full Text", full_text))
    else:
        # Combine segments in pairs: heading and following text.
        # (This is a simplistic approach – you might need to adjust for your actual OCR text.)
        for i in range(1, len(segments), 2):
            heading = segments[i].strip()
            content = segments[i+1] if i+1 < len(segments) else ""
            combined_segments.append((heading, content))
    print(f"Found {len(combined_segments)} segments.")
    return combined_segments

def parse_wild_pokemon(segment_text):
    """
    Parse wild Pokémon details from the text segment.
    This regex is designed to capture entries like:
       "Zigzagoon (Lv.3-5, Routes around Rustboro City)"
    Adjust the regex as needed for your OCR output.
    """
    pattern = re.compile(
        r"(?P<Name>[A-Za-z’\-\s]+)\s*\(Lv\.?\s*(?P<LevelRange>[\d\-]+)\s*,\s*(?P<Location>[^)]+)\)",
        re.IGNORECASE
    )
    matches = pattern.finditer(segment_text)
    wild_pokemon = []
    for m in matches:
        wild_pokemon.append({
            "Name": m.group("Name").strip(),
            "LevelRange": m.group("LevelRange").strip(),
            "Location": m.group("Location").strip()
        })
    if wild_pokemon:
        print("Wild Pokémon parsed in segment:", wild_pokemon)
    return wild_pokemon

def parse_gym_team(segment_text):
    """
    Parse gym leader/champion team compositions.
    This regex looks for patterns such as:
       "Geodude (Lv.12: HP 30, Atk 35, Def 40, Spd 20)"
    Adjust as needed.
    """
    pattern = re.compile(
        r"(?P<Pokemon>[A-Za-z’\-\s]+)\s*\(Lv\.?\s*(?P<Level>\d+)\s*:\s*HP\s*(?P<HP>\d+),\s*Atk\s*(?P<Attack>\d+),\s*Def\s*(?P<Defense>\d+),\s*Spd\s*(?P<Speed>\d+)\)",
        re.IGNORECASE
    )
    matches = pattern.finditer(segment_text)
    team = []
    for m in matches:
        team.append({
            "Pokemon": m.group("Pokemon").strip(),
            "Level": m.group("Level").strip(),
            "HP": m.group("HP").strip(),
            "Attack": m.group("Attack").strip(),
            "Defense": m.group("Defense").strip(),
            "Speed": m.group("Speed").strip()
        })
    if team:
        print("Gym team parsed in segment:", team)
    return team

def extract_additional_notes(heading, content):
    """
    Extract a brief note from the beginning of the segment.
    """
    lines = content.strip().splitlines()
    note = " ".join(lines[:3]) if lines else ""
    return f"Segment starting with '{heading}'; {note}"

def process_pdf(pdf_path, game_title, region):
    """
    Process an individual PDF file using OCR, then segment and parse the text.
    """
    full_text = pdf_to_text_ocr(pdf_path)
    segments = extract_segments(full_text)
    data = []
    for heading, content in segments:
        wild_pokemon = parse_wild_pokemon(content)
        gym_team = parse_gym_team(content)
        notes = extract_additional_notes(heading, content)
        
        # Attempt to extract a leader/champion name from the heading.
        leader = "Unknown"
        leader_match = re.search(r"(Before\s*Gym(?:\s*Battle)?|Gym\s*Battle\s*\d+)\s*([^:\n]+)", heading, re.IGNORECASE)
        if leader_match:
            leader = leader_match.group(2).strip()
        
        data.append({
            "Game Title": game_title,
            "Region": region,
            "Stage/Section": heading,
            "Available Wild Pokémon": "; ".join([f"{p['Name']} (Lv.{p['LevelRange']}, {p['Location']})" for p in wild_pokemon]) if wild_pokemon else "",
            "Gym Leader/Champion": leader,
            "Team Composition": "; ".join([f"{t['Pokemon']} (Lv.{t['Level']}: HP {t['HP']}, Atk {t['Attack']}, Def {t['Defense']}, Spd {t['Speed']})" for t in gym_team]) if gym_team else "",
            "Additional Notes/Strategy": notes
        })
    return data

def write_to_csv(data, output_csv):
    fieldnames = [
        "Game Title", "Region", "Stage/Section",
        "Available Wild Pokémon", "Gym Leader/Champion",
        "Team Composition", "Additional Notes/Strategy"
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Update the file paths for your PDFs.
pdf_files = [
    {"path": "(Prima 2005) - Pokemon Emerald.pdf", "game_title": "Pokémon Emerald", "region": "Hoenn"},
    {"path": "(Prima 2010) - Pokemon HeartGold & SoulSilver - Johto.pdf", "game_title": "Pokémon HeartGold & SoulSilver", "region": "Johto"},
    {"path": "Pokémon FireRed Version and LeafGreen Version (Prima Official Game Guide - 2004).pdf", "game_title": "Pokémon FireRed/LeafGreen", "region": "Kanto"}
]

all_data = []
for pdf in pdf_files:
    print(f"Processing {pdf['path']} ...")
    data = process_pdf(pdf["path"], pdf["game_title"], pdf["region"])
    all_data.extend(data)

output_csv = "complete_dataset.csv"
write_to_csv(all_data, output_csv)
print(f"Dataset written to {output_csv}")
