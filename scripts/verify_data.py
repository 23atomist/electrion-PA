import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'election_data.db')

def verify_data():
    """Connects to the database and runs queries to verify data integrity."""
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    with sqlite3.connect(DB_PATH) as conn:
        print("--- Verification Report ---")
        
        # 1. Count total results and registrations
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM results")
        result_count = cursor.fetchone()[0]
        print(f"\n1a. Total records in 'results' table: {result_count}")
        
        cursor.execute("SELECT COUNT(*) FROM registration")
        reg_count = cursor.fetchone()[0]
        print(f"1b. Total records in 'registration' table: {reg_count}")

        # 2. Show a sample of the joined data including registration
        print("\n2. Sample of joined data (Results + Registration):")
        
        query = """
        SELECT
            e.year,
            s.name as state,
            co.name as county_name,
            p.municipality_name,
            ca.first_name,
            ca.last_name,
            pa.party_code,
            r.vote_total,
            reg.registered_voters
        FROM results r
        JOIN elections e ON r.election_id = e.id
        JOIN states s ON e.state_id = s.id
        JOIN precincts p ON r.precinct_id = p.id
        JOIN counties co ON p.county_id = co.id
        JOIN candidates ca ON r.candidate_id = ca.id
        JOIN parties pa ON r.party_id = pa.id
        LEFT JOIN registration reg ON r.precinct_id = reg.precinct_id 
                                  AND r.election_id = reg.election_id 
                                  AND r.party_id = reg.party_id
        LIMIT 10;
        """
        
        try:
            df = pd.read_sql_query(query, conn)
            if not df.empty:
                print(df.to_string())
            else:
                print("No data found in the joined query.")
        except Exception as e:
            print(f"An error occurred while fetching data with pandas: {e}")
            print("This might be because pandas is not installed. Try 'pip install pandas'.")

        print("\n--- Verification Complete ---")

if __name__ == '__main__':
    verify_data()