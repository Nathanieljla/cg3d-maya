import os
import cg3dguru.ui
import cg3dmaya.preferences

class Cg3dMayaPrefs(cg3dguru.ui.Window):
    def __init__(self): 
        uiFilepath = os.path.join(cg3dmaya.preferences.__path__[0], 'preferences.ui')
        super(Cg3dMayaPrefs, self).__init__('cg3dmaya_prefs', uiFilepath) #, custom_widgets = custom_widgets)

        self.prefs = None
        self.init_ui()
        self.ui.apply.pressed.connect(self.save_prefs)
        self.ui.cancel.pressed.connect(self.cancel)
        self.ui.restore.triggered.connect(self.restore)
        
        
    def restore(self):
        self.init_ui(prefs=cg3dmaya.preferences.new())


    def init_ui(self, prefs=None):
        if prefs is None:
            prefs = cg3dmaya.preferences.get()
            
        self.prefs = prefs

        idx = self.ui.switch_pref.findText(prefs.callback_switch_project.value)
        self.ui.switch_pref.setCurrentIndex(idx)
        
        idx = self.ui.fbx_namespace_pref.findText(prefs.callback_fbx_namespaces.value)
        self.ui.fbx_namespace_pref.setCurrentIndex(idx)

        
        
    def save_prefs(self, *args, **kwargs):
        self.prefs.callback_switch_project = cg3dmaya.preferences.CallbackEnum(self.ui.switch_pref.currentText())
        self.prefs.callback_fbx_namespaces = cg3dmaya.preferences.CallbackEnum(self.ui.fbx_namespace_pref.currentText())
        cg3dmaya.preferences.set(self.prefs)
        self.ui.close()

    def cancel(self, *args, **kwargs):
        self.ui.close()



def run(*args):
    #filepath = os.path.join(cg3dcasc.__path__[0],  'Cascadeur.ui' )
    editor = Cg3dMayaPrefs() #WINDOW_NAME, filepath)
    #editor.ui.resize(editor.ui.layout().minimumSize())
    editor.ui.show()