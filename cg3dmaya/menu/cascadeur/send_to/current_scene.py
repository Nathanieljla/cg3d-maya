
def command(*args, **kwargs):
    import cg3dmaya.cascadeur
    cg3dmaya.cascadeur.export()
    
    import wingcarrier.pigeons
    casc = wingcarrier.pigeons.CascadeurPigeon()
    cmd = u"import cg3dguru.maya; cg3dguru.maya.import_scene(False)"
    casc.send_python_command(cmd)
