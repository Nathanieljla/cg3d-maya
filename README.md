# cg3d-maya

Maya workflow tools, including Game Exporter helpers, automatic project
switching, preferences, and rig-shape utilities.

The `cg3dmaya` package uses `maya.cmds` and `maya.api.OpenMaya` and has no
PyMEL dependency.

```python
from cg3dmaya.core import ExportType, GameExporter, ShapeCloner
```

The package requires `cg3d-maya-core>=0.9.0`, whose public import package is
`cg3dguru`.

## Compatibility

The package is exercised in Maya 2023 and Maya 2026. Its full module tree is
also import-checked with syntax warnings treated as errors in Maya 2027.

## Installation

For development, install the repository into Maya's Python environment or add
its `src` directory to `PYTHONPATH`. The drag-and-drop installer is located at
`src/cg3dmaya/install_cg3d_maya.py`.

After installation, Maya creates the Guru menu on startup.

## Version history

### 2.0.0

- Replaced the original PyMEL implementation with the native Maya API rewrite.
- Reimplemented Game Exporter, shape-cloning, path, preference, and callback
  code with Maya's native APIs.

### 1.0.0

- Added environment-variable Game Exporter paths and relocation support.
- Added optional ASCII-to-binary FBX conversion.
