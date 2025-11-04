# Onyx Parts Manager

A professional desktop application for managing electronic components inventory with real-time supplier integration.

## Current Development Status

### Latest Release (November 3, 2025) - v1.0.0
- ✅ Complete PyInstaller distribution with all dependencies
- ✅ NSIS installer with auto-update capability
- ✅ User-specific database storage (AppData)
- ✅ Database path resolution for frozen executables
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Search functionality with Enter key support
- ✅ Delete confirmation dialogs
- ✅ Improved UI styling and column layout
- ✅ Fixed column widths with horizontal scrolling
- ✅ Datasheet management with View/Change/Add PDF buttons

### Features Implemented
- ✅ Component search by Part Number, Type, and Value
- ✅ Add new components with datasheet upload
- ✅ Delete components with confirmation
- ✅ View and manage component datasheets
- ✅ Fixed-width columns with horizontal scroll
- ✅ Multi-user support (each Windows user gets their own database)
- ✅ Professional dark theme UI

### Installation Behavior
When installed, the application:
- Installs program files to `C:\Program Files\OnyxIndustries\PartsManager\`
- Creates user-specific data at `%LOCALAPPDATA%\OnyxIndustries\PartsManager\`
- Each Windows user gets their own database and datasheet storage
- No hardcoded paths - fully portable across different machines

### Next Steps
- Set up GitHub Actions for automated builds
- Add automated tests
- Implement supplier API integration (Digikey, Mouser, LCSC)
- Add CSV/Excel import functionality
- Implement price tracking features

### Quick Start for Development

1. Ensure Python 3.11 or later is installed
2. Create and activate virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Building the Installer

1. Install requirements:
   ```
   pip install pyinstaller
   ```
2. Install NSIS (Nullsoft Scriptable Install System)
3. Build the distribution:
   ```
   python -m PyInstaller "Onyx Parts Manager.spec"
   ```
4. Create the installer:
   ```
   "C:\Program Files (x86)\NSIS\makensis.exe" installer_with_updates.nsi
   ```

## Installation

### Download
Download the latest installer from the [Releases](https://github.com/onyx-23/onyx-parts-manager/releases) page.

**File**: `OnxPartsManager-Setup-1.0.0.exe` (57 MB)

After downloading:
1. Run `OnxPartsManager-Setup-1.0.0.exe`
2. Follow the installation wizard
3. The application will be installed to `C:\Program Files\OnyxIndustries\PartsManager\`
4. Your database and datasheets will be stored in `%LOCALAPPDATA%\OnyxIndustries\PartsManager\`

### System Requirements
- Windows 10 or later (64-bit)
- ~100 MB disk space
- No Python installation required (all dependencies bundled)

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