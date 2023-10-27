
PARAMS = {
    'label': 'Connect To Wing'
}



def command(*args, **kwargs):
    import pymel.core as pm
    try:
        import wingcarrier.wingdbstub
        wingcarrier.wingdbstub.Ensure()
    except:
        pm.error('Connection to wing failed.')