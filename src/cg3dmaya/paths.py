
import re
import pathlib
import os
import pymel.core as pm


import cg3dmaya.preferences


_environment_exp = r"(?P<ENV>%(?P<ENV_NAME>\S+)%)?(?P<Path>\S*)"
expression = re.compile(_environment_exp)

def env_path_to_path(input_string):
    """Returns the a tupple containing the updated file path and the used env
    
    If the second elmeent is None, then it means the path didn't change.
    """
    global expression
    
    result = expression.match(input_string)
    patterns = result.groupdict()
    env_name = patterns.get('ENV_NAME', None)
    if not env_name:
        return (input_string, None)

    environment_variables = os.environ
    if env_name not in environment_variables:
        pm.warning(f"Environment variable {env_name} not found on PC!")
        return (input_string, None)

    env_path = environment_variables[env_name].replace("\\", "/")
    path = input_string.replace(patterns['ENV'], env_path)

    print(f"path in:{input_string} path out:{path}")
    return (path, env_path)



def path_to_env_path(input_string):
    environment_variables = os.environ
    prefs = cg3dmaya.preferences.get()
    found_paths = dict()
    for ev_name in prefs.environment_variables:
        if ev_name in environment_variables:
            path = environment_variables[ev_name].replace("\\", "/")
            found_paths[ev_name] = path
            
    out_path = input_string
    for ev_name, ev_path in found_paths.items():
        if input_string.find(ev_path) != -1:
            out_path = input_string.replace(ev_path, f"%{ev_name}%")

    print(f"path in:{input_string} path out:{out_path}")
    return out_path

    