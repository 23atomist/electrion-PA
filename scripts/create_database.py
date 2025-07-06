import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'election_data.db')

def create_database():
    """Creates the SQLite database and all necessary tables."""
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Drop tables if they exist to ensure a clean slate
        cursor.execute("DROP TABLE IF EXISTS registration")
        cursor.execute("DROP TABLE IF EXISTS results")
        cursor.execute("DROP TABLE IF EXISTS offices")
        cursor.execute("DROP TABLE IF EXISTS parties")
        cursor.execute("DROP TABLE IF EXISTS candidates")
        cursor.execute("DROP TABLE IF EXISTS precincts")
        cursor.execute("DROP TABLE IF EXISTS counties")
        cursor.execute("DROP TABLE IF EXISTS elections")
        cursor.execute("DROP TABLE IF EXISTS states")

        # Create states table
        cursor.execute("""
        CREATE TABLE states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            abbreviation TEXT UNIQUE NOT NULL
        )
        """)

        # Create elections table
        cursor.execute("""
        CREATE TABLE elections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            type TEXT NOT NULL,
            FOREIGN KEY (state_id) REFERENCES states (id),
            UNIQUE (state_id, year, type)
        )
        """)

        # Create counties table
        cursor.execute("""
        CREATE TABLE counties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state_id INTEGER NOT NULL,
            county_code TEXT NOT NULL,
            name TEXT,
            fips_code TEXT,
            FOREIGN KEY (state_id) REFERENCES states (id),
            UNIQUE (state_id, county_code)
        )
        """)

        # Create precincts table
        cursor.execute("""
        CREATE TABLE precincts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            county_id INTEGER NOT NULL,
            precinct_code TEXT NOT NULL,
            municipality_name TEXT,
            registered_voters INTEGER,
            ballots_cast INTEGER,
            us_congressional_district TEXT,
            state_senatorial_district TEXT,
            state_house_district TEXT,
            FOREIGN KEY (county_id) REFERENCES counties (id),
            UNIQUE (county_id, precinct_code)
        )
        """)

        # Create candidates table
        cursor.execute("""
        CREATE TABLE candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_number TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT
        )
        """)

        # Create parties table
        cursor.execute("""
        CREATE TABLE parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_code TEXT UNIQUE NOT NULL,
            name TEXT
        )
        """)

        # Create offices table
        cursor.execute("""
        CREATE TABLE offices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            office_code TEXT UNIQUE NOT NULL,
            name TEXT,
            district INTEGER
        )
        """)

        # Create results table
        cursor.execute("""
        CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER NOT NULL,
            precinct_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            party_id INTEGER NOT NULL,
            office_id INTEGER NOT NULL,
            vote_total INTEGER NOT NULL,
            FOREIGN KEY (election_id) REFERENCES elections (id),
            FOREIGN KEY (precinct_id) REFERENCES precincts (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id),
            FOREIGN KEY (party_id) REFERENCES parties (id),
            FOREIGN KEY (office_id) REFERENCES offices (id)
        )
        """)

        # Create registration table
        cursor.execute("""
        CREATE TABLE registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER NOT NULL,
            precinct_id INTEGER NOT NULL,
            party_id INTEGER NOT NULL,
            registered_voters INTEGER NOT NULL,
            FOREIGN KEY (election_id) REFERENCES elections (id),
            FOREIGN KEY (precinct_id) REFERENCES precincts (id),
            FOREIGN KEY (party_id) REFERENCES parties (id),
            UNIQUE (election_id, precinct_id, party_id)
        )
        """)

        print(f"Database created successfully at {DB_PATH}")

if __name__ == '__main__':
    create_database()