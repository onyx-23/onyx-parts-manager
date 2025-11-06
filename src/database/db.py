import sqlite3
import os
import sys
import logging
from pathlib import Path
from src.security import validate_part_number, sanitize_string

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        # Get the application's data directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use AppData for writable storage
            appdata = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
            application_path = appdata / 'OnyxIndustries' / 'PartsManager'
        else:
            # Running as script - use project directory
            application_path = Path(__file__).parent.parent.parent
        
        self.db_path = application_path / 'data' / 'parts.db'
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.init_database()
        logger.info(f"Database initialized at: {self.db_path}")

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
        """
        Add a new component to the database with input validation.
        
        Security:
            - Input sanitization to prevent SQL injection
            - Parameterized queries
            - Length validation
        """
        # SECURITY: Validate and sanitize inputs
        if not validate_part_number(company_part_number):
            logger.error(f"Invalid company part number: {company_part_number}")
            raise ValueError("Invalid company part number format")
        
        # SECURITY: Sanitize all string inputs
        company_part_number = sanitize_string(company_part_number, max_length=100)
        type_name = sanitize_string(type_name, max_length=50)
        value = sanitize_string(value, max_length=100)
        package_type = sanitize_string(package_type, max_length=50)
        footprint_size = sanitize_string(footprint_size, max_length=50)
        voltage_rating = sanitize_string(voltage_rating, max_length=50)
        description = sanitize_string(description, max_length=500)
        manufacturer = sanitize_string(manufacturer, max_length=100)
        mpn = sanitize_string(mpn, max_length=100)
        datasheet_path = sanitize_string(datasheet_path, max_length=500) if datasheet_path else None
        
        # SECURITY: Validate numeric inputs
        try:
            stock = int(stock) if stock is not None else 0
            minimum_stock = int(minimum_stock) if minimum_stock is not None else 0
        except (ValueError, TypeError):
            logger.error("Invalid stock values")
            raise ValueError("Stock values must be integers")
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            # SECURITY: Using parameterized query to prevent SQL injection
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

    def search_components(self, pn_filter=None, type_filter=None, value_filter=None):
        """
        Search components based on filters with input validation.
        
        Security:
            - Input sanitization
            - Parameterized queries
            - No string concatenation in SQL
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Base query to get all components
            query = "SELECT * FROM components"
            params = []
            
            # Only add WHERE clause if we have actual filters
            conditions = []
            
            # SECURITY: Sanitize inputs before using in query
            if pn_filter and pn_filter.strip():
                pn_filter = sanitize_string(pn_filter.strip(), max_length=100)
                # Validate part number pattern
                if validate_part_number(pn_filter):
                    conditions.append("company_part_number LIKE ?")
                    params.append(f"%{pn_filter}%")
                else:
                    logger.warning(f"Invalid part number filter rejected: {pn_filter}")
            
            if type_filter and type_filter != "All":
                type_filter = sanitize_string(type_filter, max_length=50)
                conditions.append("type = ?")
                params.append(type_filter)
                
            if value_filter and value_filter.strip():
                value_filter = sanitize_string(value_filter.strip(), max_length=100)
                conditions.append("value LIKE ?")
                params.append(f"%{value_filter}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            # Add ordering to ensure consistent display
            query += " ORDER BY company_part_number"
            
            # SECURITY: Using parameterized query
            cursor.execute(query, params)
            return cursor.fetchall()

    def update_supplier_info(self, component_id, supplier, part_number, price, stock):
        """
        Update or insert supplier information for a component.
        
        Security:
            - Input validation
            - Parameterized queries
        """
        # SECURITY: Validate inputs
        try:
            component_id = int(component_id)
        except (ValueError, TypeError):
            logger.error("Invalid component ID")
            raise ValueError("Component ID must be an integer")
        
        supplier = sanitize_string(supplier, max_length=50)
        part_number = sanitize_string(part_number, max_length=100)
        
        try:
            price = float(price) if price is not None else None
            stock = int(stock) if stock is not None else None
        except (ValueError, TypeError):
            logger.error("Invalid price or stock values")
            raise ValueError("Price must be a number and stock must be an integer")
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            # SECURITY: Using parameterized query
            cursor.execute('''
                INSERT OR REPLACE INTO supplier_parts (
                    component_id, supplier, supplier_part_number,
                    price, stock, last_updated
                ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (component_id, supplier, part_number, price, stock))
            conn.commit()