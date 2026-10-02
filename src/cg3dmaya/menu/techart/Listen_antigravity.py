DIVIDER = ''

def command(*args, **kwargs):
    import debugpy
    try:
        debugpy.listen(5678)
        print("Debug connection is open and listening on port 5678.")
    except Exception as e:
        print(f"Debugger error or already listening: {e}")
