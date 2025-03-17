
import regex
import pathlib

import cg3dmaya.preferences


def get_path(input_string):
    environment_exp = r"(?P<ENV>%(?P<ENV_NAME>\S+)%)?(?P<Path>\S*)"
    prefs = cg3dmaya.preferences.get()
    
    return pathlib.Path(input_string)