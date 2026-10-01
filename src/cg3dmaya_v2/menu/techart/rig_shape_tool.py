PARAMS = {
    'label': 'Rig Shape(s) Tool'
}

DIVIDER = ''

def command(*args, **kwargs):
    import cg3dmaya_v2.uis.rig_shape_editor
    cg3dmaya_v2.uis.rig_shape_editor.run()