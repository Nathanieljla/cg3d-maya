
def command(*args, **kwargs):
    try:
        import wingcarrier.wingdbstub
        wingcarrier.wingdbstub.Ensure()
    except:
        scene.error('Connection to wing failed.') 