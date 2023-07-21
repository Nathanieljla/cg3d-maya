
import os

import pymel.core as pm
from PySide2.QtWidgets import *

import cg3dmaya
import cg3dguru.ui
import cg3dmaya.cascadeur.core


WINDOW_NAME = 'HIK Export'

#for Designer "PromotTo" you want to put cg3dmaya/cascadeur/editor.py for the header
#and use QUiLoader.registerCustomWidget(DropLinEdit)
class DropLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(DropLineEdit, self).__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        input_text = event.mimeData().text()
        entries = input_text.split('\n')
        
        if not entries or len(entries) != 1:
            return
        
        node = pm.PyNode(entries[0])
        if node.type() != 'joint':
            return
        
        event.acceptProposedAction()


    def dropEvent(self, event):
        input_text = event.mimeData().text()
        segments = input_text.split('|')
        
        try:
            #This will except when there's a name conflict
            pm.PyNode(segments[-1])
            input_text = segments[-1]
        except:
            print('Name conflict. Using long name')
        
        self.setText(input_text)



class HikExportEditor(cg3dguru.ui.Window):
    def __init__(self, windowKey, uiFilepath, *args, **kwargs):
        custom_widgets = [DropLineEdit]
        super(HikExportEditor, self).__init__(windowKey, uiFilepath, custom_widgets = custom_widgets)
        self.job_handlers = {}
        self.add_script_jobs()
        self.qrig_data = cg3dmaya.cascadeur.core.QRigData()
        self.export_data_instance = cg3dmaya.cascadeur.core.CascExportData()
        self.scene_nodes = {}        
        self.spine_joints = {}
        self.extras = {}
        
        self.loading_data = False
        self.node_to_select = None
        self.active_selection = None
        self.rig_data = None
        self.export_data = None

        self._init_drag_n_drop()
        self.init_ui()
        
        #signals
        self.ui.scene_list.currentTextChanged.connect(self.on_node_selected)
        self.ui.spine_list.currentTextChanged.connect( self.on_spine_choice_changed )
        self.ui.create_data_button.pressed.connect(self.on_create_data)
        self.ui.add_hik_button.pressed.connect(self.on_add_hik)
        self.ui.left_weapon_node.textChanged.connect( lambda : self.on_weapon_changed(self.ui.left_weapon_node, "leftWeapon") )
        self.ui.right_weapon_node.textChanged.connect( lambda : self.on_weapon_changed(self.ui.right_weapon_node, "rightWeapon") )
        self.ui.clear_left_weapon.pressed.connect(lambda : self.on_clear_weapon(self.ui.left_weapon_node))
        self.ui.clear_right_weapon.pressed.connect(lambda : self.on_clear_weapon(self.ui.right_weapon_node))
        self.ui.add_extras.pressed.connect(self.on_add_extras)
        self.ui.remove_extras.pressed.connect(self.on_remove_extras)
        self.ui.align_pelvis.stateChanged.connect(self.on_align_pelvis)
        self.ui.create_layers.stateChanged.connect(self.on_create_layers)
        self.ui.export_button.pressed.connect(self.on_export)
                
                
                
    def _create_export_data(self, node = None):
        if not node:
            node, data = cg3dmaya.cascadeur.core.CascExportData.create_node(nodeType = 'objectSet')
        else:
            self.export_data_instance.add_data(node)
            
        return node
                
        
        
    def on_create_data(self, *args, **kwargs):
        data_name, ok = QInputDialog.getText(None, "New Node Name", 'Name this data')
        if ok:
            new_node = self._create_export_data()
            pm.rename(new_node, data_name)
            self.node_to_select = new_node
            
        self.init_ui()
            
    
    
    def on_add_hik(self):
        
        pass
        
        
    def on_export(self):
        if not self.export_data:
            return
        
        cg3dmaya.cascadeur.core.export(self.export_data, qrig_data=self.rig_data, character_node=self.active_selection)
        
    def on_align_pelvis(self, *args):
        if self.loading_data or not self.active_selection:
            return
        
        self.rig_data.alignPelvis.set(args[0] != 0)
      
        
    def on_create_layers(self, *args):
        if self.loading_data or not self.active_selection:
            return
        
        self.rig_data.createLayers.set(args[0] != 0)    
        
        
    def _get_active_node(self):
        self.active_selection = None
        self.rig_data = None
        self.export_data = None        
        
        if self.ui.scene_list.currentText():
            self.active_selection = self.ui.scene_list.currentData()
            self.export_data = self.export_data_instance.get_data(self.active_selection) #, force_add = True)
            
            if not self.export_data:
                pm.error("Casc Editor: Active node somehow doesn't have export data?!?")
            
            self.rig_data = self.qrig_data.get_data(self.active_selection) #, force_add = True)
            
            
        self.ui.qrig_data.setVisible(self.rig_data is not None)
        
        
    def on_node_selected(self, *args):
        if self.loading_data:
            return
        
        self._get_active_node()
        
        
    def on_remove_extras(self):
        if self.loading_data or not self.active_selection:
            return
        
        selected_items = self.ui.extras_list.selectedItems()
        for item in selected_items:
            node = self.extras[item.text()]
            pm.Attribute.disconnect(node.message, self.export_data.exportNodes, nextAvailable=True)
            
        self._init_extras_view()
        
        
    def on_add_extras(self):
        if self.loading_data or not self.active_selection:
            return              
        
        selection = pm.ls(sl=True,type=['transform','objectSet', 'skinCluster'])
        for selected in selection:
            if selected.message.isConnectedTo(self.export_data.exportNodes,
                                              checkOtherArray=True):
                continue
            
            pm.Attribute.connect(selected.message,
                                 self.export_data.exportNodes, nextAvailable=True)

            
        self._init_extras_view()
        
        
    def on_clear_weapon(self, weapon):
        weapon.setText('')
        
        
    def on_weapon_changed(self, control, attr_name):
        if self.loading_data or not self.active_selection:
            return                 
        
        name = control.text()
        if not name:
            if self.rig_data:
                attr = self.rig_data.attr(attr_name)
                inputs = attr.inputs(plugs=True)
                if inputs:
                    inputs[0] // attr
            
        else:    
            try:
                node = pm.PyNode(name)
            except:
                node = None
         
            if node:
                if self.rig_data:
                    attr = self.rig_data.attr(attr_name)
                    node.message >> attr  


    def on_spine_choice_changed(self, *args, **kwargs):
        if self.loading_data or not self.active_selection:
            return        
        
        joint = self.ui.spine_list.currentData()
        if not joint:
            return
        
        if self.rig_data:
            joint.message >> self.rig_data.chestJoint
            
        blank_idx = self.ui.spine_list.findText('')
        if blank_idx > -1:
            self.ui.spine_list.removeItem(blank_idx)
        
        
    def _init_drag_n_drop(self):
        #https://stackoverflow.com/questions/60012363/set-qlineedit-to-read-only-but-still-accept-drops
        self.ui.left_weapon_node.setReadOnly(True)
        self.ui.left_weapon_node.setAcceptDrops(True)
        
        
    
    def _get_invalid_characters(self):
        hik_nodes = pm.ls(type='HIKCharacterNode')
        valid_nodes = cg3dguru.user_data.Utils.get_nodes_with_data(nodes = hik_nodes, data_class=cg3dmaya.cascadeur.core.CascExportData)
        hik_nodes = set(hik_nodes)
        valid_nodes = set(valid_nodes)
        
        return hik_nodes.difference(valid_nodes)
        
        
        
    def _init_scene_list(self):
        self.scene_nodes.clear()
        self.ui.scene_list.clear()
            
        #Find the data in our scene
        scene_sets = pm.ls(type='objectSet')
        data_nodes = cg3dguru.user_data.Utils.get_nodes_with_data(scene_sets, data_class=cg3dmaya.cascadeur.core.CascExportData)
        
        for node in  data_nodes:
            self.scene_nodes[node.name()] = node
            
            
        #Build our dropdown list when the names sorted
        node_names = list(self.scene_nodes)
        node_names.sort()
        
        self.active_selection = None
        if node_names:
            for name in node_names:
                self.ui.scene_list.addItem(name, self.scene_nodes[name])
            
            if self.node_to_select:
                idx = self.ui.scene_list.findText(self.node_to_select.name())
                self.node_to_select = None
                if idx > -1:
                    self.ui.scene_list.setCurrentIndex(idx)

            self.active_selection = self.ui.scene_list.currentData()
             
                  
        #let's activate and hide data based on our scene list
        invalid_nodes = self._get_invalid_characters()
        self.ui.add_hik_button.setVisible(len(invalid_nodes) > 0)
        self.ui.selected_data_widget.setEnabled(self.active_selection is not None)

    
    def _init_spine_list(self):
        self.spine_joints.clear()
        self.ui.spine_list.clear()
        
        if not self.rig_data:
            return
        
        spine_joints = cg3dmaya.cascadeur.core.get_spine_joints(self.active_selection)
        for spine_name, joint in spine_joints:
            self.spine_joints[joint.name()] = joint
        
        spine_names = list(self.spine_joints)
        spine_names.sort()
        for name in spine_names:
            self.ui.spine_list.addItem(name, self.spine_joints[name])
        
        #Make an empty entry if the rig_data doesn't reference a valid spine
        #otherwise set the dropdown the matching spine
        inputs = self.rig_data.chestJoint.inputs()
        valid_spine = None
        if inputs and inputs[0].name() in self.spine_joints:
            valid_spine = inputs[0]
            
        if valid_spine is None:
            self.ui.spine_list.addItem('', None)
            self.ui.spine_list.setCurrentText('')
        else:
            self.ui.spine_list.setCurrentText(valid_spine.name())

        
        
    def _init_extras_view(self):
        self.ui.extras_list.clear()
        self.extras.clear()
        
        if not self.active_selection:
            return
        
        inputs = self.export_data.exportNodes.inputs()
        names = []
        for node in inputs:
            name = node.name()
            names.append(name)
            self.extras[name] = node

        names.sort()
        self.ui.extras_list.addItems(names)
        

    def _init_weapon_nodes(self):
        def set_ui_value(ui_element, attr_name):
            attr = self.rig_data.attr(attr_name)
            inputs = attr.inputs()
            if inputs:
                ui_element.setText(inputs[0].name())

        self.ui.left_weapon_node.setText('')
        self.ui.right_weapon_node.setText('')
                     
        if not self.rig_data:
            return
        
        set_ui_value(self.ui.left_weapon_node, 'leftWeapon')
        set_ui_value(self.ui.right_weapon_node, 'rightWeapon')

        
    def _init_check_boxes(self):
        if not self.rig_data:
            self.ui.align_pelvis.setChecked(False)
            self.ui.create_layers.setChecked(False)
        else:
            self.ui.align_pelvis.setChecked(self.rig_data.alignPelvis.get())
            self.ui.create_layers.setChecked(self.rig_data.createLayers.get())
                        
        
    def init_ui(self):
        self.loading_data = True
        self._init_scene_list()
        self._get_active_node()
        self._init_spine_list()
        self._init_weapon_nodes()
        self._init_check_boxes()
        self._init_extras_view()
        self.loading_data = False
        
        
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
        
  
        
def run(*args):
    filepath = os.path.join(cg3dmaya.cascadeur.__path__[0],  'Cascadeur.ui' )
    editor = HikExportEditor(WINDOW_NAME, filepath)
    editor.ui.show()