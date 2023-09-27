
PARAMS = {
    'label': 'Update Animation(s)'
}


def command(*args, **kwargs):
    import cg3dmaya.cascadeur
    cg3dmaya.cascadeur.update_animations()
    
    #import wingcarrier.pigeons
    #casc = wingcarrier.pigeons.CascadeurPigeon()
    #cmd = u"import cg3dguru.maya; cg3dguru.maya.update_animations()"
    #casc.send_python_command(cmd)