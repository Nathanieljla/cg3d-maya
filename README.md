# cg3d-maya

Maya workflow tools, including Game Exporter helpers, automatic project
switching, preferences, and rig-shape utilities.

## Packages

- `cg3dmaya_v2` is the current rewrite. It uses `maya.cmds` and
  `maya.api.OpenMaya` and has no PyMEL dependency.
- `cg3dmaya` is the unchanged legacy implementation. Install the optional
  `legacy` dependency only when code still imports that package.

```shell
pip install .
pip install ".[legacy]"  # Only for the original cg3dmaya package.
```

New code should import the v2 package explicitly while both implementations
are present:

```python
from cg3dmaya_v2.core import ExportType, GameExporter, ShapeCloner
```

The v2 package requires `cg3d-maya-core>=0.9.0`, whose public import package
is `cg3dguru`.

## Compatibility

The rewrite is exercised in Maya 2023 and Maya 2026. Its full module tree is
also import-checked with syntax warnings treated as errors in Maya 2027.

## Installation

For development, install the repository into Maya's Python environment or add
its `src` directory to `PYTHONPATH`. The drag-and-drop installer remains at
`src/cg3dmaya_v2/install_cg3d_maya.py`.

After installation, Maya creates the Guru menu on startup.

## Version history

### 1.1.0

- Added the `cg3dmaya_v2` package without a PyMEL runtime dependency.
- Reimplemented Game Exporter, shape-cloning, path, preference, and callback
  code with Maya's native APIs.
- Kept `cg3dmaya` unchanged for migration compatibility.

### 1.0.0

- Added environment-variable Game Exporter paths and relocation support.
- Added optional ASCII-to-binary FBX conversion.
