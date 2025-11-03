import sqlite3
import os
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / 'data' / 'parts.db'
        self.init_database()

    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(str(self.db_path))

    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Create components table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS components (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_part_number TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    value TEXT,
                    package_type TEXT,
                    footprint_size TEXT,
                    voltage_rating TEXT,
                    description TEXT,
                    manufacturer TEXT,
                    manufacturer_part_number TEXT,
                    datasheet_path TEXT,
                    stock INTEGER DEFAULT 0,
                    minimum_stock INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create supplier_parts table for price tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS supplier_parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_id INTEGER,
                    supplier TEXT NOT NULL,
                    supplier_part_number TEXT,
                    price REAL,
                    stock INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (component_id) REFERENCES components (id)
                )
            ''')
            
            conn.commit()

    def add_component(self, company_part_number, type_name, value, package_type,
                     footprint_size, voltage_rating, description, manufacturer,
                     mpn, datasheet_path, stock=0, minimum_stock=0):
        """Add a new component to the database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO components (
                    company_part_number, type, value, package_type, footprint_size,
                    voltage_rating, description, manufacturer, manufacturer_part_number,
                    datasheet_path, stock, minimum_stock
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_part_number, type_name, value, package_type, footprint_size,
                 voltage_rating, description, manufacturer, mpn, datasheet_path,
                 stock, minimum_stock))
            return cursor.lastrowid

    def search_components(self, type_filter=None, value_filter=None):
        """Search components based on filters."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Base query to get all components
            query = "SELECT * FROM components"
            params = []
            
            # Only add WHERE clause if we have actual filters
            conditions = []
            
            if type_filter and type_filter != "All":
                conditions.append("type = ?")
                params.append(type_filter)
                
            if value_filter and value_filter.strip():
                conditions.append("(value LIKE ? OR company_part_number LIKE ?)")
                params.extend([f"%{value_filter}%", f"%{value_filter}%"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            # Add ordering to ensure consistent display
            query += " ORDER BY company_part_number"
            
            cursor.execute(query, params)
            return cursor.fetchall()

    def update_supplier_info(self, component_id, supplier, part_number, price, stock):
        """Update or insert supplier information for a component."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO supplier_parts (
                    component_id, supplier, supplier_part_number,
                    price, stock, last_updated
                ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (component_id, supplier, part_number, price, stock))
            conn.commit()