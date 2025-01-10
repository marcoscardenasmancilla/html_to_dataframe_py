# ==================================================================================================================================================================

# Author                    : Dr. Marcos H. Cárdenas Mancilla
# E-mail                    : marcos.cardenas.m@usach.cl
# Date of creation          : 2024-11-15
# Licence                   : AGPL V3
# Copyright (c) 2024 Marcos H. Cárdenas Mancilla.

# ==================================================================================================================================================================

# Descripción de HTML_to_DataFrame_PY:
# Este código Python extrae y organiza datos lingüísticos preprocesados por IA y posteriormente anotados por humanos en un corpus paralelo de canciones en japonés 
# (origen) y su traducción al inglés (meta).
# Los códigos de color asignados a cada fila corresponden a los procesos verbales en japonés que fueron identificados y clasificados por la IA y después anotados en
# la revisión manual. El Identificador Único corresponde a un código alfanumérico p.ej., [a] asignado automáticamente a cada una de las instancias por orden de 
# aparición en el corpus. Significado de códigos de color: 'amarillo' = Instancia clasificada exitosamente por IA, verificada por humano;
# 'rojo' =  Instancia no clasificada por IA. Requiere extracción y verificación manual.

# Características:
# 1. parsea el HTML usando BeautifulSoup para identificar y extraer procesos verbales.
# 2. asocia los datos a un identificador único y un código de color (amarillo o rojo). 
# 3. organiza estos datos en un DataFrame de pandas, añadiendo información adicional como la traducción al inglés de cada proceso verbal obtenida también del HTML. 
# 4. exporta este DataFrame a un archivo Excel, creando un conjunto de datos limpio y estructurado listo para su análisis,
# donde cada fila representa un proceso verbal con su canción de origen, significado y color.

# ==================================================================================================================================================================

# Load libraries
# Import necessary libraries
import pandas as pd
from bs4 import BeautifulSoup

# Load the HTML content from the file
with open(r'AnalisisCancionesJapones.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Extract all identifiers from the HTML file in the order they appear
identifiers_in_order = []
for tag in soup.find_all('a', id=lambda x: x and x.startswith("cmnt")):
    identifier = tag.get_text(strip=True)
    identifiers_in_order.append(identifier)

# Debugging: Check how many identifiers we have extracted and the first few values
print(f"Total identifiers extracted: {len(identifiers_in_order)}")  # Should print 304
print(f"First 10 identifiers extracted: {identifiers_in_order[:10]}")  # Display the first 10 identifiers

# Define the identifiers for each song based on the exact ranges you provided
song_identifiers = {
    "Canción 1": identifiers_in_order[:32],
    "Canción 2": identifiers_in_order[33:65],
    "Canción 3": identifiers_in_order[66:97],
    "Canción 4": identifiers_in_order[98:121],
    "Canción 5": identifiers_in_order[122:159],
    "Canción 6": identifiers_in_order[160:181],
    "Canción 7": identifiers_in_order[182:196],
    "Canción 8": identifiers_in_order[197:236],
    "Canción 9": identifiers_in_order[237:277],
    "Canción 10": identifiers_in_order[278:]
}

# Double-check the total identifiers across all songs
total_identifiers = sum([len(ids) for ids in song_identifiers.values()])
print(f"Total identifiers across all songs: {total_identifiers}")  # Should print 304

# Extract verb processes based on the identifiers for each song
highlighted_segments_full = []
used_identifiers = set()

# Loop through each song and its identifiers to extract verb processes
for song, identifiers in song_identifiers.items():
    for identifier in identifiers:
        if identifier in used_identifiers:
            continue
        # Find the <a> tag with the specific identifier
        verb_process_tag = soup.find('a', string=identifier)
        if verb_process_tag:
            # Get the parent span tag which contains the verb process
            parent_span = verb_process_tag.find_previous('span')
            if parent_span:
                text = parent_span.get_text(strip=True)
                color_class = parent_span.get('class', [])
                if 'c1' in color_class:
                    color = 'Amarillo'
                elif 'c7' in color_class:
                    color = 'Rojo'
                else:
                    color = 'Unknown'
                highlighted_segments_full.append((text, identifier, color, song))
                used_identifiers.add(identifier)

# Verify if the number of rows in the final DataFrame matches the expected 304
print(f"Rows in final DataFrame: {len(highlighted_segments_full)}")  # Should be 304

# Create a DataFrame with the full list of verb processes for all songs
columns = ['Proceso Verbal', 'Identificador', 'Color', 'Canción']
df_highlighted_segments_full = pd.DataFrame(highlighted_segments_full, columns=columns)

# Add a column with the color definitions
verified_color_mapping = {
    "Amarillo": "#ffff00",
    "Rojo": "#ff0000"
}
df_highlighted_segments_full['Color Definition'] = df_highlighted_segments_full['Color'].map(verified_color_mapping)

# Extract meanings using the specified code structure from the HTML
meanings_extracted_corrected = []
for tag in soup.find_all('a', id=lambda x: x and x.startswith("cmnt")):
    identifier = tag.get_text(strip=True)
    # Find the next span or sibling element that contains the meaning
    meaning_tag = tag.find_next_sibling('span', class_='c0')
    if meaning_tag:
        meaning_text = meaning_tag.get_text(strip=True)
        meanings_extracted_corrected.append((identifier, meaning_text))

# Create a DataFrame with the extracted meanings based on the corrected structure
df_meanings_extracted_corrected = pd.DataFrame(meanings_extracted_corrected, columns=['Identifier', 'Meaning in English'])

# Convert the extracted meanings DataFrame to a dictionary for easier mapping
meanings_dict_corrected = df_meanings_extracted_corrected.set_index('Identifier')['Meaning in English'].to_dict()

# Update the 'Meaning in English' column in the original DataFrame
df_highlighted_segments_full['Meaning in English'] = df_highlighted_segments_full['Identificador'].map(meanings_dict_corrected)

# Reorder columns
ordered_columns = ['Identificador', 'Canción', 'Proceso Verbal', 'Meaning in English', 'Color', 'Color Definition']
df_highlighted_segments_full = df_highlighted_segments_full[ordered_columns]

# Export the final DataFrame to Excel
df_final = df_highlighted_segments_full
final_columns = ['Identificador', 'Canción', 'Proceso Verbal', 'Meaning in English', 'Color']
df_final = df_final[final_columns]
df_final.rename(columns={'Canción': 'Song'}, inplace=True)

# Export to Excel file
df_final.to_excel('Final_Compiled_Verb_Processes_Canciones_1_to_10.xlsx', index=False)

# Display the final DataFrame
print("Final Compiled Verb Processes for Canciones 1 to 10")
print(df_final.to_string(index=False))
