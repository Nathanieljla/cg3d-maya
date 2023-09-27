
PARAMS = {
    'label': 'Update Model(s)'
}


def command(*args, **kwargs):
    import cg3dmaya.cascadeur
    cg3dmaya.cascadeur.update_models()
    
    #import wingcarrier.pigeons
    #casc = wingcarrier.pigeons.CascadeurPigeon()
    #cmd = u"import cg3dguru.maya; cg3dguru.maya.update_models()"
    #casc.send_python_command(cmd)