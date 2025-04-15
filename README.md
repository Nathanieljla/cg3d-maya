![maya2025](https://img.shields.io/badge/Maya2025-tested-brightgreen.svg)
![maya2024](https://img.shields.io/badge/Maya2024-tested-brightgreen.svg)

# cg3d-maya
The best of my personal maya scripts for public consumption in an easy to use module.

## Version History
1.0.0 
- Users can now add an environment variable to their PC.  Then (from The Guru preferences) add the environment name.  This will replace hard-coded Game exporter paths with the path defined in the variable.
- When an environment variable has been found, then you can optionally search for a change in the file location based on the environment variables path.  This allows you to restructure fbx files from Unity and have the data updated in Maya. Search behaviour is defined in the preferences "Search for new location" option.
- ASCII files can be converted to binary files. Note: This starts a Maya instance behind the scenes, so it does take a moment to do the conversion.

### Current Features
1. Menu to connect to the wing-ide
2. Automatically detect when you're loading a Maya file from another project and ask if you'd like to auto-switch projects and reload.
3. Note for tech artists: My cg3guru package gets installed.  Checkout the udata class for creating attributes with versioning.



# Installation

### Drag & Drop
1. Download [install_cg3d_maya.py](https://github.com/Nathanieljla/cg3d-maya/releases/download/v0.5.2/install_cg3d_maya.py)
2. Drag-n-drop the downloaded file into the Maya viewport.
3. Hit "Install" and wait until it says the installation is complete.

Once the installation has finished you should see a new menu labeled "Guru" on the main menu bar. 

When closing Maya the first time after the installation, you might see a dialog like this:
![image](https://github.com/Nathanieljla/cg3d-maya/assets/1466171/09e48a5e-cbf4-4257-b3c8-3ba963da8865)

You'll want to say "yes" to this dialog.

