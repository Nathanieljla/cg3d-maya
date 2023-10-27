import os
import cg3dguru
import cg3dmaya.preferences

class Cg3dMayaPrefs(cg3dguru.ui.Window):
    def __init__(self): 
        uiFilepath = os.path.join(cg3dmaya.preferences.__path__[0], 'preferences.ui')
        super(Cg3dMayaPrefs, self).__init__('cg3dmaya_prefs', uiFilepath) #, custom_widgets = custom_widgets)




def run(*args):
    #filepath = os.path.join(cg3dcasc.__path__[0],  'Cascadeur.ui' )
    editor = Cg3dMayaPrefs() #WINDOW_NAME, filepath)
    #editor.ui.resize(editor.ui.layout().minimumSize())
    editor.ui.show()