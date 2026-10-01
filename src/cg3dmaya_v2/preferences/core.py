from maya import cmds
import enum
import pathlib
import pickle

_PREFS_INSTANCE = None


class OptionEnum(enum.IntEnum):
    NEVER = 0
    ALWAYS = 1
    ASK = 2


class _PreferenceData(object):
    def __init__(self):
        #-Callbacks
        self.callback_switch_project = OptionEnum.NEVER
        self.callback_fbx_namespaces = OptionEnum.NEVER

        #--Game export + options
        self.remove_subdeformer_namespaces = OptionEnum.NEVER
        self.convert_fbx_to_binary = OptionEnum.NEVER
        self.search_for_new_location = OptionEnum.NEVER

        #-Reference Update
        self.ref_expression = r"(?P<base_name>[\w]*([ |_]v?))(((?P<major>[\d]+).?)((?P<minor>[\d]+).?)?((?P<patch>[\d]+))?)?"
        self.major_update = OptionEnum.NEVER
        self.minor_update = OptionEnum.NEVER
        self.patch_update = OptionEnum.NEVER
        
        self.environment_variables = set()
        
        
    @staticmethod
    def clone(other):
        new_prefs = _PreferenceData()
        for key, value in other.__dict__.items():
            if key in new_prefs.__dict__:
                new_prefs.__dict__[key] = value
                
        return new_prefs
    
    
    @staticmethod
    def use_option(option_value: OptionEnum, question) -> bool:
        if option_value == OptionEnum.NEVER:
            return False

        elif option_value == OptionEnum.ALWAYS:
            return True

        elif option_value == OptionEnum.ASK:
            result = cmds.confirmDialog(title='3D CG Guru', message=question, messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
            return result == 'Yes'
        else:
            raise KeyError(f"OptionEnum value of {option_value} isn't supported in use_option")


def _get_save_path():
    preferences_dir = pathlib.Path(cmds.internalVar(userPrefDir=True)).joinpath(
        'cg3dmaya_v2'
    )
    preferences_dir.mkdir(parents=True, exist_ok=True)
    return preferences_dir.joinpath('prefs.pickle')


def new():
    return _PreferenceData()
        

def get():
    global _PREFS_INSTANCE
    
    if _PREFS_INSTANCE is not None:
        return _PREFS_INSTANCE

    saved_data = _get_save_path()
    if saved_data.exists():
        try:
            with open(saved_data, 'rb') as prefs_file:
                saved_prefs = pickle.load(prefs_file)
            _PREFS_INSTANCE = _PreferenceData.clone(saved_prefs)
        except (OSError, pickle.PickleError, EOFError, AttributeError, ValueError):
            cmds.warning("3D CG Maya: Preferences are reset due to corrupt data")
            set_prefs(_PreferenceData())
    else:
        set_prefs(_PreferenceData())
        
    return _PREFS_INSTANCE
        

def set_prefs(data: _PreferenceData):
    global _PREFS_INSTANCE
    _PREFS_INSTANCE = data
    saved_data = _get_save_path()
    
    with open(saved_data, "wb") as prefs_file:
        pickle.dump(data, prefs_file)
