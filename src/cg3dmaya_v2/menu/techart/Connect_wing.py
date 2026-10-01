
PARAMS = {
    'label': 'Connect To Wing'
}



def command(*args, **kwargs):
    from maya import cmds
    try:
        import wingcarrier.wingdbstub
        wingcarrier.wingdbstub.Ensure()
    except:
        cmds.error('Connection to wing failed.')
