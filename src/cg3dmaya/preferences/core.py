import pymel.core as pm
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
        self.callback_switch_project = OptionEnum.NEVER
        self.callback_fbx_namespaces = OptionEnum.NEVER
        self.ref_expression = r"(?P<base_name>[\w]*([ |_]v?))(((?P<major>[\d]+).?)((?P<minor>[\d]+).?)?((?P<patch>[\d]+))?)?"
        self.major_update = OptionEnum.NEVER
        self.minor_update = OptionEnum.NEVER
        self.patch_update = OptionEnum.NEVER
        
        
    @staticmethod
    def clone(other):
        new_prefs = _PreferenceData()
        for key, value in other.__dict__.items():
            if key in new_prefs.__dict__:
                new_prefs.__dict__[key] = value
                
        return new_prefs


def _get_save_path():
    saved_data = pathlib.Path(__file__)
    saved_data = saved_data.parent
    saved_data = saved_data.joinpath('prefs.pickle')
    
    return saved_data


def new():
    return _PreferenceData()
        

def get():
    global _PREFS_INSTANCE
    
    if _PREFS_INSTANCE is not None:
        return _PREFS_INSTANCE

    saved_data = _get_save_path()
    if saved_data.exists():
        try:       
            file = open(saved_data, 'rb')
            saved_prefs = pickle.load(file)
            file.close()
            _PREFS_INSTANCE = _PreferenceData.clone(saved_prefs)
        except:
            pm.warning("3D CG Maya: Preferences are reset due to corrupt data")
            set(_PreferenceData())
    else:
        set(_PreferenceData())
        
    return _PREFS_INSTANCE
        

def set(data: _PreferenceData):
    global _PREFS_INSTANCE
    _PREFS_INSTANCE = data
    saved_data = _get_save_path()
    
    file = open(saved_data, "wb")
    pickle.dump(data, file)
    file.close()

    