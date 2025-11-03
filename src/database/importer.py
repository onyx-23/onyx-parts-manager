import os
import pandas as pd
from pathlib import Path
from database.db import Database

class MasterPartsImporter:
    def __init__(self, master_parts_path):
        self.master_parts_path = Path(master_parts_path)
        self.db = Database()
        
    def import_parts(self):
        """
        Import parts from the master parts file into the database.
        Expects an Excel file with specific columns.
        """
        try:
            # Read the master parts file (adjust format as needed)
            df = pd.read_excel(self.master_parts_path)
            
            # Map columns from master file to database schema
            for _, row in df.iterrows():
                try:
                    # Adjust these column names to match your master file
                    self.db.add_component(
                        company_part_number=row['Company P/N'],
                        type_name=row['Type'],
                        value=row['Value'],
                        description=row['Description'],
                        manufacturer=row['Manufacturer'],
                        mpn=row['Manufacturer P/N'],
                        datasheet_path=row.get('Datasheet Path', ''),
                        stock=row.get('Stock', 0),
                        minimum_stock=row.get('Minimum Stock', 0)
                    )
                except Exception as e:
                    print(f"Error importing row: {row['Company P/N']} - {str(e)}")
                    
        except Exception as e:
            print(f"Error reading master parts file: {str(e)}")
            raise