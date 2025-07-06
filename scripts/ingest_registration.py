import sqlite3
import csv
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'election_data.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# County mapping from the data layout file
COUNTY_MAP = {
    "01": "Adams", "02": "Allegheny", "03": "Armstrong", "04": "Beaver", "05": "Bedford",
    "06": "Berks", "07": "Blair", "08": "Bradford", "09": "Bucks", "10": "Butler",
    "11": "Cambria", "12": "Cameron", "13": "Carbon", "14": "Centre", "15": "Chester",
    "16": "Clarion", "17": "Clearfield", "18": "Clinton", "19": "Columbia", "20": "Crawford",
    "21": "Cumberland", "22": "Dauphin", "23": "Delaware", "24": "Elk", "25": "Erie",
    "26": "Fayette", "27": "Forest", "28": "Franklin", "29": "Fulton", "30": "Greene",
    "31": "Huntingdon", "32": "Indiana", "33": "Jefferson", "34": "Juniata", "35": "Lackawanna",
    "36": "Lancaster", "37": "Lawrence", "38": "Lebanon", "39": "Lehigh", "40": "Luzerne",
    "41": "Lycoming", "42": "McKean", "43": "Mercer", "44": "Mifflin", "45": "Monroe",
    "46": "Montgomery", "47": "Montour", "48": "Northampton", "49": "Northumberland", "50": "Perry",
    "51": "Philadelphia", "52": "Pike", "53": "Potter", "54": "Schuylkill", "55": "Snyder",
    "56": "Somerset", "57": "Sullivan", "58": "Susquehanna", "59": "Tioga", "60": "Union",
    "61": "Venango", "62": "Warren", "63": "Washington", "64": "Wayne", "65": "Westmoreland",
    "66": "Wyoming", "67": "York"
}

def get_or_create(cursor, table_name, unique_data, other_data=None):
    """Gets the ID of a row in a table if it exists, otherwise creates it."""
    unique_values = tuple(unique_data.values())
    where_clause = ' AND '.join(f'{k} = ?' for k in unique_data.keys())
    cursor.execute(f"SELECT id FROM {table_name} WHERE {where_clause}", unique_values)
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        all_data = unique_data.copy()
        if other_data:
            all_data.update(other_data)
        columns = ', '.join(all_data.keys())
        placeholders = ', '.join('?' for _ in all_data)
        values = tuple(all_data.values())
        cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
        return cursor.lastrowid

def process_registration_file(cursor, file_path, year):
    """Processes a single registration file, either txt or xlsx."""
    print(f"Processing registration file: {file_path}...")
    state_id = get_or_create(cursor, 'states', {'abbreviation': 'PA'}, {'name': 'Pennsylvania'})
    
    fieldnames = [
        'election_year', 'election_type', 'county_code', 'precinct_code',
        'party_1_rank', 'party_1_abbr', 'party_1_voters', 'party_2_rank', 'party_2_abbr', 'party_2_voters',
        'party_3_rank', 'party_3_abbr', 'party_3_voters', 'party_4_rank', 'party_4_abbr', 'party_4_voters',
        'party_5_rank', 'party_5_abbr', 'party_5_voters', 'party_6_rank', 'party_6_abbr', 'party_6_voters',
        'us_congressional_district', 'state_senatorial_district', 'state_house_district',
        'municipality_type_code', 'municipality_name', 'municipality_breakdown_code_1',
        'municipality_breakdown_name_1', 'municipality_breakdown_code_2', 'municipality_breakdown_name_2',
        'bi_county_code', 'm_c_d_code', 'f_i_p_s_code', 'v_t_d_code',
        'previous_precinct_code', 'previous_us_congressional_district',
        'previous_state_senatorial_district', 'previous_state_house_district'
    ]

    rows = []
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f, fieldnames=fieldnames))
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, header=None)
        # Trim the dataframe to the expected number of columns before assigning names
        df = df.iloc[:, :len(fieldnames)]
        df.columns = fieldnames
        rows = df.to_dict('records')

    count = 0
    for row in rows:
        try:
            # Standardize data types
            row = {k: str(v).strip() if v is not None else '' for k, v in row.items()}

            county_code_str = row['county_code'].zfill(2)
            county_name = COUNTY_MAP.get(county_code_str, f"Unknown County {county_code_str}")

            election_id = get_or_create(cursor, 'elections', 
                                        {'state_id': state_id, 'year': int(year), 'type': 'G'})

            county_id = get_or_create(cursor, 'counties', 
                                      {'state_id': state_id, 'county_code': county_code_str},
                                      {'name': county_name, 'fips_code': row.get('f_i_p_s_code', '')})

            precinct_id = get_or_create(cursor, 'precincts',
                                        {'county_id': county_id, 'precinct_code': row['precinct_code']},
                                        {'municipality_name': row.get('municipality_name', ''),
                                         'us_congressional_district': row.get('us_congressional_district', ''),
                                         'state_senatorial_district': row.get('state_senatorial_district', ''),
                                         'state_house_district': row.get('state_house_district', '')})

            for i in range(1, 7):
                party_abbr = row.get(f'party_{i}_abbr', '')
                voters_str = row.get(f'party_{i}_voters', '0')
                # Handle potential NaN values from pandas, which can be objects or the string 'nan'
                if voters_str == 'nan' or pd.isna(voters_str):
                    voters_str = '0'
                if party_abbr and voters_str and int(float(voters_str)) > 0:
                    party_id = get_or_create(cursor, 'parties', {'party_code': party_abbr})
                    cursor.execute("""
                    INSERT OR IGNORE INTO registration (election_id, precinct_id, party_id, registered_voters)
                    VALUES (?, ?, ?, ?)
                    """, (election_id, precinct_id, party_id, int(float(voters_str))))
            
            count += 1
        except Exception as e:
            print(f"Error processing row in {year}: {row}")
            print(f"Error: {e}")
    
    print(f"Successfully processed {count} records for {year}.")

def ingest_all_registration_data():
    """Iterates through all years and ingests registration data."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        years = [2000, 2004, 2008, 2012, 2016, 2020, 2024]
        
        for year in years:
            # Handle different file extensions and naming conventions
            txt_path = os.path.join(DATA_DIR, f'VoterRegistration_{year}_General_Precinct.txt')
            xlsx_path = os.path.join(DATA_DIR, f'VoterRegistration_{year}_General_Precinct.xlsx')
            # Handle lowercase 'p' in 2004 filename
            txt_path_lower = os.path.join(DATA_DIR, f'VoterRegistration_{year}_General_precinct.txt')

            if os.path.exists(txt_path):
                process_registration_file(cursor, txt_path, year)
            elif os.path.exists(txt_path_lower):
                process_registration_file(cursor, txt_path_lower, year)
            elif os.path.exists(xlsx_path):
                process_registration_file(cursor, xlsx_path, year)
            else:
                print(f"No registration file found for {year}")
        
        conn.commit()

if __name__ == '__main__':
    ingest_all_registration_data()