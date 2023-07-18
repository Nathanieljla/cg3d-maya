
import os

import pymel.core as pm
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

#from PySide2.QtCore import * 
from PySide2.QtUiTools import *
#from PySide2 import __version__
#from shiboken2 import wrapInstance 

import cg3dmaya
import cg3dguru.ui
import cg3dmaya.cascadeur.core


WINDOW_NAME = 'HIK Export'

#<class>DropLineEdit</class>
#<extends>QLineEdit</extends>
#<header>cg3dmaya/cascadeur/editor.py</header>
#https://python.hotexamples.com/examples/PySide.QtUiTools/QUiLoader/registerCustomWidget/python-quiloader-registercustomwidget-method-examples.html
#https://stackoverflow.com/questions/4625102/how-to-replace-a-widget-with-another-using-qt
class DropLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(DropLineEdit, self).__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        input_text = event.mimeData().text()
        entries = input_text.split('\n')
        
        if entries and len(entries) == 1:
            entries[0]
            self.setText(entries[0]) #.lstrip('|'))



class HikExportEditor(cg3dguru.ui.Window):
    def __init__(self, windowKey, uiFilepath, *args, **kwargs):
        custom_widgets = [DropLineEdit]
        super(HikExportEditor, self).__init__(windowKey, uiFilepath, custom_widgets = custom_widgets)
        self.job_handlers = {}
        self.add_script_jobs()
        self.qrig_data = cg3dmaya.cascadeur.core.QRigData()
        self.character_nodes = {}        
        self.spine_joints = {}
        
        self.active_character = None
        self.init_ui()
        
        #signals
        self.ui.spine_list.currentTextChanged.connect( self._spine_choice_changed )
        self.ui.left_weapon_node.textChanged.connect( lambda : self._weapon_changed(self.ui.left_weapon_node, "leftWeapon") )
        self.ui.right_weapon_node.textChanged.connect( lambda : self._weapon_changed(self.ui.right_weapon_node, "rightWeapon") )
        
        
    def _weapon_changed(self, control, attr_name):
        print(attr_name)
        if not self.active_character:
            return          
        
        name = control.text()
        if not name:
            rig_data = self.qrig_data.get_data(self.active_character)
            #if rig_data:
                #node.message >> rig_data.leftWeapon
                
        try:
            node = pm.PyNode(name)
        except:
            node = None
     
        if node:
            rig_data = self.qrig_data.get_data(self.active_character)
            if rig_data:
                attr = rig_data.attr(attr_name)
                node.message >> attr  
        

    #def _left_weapon_changed(self, *args):
        #if not self.active_character:
            #return          
        
        #name = args[0]
        #if not name:
            #rig_data = self.qrig_data.get_data(self.active_character)
            ##if rig_data:
                ##node.message >> rig_data.leftWeapon
                
        #try:
            #node = pm.PyNode(name)
        #except:
            #node = None
     
        #if node:
            #rig_data = self.qrig_data.get_data(self.active_character)
            #if rig_data:
                #node.message >> rig_data.leftWeapon



    def _spine_choice_changed(self, *args, **kwargs):
        if not self.active_character:
            return
        
        joint = self.ui.spine_list.currentData()
        if not joint:
            return
        
        rig_data = self.qrig_data.get_data(self.active_character)
        if rig_data:
            joint.message >> rig_data.chestJoint
            
        blank_idx = self.ui.spine_list.findText('')
        if blank_idx > -1:
            self.ui.spine_list.removeItem(blank_idx)
        
        
    def _init_drag_n_drop(self):
        #https://stackoverflow.com/questions/60012363/set-qlineedit-to-read-only-but-still-accept-drops
        self.ui.left_weapon_node.setReadOnly(True)
        self.ui.left_weapon_node.setAcceptDrops(True)
        
        
        
    def _init_character_list(self):
        self.character_nodes.clear()
        self.ui.character_list.clear()

        character_definitions = pm.ls(type='HIKCharacterNode')
        for character_node in  character_definitions:
            self.character_nodes[character_node.name()] = character_node
            
        character_names = list(self.character_nodes)
        character_names.sort()
        
        self.active_character = None
        if character_names:
            for name in character_names:
                self.ui.character_list.addItem(name, self.character_nodes[name])
                
            self.active_character = self.ui.character_list.currentData()
            
        self.ui.qrig_data.setEnabled(self.active_character is not None)
                
        
    
    def _init_spine_list(self):
        self.ui.spine_list.blockSignals(True)
        
        self.spine_joints.clear()
        self.ui.spine_list.clear()
        
        if not self.active_character:
            return
        
        spine_joints = cg3dmaya.cascadeur.core.get_spine_joints(self.active_character)
        for joint in spine_joints:
            self.spine_joints[joint.name()] = joint
        
        spine_names = list(self.spine_joints)
        spine_names.sort()
        for name in spine_names:
            self.ui.spine_list.addItem(name, self.spine_joints[name])
        
        #Make an empty entry if the rig_data doesn't reference a valid spine
        #otherwise set the dropdown the matching spine
        rig_data = self.qrig_data.get_data(self.active_character, force_add = True)
        inputs = rig_data.chestJoint.inputs()
        valid_spine = None
        if inputs and inputs[0].name() in self.spine_joints:
            valid_spine = inputs[0]
            
        if valid_spine is None:
            self.ui.spine_list.addItem('', None)
            self.ui.spine_list.setCurrentText('')
        else:
            self.ui.spine_list.setCurrentText(valid_spine.name())
            
        self.ui.spine_list.blockSignals(False)
        
        
    def _init_weapon_nodes(self):
        def set_ui_value(ui_element, value):
            ui_element.blockSignals(True)
            ui_element.setText(value)
            ui_element.blockSignals(False)
            
            
        set_ui_value(self.ui.left_weapon_node, '')
        set_ui_value(self.ui.right_weapon_node, '')
                     
        if not self.active_character:
            return
        
        rig_data = self.qrig_data.get_data(self.active_character)
        inputs = rig_data.leftWeapon.inputs()
        if inputs:
            set_ui_value(self.ui.left_weapon_node, inputs[0].name().lstrip('|'))
            
        inputs = rig_data.rightWeapon.inputs()
        if inputs:
            set_ui_value(self.ui.right_Weapon_node, inputs[0].name().lstrip('|'))

        
    def init_ui(self):
        self._init_character_list()
        self._init_spine_list()
        self._init_drag_n_drop()
        self._init_weapon_nodes()
        
        
    def scene_loaded(self):
        isVisible = self.ui.centralwidget.isVisible()
        print("HikExportEditor: refreshing character list {}".format(isVisible))
        if isVisible:
            self.init_ui()
        
        
    def _add_script_job(self, event_name, func):
        jobId   = pm.scriptJob( event=[event_name, func] )
        handler = lambda : self.remove_script_job(jobId)
        self.job_handlers[jobId] = handler
        self.ui.destroyed.connect( handler )
        
        
    def add_script_jobs(self):
        self.job_handlers = {}
        self._add_script_job('PostSceneRead', self.scene_loaded)
        self._add_script_job('NewSceneOpened', self.scene_loaded)
    
    
    def remove_script_job(self, jobId):
        print("removing script job")
        self.ui.destroyed.disconnect( self.job_handlers[jobId] )
        pm.scriptJob( kill = jobId )
        
  
        
def run():

    filepath = os.path.join(cg3dmaya.cascadeur.__path__[0],  'Cascadeur.ui' )
    editor = HikExportEditor(WINDOW_NAME, filepath)
    editor.ui.show()