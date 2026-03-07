import os
import cg3dmaya
import cg3dguru.ui
import cg3dmaya.core
import pymel.core as pm


class RigShapeEditor(cg3dguru.ui.Window):
   def __init__(self):
      uiFilepath = os.path.join(cg3dmaya.__path__[0], 'uis', 'rig_shapes.ui')
      super(RigShapeEditor, self).__init__('rig_shapes', uiFilepath)
      
      self.ui.move_shapes.pressed.connect(lambda: self.action(True))
      self.ui.copy_shapes.pressed.connect(lambda: self.action(False))


   def action(self, only_match):
      try:
         cg3dmaya.core.ShapeCloner.run(only_match=only_match)
      except Exception as e:
         pm.confirmDialog(title='Rig Shape Tool: Error', message=str(e), messageAlign='center')



def run(*args):
   editor = RigShapeEditor()
   editor.ui.show()