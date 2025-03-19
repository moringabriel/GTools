# GTool Shelf: Your Centralized Nuke Tool Management Hub

## Overview
GTool Shelf is a comprehensive Nuke addon designed to revolutionize how compositors manage and access their tools. It provides a dynamic, customizable PySide panel that functions as a powerful tool shelf, empowering artists to organize and centralize their diverse collection of Nuke tools, scripts, and gizmos. While GTool Shelf includes a set of default productivity tools, its primary purpose is to enable artists to create a personalized tool management system.

## Key Features
- **Centralized Tool Management:** Create categorized shelves for your custom tools, gizmos, and Python scripts, ensuring rapid access and a clean workspace.
- **Customizable Tool Shelf:** Design your own tool shelf layout with intuitive drag-and-drop functionality, tailoring it to your specific workflow.
- **Extensive Library of Default Tools:** Includes a range of Python scripts for common compositing tasks, serving as a foundation for your personalized tool collection.
- **Seamless Nuke Integration:** Integrates directly into Nuke's interface, providing a natural and efficient user experience.
- **Designed to Reduce Repetitive Workflows:** Streamlines tool access, minimizing time spent searching and maximizing creative output.
- **Transitioning to SQLite for Local Data Storage:** GTool Shelf is currently transitioning to SQLite for local data storage. Currently, data is stored in json file and python scripts. This transition is being implemented to address limitations in the current storage method, which can become inefficient and cumbersome with large tool libraries. By leveraging SQLite, GTool Shelf will offer several key benefits:
    - **Improved Data Management:** SQLite's robust database structure will provide more efficient organization and retrieval of tool data.
    - **Enhanced Performance:** SQLite's optimized query capabilities will significantly improve performance, especially when managing a large number of tools.
    - **Increased Reliability:** SQLite's data integrity features will ensure that tool data is stored and accessed reliably, minimizing the risk of data loss or corruption.
    - **Future Scalability:** SQLite's flexible schema and efficient data handling will allow GTool Shelf to scale effectively as tool libraries grow.

## Installation
1. Clone the repository.
2. Add the project directory to your Nuke Python path.
3. Restart Nuke.
4. Configure `menu.py` to load the tools.

## Requirements
- Nuke (version 15.1)
- Python 3.10+
- PySide/PySide2

## Functionality Highlights
- Tool organization and categorization.
- Rapid access to custom scripts and gizmos.
- Default tools for render management, node manipulation, color grading, and file/project organization.

## Design Philosophy
- Empower artists to manage their tools effectively.
- Non-intrusive tool layer that enhances productivity.
- Modular and extensible architecture for future growth.

## Planned Enhancements
- Radial menu implementation for quick tool selection.
- Expanded tool library and customization options.
- Enhanced search functionality for faster tool retrieval.

## License

MIT License

Copyright (c) 2025 Gabriel Morin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.