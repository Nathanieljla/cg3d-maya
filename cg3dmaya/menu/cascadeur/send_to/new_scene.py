
def command(*args, **kwargs):
    import cg3dmaya.cascadeur
    cg3dmaya.cascadeur.export_scene(True)
    
    #import wingcarrier.pigeons
    #casc = wingcarrier.pigeons.CascadeurPigeon()
    #cmd = u"import cg3dguru.maya; cg3dguru.maya.import_scene(True)"
    #casc.send_python_command(cmd)
