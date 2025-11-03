# Onyx Parts Manager

A professional desktop application for managing electronic components inventory with real-time supplier integration.

## Features

- Search and filter electronic components by type, value, and other parameters
- View and manage component datasheets
- Track local inventory levels
- Real-time price and stock checking from suppliers (Digikey, Mouser, LCSC)
- SQLite database for local storage

## Setup

1. Ensure Python 3.11 or later is installed
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Configure supplier API keys:
   - Copy `template.env` to `.env`
   - Sign up for API access at:
     - Digikey: https://developer.digikey.com/
     - Mouser: https://www.mouser.com/api-hub/
     - LCSC: https://lcsc.com/api
   - Update `.env` with your API keys

## Running the Application

### From Source
```
python src/main.py
```

### Using the Executable
1. Download the latest release from the releases page
2. Extract the zip file to your desired location
3. Copy `template.env` to `.env` and configure your API keys
4. Run `Onyx Parts Manager.exe`

## Building the Executable

To create the executable yourself:

1. Ensure all dependencies are installed:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. Run PyInstaller:
   ```
   pyinstaller onyx_parts_manager.spec
   ```
3. The executable will be created in the `dist` folder

## Project Structure

- `src/` - Source code
  - `gui/` - GUI components
  - `database/` - Database management
  - `suppliers/` - Supplier API integration
- `data/` - Data storage
  - `datasheets/` - PDF datasheets storage
  
## Managing Components

### Importing from Master Parts File
The application can import components from your existing Master Parts File:
1. Ensure your Master Parts File is in Excel format
2. Use the File > Import menu to select your Master Parts File
3. The importer will map columns and import your components

### Adding New Components
1. Use the application to add new components to your inventory
2. Store datasheets in the `data/datasheets` directory
3. Component information is stored in a SQLite database at `data/parts.db`

### Company Part Numbers
- Each component is assigned a unique Onyx Industries part number
- Parts can be searched by company part number or manufacturer part number
- The company part number is displayed prominently in the interface

## Supplier Integration

The application integrates with major electronic component suppliers to fetch real-time pricing and stock information. To use this feature:

1. Sign up for API access with the suppliers you want to use
2. Add your API keys to the `.env` file
3. The application will automatically fetch prices when viewing components

Note: Each supplier has their own API limits and terms of use. Please review their documentation for details.