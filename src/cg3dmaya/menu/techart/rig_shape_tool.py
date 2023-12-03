PARAMS = {
    'label': 'Rig Shape(s) Tool'
}


def command(*args, **kwargs):
    import cg3dmaya.uis.rig_shape_editor
    cg3dmaya.uis.rig_shape_editor.run()