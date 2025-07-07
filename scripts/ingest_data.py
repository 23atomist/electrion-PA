import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'election_data.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

from ingest_registration import get_or_create, COUNTY_MAP

# Mapping for office codes to full names
OFFICE_CODE_MAP = {
    'PRES': 'PRESIDENT OF THE UNITED STATES',
    'USSN': 'UNITED STATES SENATOR',
    'GOV': 'GOVERNOR',
    'LTGOV': 'LIEUTENANT GOVERNOR',
    'ATTYG': 'ATTORNEY GENERAL',
    'AUDG': 'AUDITOR GENERAL',
    'TREAS': 'STATE TREASURER',
    'REPR': 'REPRESENTATIVE IN CONGRESS',
    'STSEN': 'STATE SENATOR',
    'STH': 'REPRESENTATIVE IN THE GENERAL ASSEMBLY',
    'JUDGE': 'JUDGE OF THE SUPERIOR COURT',
    'SUPCT': 'JUSTICE OF THE SUPREME COURT',
    'COMCT': 'JUDGE OF THE COMMONWEALTH COURT',
    'SUPSCT': 'JUDGE OF THE SUPERIOR COURT',
    'MUNCT': 'JUDGE OF THE MUNICIPAL COURT',
    'MAGDIS': 'MAGISTERIAL DISTRICT JUDGE',
    'RET': 'RETENTION ELECTION',
    'USP': 'PRESIDENT OF THE UNITED STATES', # Added based on debug output
    'USS': 'UNITED STATES SENATOR', # Added based on debug output
    'ATT': 'ATTORNEY GENERAL', # Added based on debug output
    'AUD': 'AUDITOR GENERAL', # Added based on debug output
    'TRE': 'STATE TREASURER', # Added based on debug output
    'USC': 'REPRESENTATIVE IN CONGRESS', # Added based on debug output
    'STS': 'STATE SENATOR', # Added based on debug output
    # Add more as needed based on data
}

def process_election_file(cursor, file_path, year):
    """Processes a single election results file."""
    print(f"Processing election file: {file_path}...")
    state_id = get_or_create(cursor, 'states', {'abbreviation': 'PA'}, {'name': 'Pennsylvania'})

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                if not row.get('candidate_number', '').strip():
                    continue

                election_id = get_or_create(cursor, 'elections',
                                            {'state_id': state_id, 'year': int(year), 'type': 'G'})

                county_code_str = row['county_code'].zfill(2)
                county_name = COUNTY_MAP.get(county_code_str, f"Unknown County {county_code_str}")
                county_id = get_or_create(cursor, 'counties',
                                          {'state_id': state_id, 'county_code': county_code_str},
                                          {'name': county_name})

                precinct_id = get_or_create(cursor, 'precincts',
                                            {'county_id': county_id, 'precinct_code': row['precinct_code'].strip()})

                candidate_id = get_or_create(cursor, 'candidates',
                                             {'candidate_number': row['candidate_number'].strip()},
                                             {'first_name': row['candidate_first_name'].strip(), 'last_name': row['candidate_last_name'].strip()})

                party_id = get_or_create(cursor, 'parties', {'party_code': row['candidate_party_code'].strip()})

                office_code = row['candidate_office_code'].strip()
                office_name = OFFICE_CODE_MAP.get(office_code, office_code) # Use mapping, fallback to code
                
                office_id = get_or_create(cursor, 'offices',
                                           {'office_code': office_code},
                                           {'name': office_name, 'district': int(row['candidate_district']) if row['candidate_district'].isdigit() else None})

                cursor.execute("""
                INSERT OR IGNORE INTO results (election_id, precinct_id, candidate_id, party_id, office_id, vote_total)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (election_id, precinct_id, candidate_id, party_id, office_id, int(row['vote_total'])))
                
                count += 1
            except Exception as e:
                print(f"Error processing row in {year}: {row}")
                print(f"Error: {e}")
        
        print(f"Successfully ingested {count} election result records for {year}.")

def ingest_all_election_data():
    """Iterates through all years and ingests election data."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        years = [2000, 2004, 2008, 2012, 2016, 2020, 2024]

        for year in years:
            # Handle typo in 2000 filename
            filename = f'ElectionReturns_{year}_General_PrecinctReturns.txt'
            if year == 2000:
                filename = 'ElectionReturns_2000_General_PrecinctRetuns.txt'
            
            file_path = os.path.join(DATA_DIR, filename)

            if os.path.exists(file_path):
                process_election_file(cursor, file_path, year)
            else:
                print(f"No election results file found for {year}")
        
        conn.commit()

if __name__ == '__main__':
    ingest_all_election_data()