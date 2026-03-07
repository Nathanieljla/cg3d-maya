import os
import cg3dguru.ui
import cg3dmaya.preferences as cg_prefs

class Cg3dMayaPrefs(cg3dguru.ui.Window):
    def __init__(self): 
        uiFilepath = os.path.join(cg_prefs.__path__[0], 'preferences.ui')
        super(Cg3dMayaPrefs, self).__init__('cg3dmaya_prefs', uiFilepath) #, custom_widgets = custom_widgets)

        self.prefs = None
        self.init_ui()
        self.ui.apply.pressed.connect(self.save_prefs)
        self.ui.cancel.pressed.connect(self.cancel)
        self.ui.restore.triggered.connect(self.restore)
        
        
    def restore(self):
        self.init_ui(prefs=cg_prefs.new())


    def init_ui(self, prefs=None):
        if prefs is None:
            prefs = cg_prefs.get()
            
        self.prefs = prefs

        #idx = self.ui.switch_pref.findText(prefs.callback_switch_project.value)
        self.ui.switch_pref.setCurrentIndex(prefs.callback_switch_project)
        
        
        self.ui.fbx_namespace_pref.setCurrentIndex(prefs.callback_fbx_namespaces)
        
        self.ui.ge_fbx_deformer_choice.setCurrentIndex(prefs.remove_subdeformer_namespaces)
        self.ui.ge_fbx_binary_choice.setCurrentIndex(prefs.convert_fbx_to_binary)
        self.ui.ge_update_location_choice.setCurrentIndex(prefs.search_for_new_location)

        ev_values = list(prefs.environment_variables)
        ev_values.sort()
        ev_str = ''
        for value in ev_values:
            if not value:
                continue
            
            ev_str += f"{value}\n"
            
        self.ui.ev_name_values.setText(ev_str)
        
        self.ui.reference_regex.setPlainText(prefs.ref_expression)
        self.ui.ref_update_major.setCurrentIndex(prefs.major_update)
        self.ui.ref_update_minor.setCurrentIndex(prefs.minor_update)
        self.ui.ref_update_patch.setCurrentIndex(prefs.patch_update)

        
        
    def save_prefs(self, *args, **kwargs):
        self.prefs.callback_switch_project = cg_prefs.OptionEnum(self.ui.switch_pref.currentIndex())
        self.prefs.callback_fbx_namespaces = cg_prefs.OptionEnum(self.ui.fbx_namespace_pref.currentIndex())

        self.prefs.remove_subdeformer_namespaces = cg_prefs.OptionEnum(self.ui.ge_fbx_deformer_choice.currentIndex())
        self.prefs.convert_fbx_to_binary = cg_prefs.OptionEnum(self.ui.ge_fbx_binary_choice.currentIndex())
        self.prefs.search_for_new_location = cg_prefs.OptionEnum(self.ui.ge_update_location_choice.currentIndex())

        ev_values = set()
        for name in self.ui.ev_name_values.toPlainText().split('\n'):
            name = name.strip()
            if name:
                ev_values.add(name.strip())
            
        self.prefs.environment_variables = ev_values

        self.prefs.ref_expression = self.ui.reference_regex.toPlainText()
        self.prefs.major_update = cg_prefs.OptionEnum(self.ui.ref_update_major.currentIndex())
        self.prefs.minor_update = cg_prefs.OptionEnum(self.ui.ref_update_minor.currentIndex())
        self.prefs.patch_update = cg_prefs.OptionEnum(self.ui.ref_update_patch.currentIndex())
        
        cg_prefs.set_prefs(self.prefs)
        self.ui.close()

    def cancel(self, *args, **kwargs):
        self.ui.close()



def run(*args):
    #filepath = os.path.join(cg3dcasc.__path__[0],  'Cascadeur.ui' )
    editor = Cg3dMayaPrefs() #WINDOW_NAME, filepath)
    #editor.ui.resize(editor.ui.layout().minimumSize())
    editor.ui.show()