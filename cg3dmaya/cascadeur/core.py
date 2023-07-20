
import json
import tempfile
import os

import pymel.core as pm

import cg3dguru.user_data
import cg3dguru.animation.fbx


#https://forums.autodesk.com/t5/maya-programming/python-hik/td-p/4262564
#https://mayastation.typepad.com/maya-station/2011/04/maya-2012-hik-menus-and-mel-commands-part-1.html
#https://github.com/bungnoid/glTools/blob/master/utils/hik.py

HIK_ATTRS = {
    'Reference': None, 
    'Hips': 'pelvis',
    'HipsTranslation' : None, 
    'Spine': 'stomach',
    #anyone of the spine1-9 could be the chest bone.
    #which is based on the user_data selection
    'Spine1': 'chest', 
    'Spine2': 'chest',
    'Spine3': 'chest',
    'Spine4': 'chest',
    'Spine5': 'chest',
    'Spine6': 'chest',
    'Spine7': 'chest',
    'Spine8': 'chest',
    'Spine9': 'chest',
    'Neck': 'neck',
    'Neck1': None,
    'Neck2': None,
    'Neck3': None,
    'Neck4': None,
    'Neck5': None,
    'Neck6': None,
    'Neck7': None,
    'Neck8': None,
    'Neck9': None, 
    'Head': 'head',
    'LeftUpLeg': 'thigh_l',
    'LeftLeg': 'calf_l',
    'LeftFoot': 'foot_l',
    'LeftToeBase': 'toe_l',
    'LeftShoulder': 'clavicle_l',
    'LeftShoulderExtra': None, 
    'LeftArm': 'arm_l',
    'LeftForeArm': 'forearm_l',
    'LeftHand': 'hand_l',
    'LeftFingerBase': None,
    'LeftHandThumb1': 'thumb_l_1', 
    'LeftHandThumb2': 'thumb_l_2',
    'LeftHandThumb3': 'thumb_l_3',
    'LeftHandThumb4': None,
    'LeftHandIndex1': 'index_finger_l_1',
    'LeftHandIndex2': 'index_finger_l_2',
    'LeftHandIndex3': 'index_finger_l_3',
    'LeftHandIndex4': None,
    'LeftHandMiddle1':'middle_finger_l_1',
    'LeftHandMiddle2': 'middle_finger_l_2',
    'LeftHandMiddle3': 'middle_finger_l_3',
    'LeftHandMiddle4': None,
    'LeftHandRing1':'ring_finger_l_1',
    'LeftHandRing2':'ring_finger_l_2',
    'LeftHandRing3':'ring_finger_l_3',
    'LeftHandRing4': None,
    'LeftHandPinky1':'pinky_finger_l_1',
    'LeftHandPinky2':'pinky_finger_l_2', 
    'LeftHandPinky3':'pinky_finger_l_3',
    'LeftHandPinky4': None,
    'LeftHandExtraFinger1': None,
    'LeftHandExtraFinger2': None, 
    'LeftHandExtraFinger3': None, 
    'LeftHandExtraFinger4': None,
    'LeftInHandThumb': None,
    'LeftInHandIndex': None,
    'LeftInHandMiddle': None,
    'LeftInHandRing': None,
    'LeftInHandPinky': None,
    'LeftInHandExtraFinger': None,
    'LeftFootThumb1': None, 
    'LeftFootThumb2': None,
    'LeftFootThumb3': None,
    'LeftFootThumb4': None,
    'LeftFootIndex1': None,
    'LeftFootIndex2': None,
    'LeftFootIndex3': None,
    'LeftFootIndex4': None,
    'LeftFootMiddle1': None,
    'LeftFootMiddle2': None,
    'LeftFootMiddle3': None,
    'LeftFootMiddle4': None,
    'LeftFootRing1': None,
    'LeftFootRing2': None,
    'LeftFootRing3': None,
    'LeftFootRing4': None,
    'LeftFootPinky1': None,
    'LeftFootPinky2': None,
    'LeftFootPinky3': None,
    'LeftFootPinky4': None,
    'LeftFootExtraFinger1': None,
    'LeftFootExtraFinger2': None, 
    'LeftFootExtraFinger3': None, 
    'LeftFootExtraFinger4': None,
    'LeftInFootThumb': None,
    'LeftInFootIndex': None,
    'LeftInFootMiddle': None,
    'LeftInFootRing': None,
    'LeftInFootPinky': None, 
    'LeftInFootExtraFinger': None,
    'LeftUpLegRoll' : None, #this isn't in the HIK UI
    'LeftLegRoll': None, #this isn't in the HIK UI
    'LeftArmRoll': None, #this isn't in the HIK UI
    'LeftForeArmRoll': None, #this isn't in the HIK UI
    'LeafLeftUpLegRoll1': 'thigh_l',
    'LeafLeftUpLegRoll2': None,
    'LeafLeftUpLegRoll3': None,
    'LeafLeftUpLegRoll4': None,
    'LeafLeftUpLegRoll5': None, 
    'LeafLeftLegRoll1': 'calf_l',
    'LeafLeftLegRoll2': None,
    'LeafLeftLegRoll3': None,
    'LeafLeftLegRoll4': None,
    'LeafLeftLegRoll5': None, 
    'LeafLeftArmRoll1': 'arm_l',
    'LeafLeftArmRoll2': None,
    'LeafLeftArmRoll3': None,
    'LeafLeftArmRoll4': None,
    'LeafLeftArmRoll5': None, 
    'LeafLeftForeArmRoll1': 'forearm_l',
    'LeafLeftForeArmRoll2': None,
    'LeafLeftForeArmRoll3': None,
    'LeafLeftForeArmRoll4': None,
    'LeafLeftForeArmRoll5': None,
    'RightUpLeg': 'thigh_r',
    'RightLeg': 'calf_r',
    'RightFoot': 'foot_r',
    'RightToeBase': 'toe_r',
    'RightShoulder': 'clavicle_r',
    'RightShoulderExtra': None, 
    'RightArm': 'arm_r',
    'RightForeArm': 'forearm_r',
    'RightHand': 'hand_r',
    'RightFingerBase': None,
    'RightHandThumb1': 'thumb_r_1', 
    'RightHandThumb2': 'thumb_r_2',
    'RightHandThumb3': 'thumb_r_3',
    'RightHandThumb4': None,
    'RightHandIndex1': 'index_finger_r_1',
    'RightHandIndex2': 'index_finger_r_2',
    'RightHandIndex3': 'index_finger_r_3',
    'RightHandIndex4': None,
    'RightHandMiddle1':'middle_finger_r_1',
    'RightHandMiddle2': 'middle_finger_r_2',
    'RightHandMiddle3': 'middle_finger_r_3',
    'RightHandMiddle4': None,
    'RightHandRing1':'ring_finger_r_1',
    'RightHandRing2':'ring_finger_r_2',
    'RightHandRing3':'ring_finger_r_3',
    'RightHandRing4': None,
    'RightHandPinky1':'pinky_finger_r_1',
    'RightHandPinky2':'pinky_finger_r_2', 
    'RightHandPinky3':'pinky_finger_r_3',
    'RightHandPinky4': None,
    'RightHandExtraFinger1': None,
    'RightHandExtraFinger2': None, 
    'RightHandExtraFinger3': None, 
    'RightHandExtraFinger4': None,
    'RightInHandThumb': None,
    'RightInHandIndex': None,
    'RightInHandMiddle': None,
    'RightInHandRing': None,
    'RightInHandPinky': None,
    'RightInHandExtraFinger': None,
    'RightFootThumb1': None, 
    'RightFootThumb2': None,
    'RightFootThumb3': None,
    'RightFootThumb4': None,
    'RightFootIndex1': None,
    'RightFootIndex2': None,
    'RightFootIndex3': None,
    'RightFootIndex4': None,
    'RightFootMiddle1': None,
    'RightFootMiddle2': None,
    'RightFootMiddle3': None,
    'RightFootMiddle4': None,
    'RightFootRing1': None,
    'RightFootRing2': None,
    'RightFootRing3': None,
    'RightFootRing4': None,
    'RightFootPinky1': None,
    'RightFootPinky2': None,
    'RightFootPinky3': None,
    'RightFootPinky4': None,
    'RightFootExtraFinger1': None,
    'RightFootExtraFinger2': None, 
    'RightFootExtraFinger3': None, 
    'RightFootExtraFinger4': None,
    'RightInFootThumb': None,
    'RightInFootIndex': None,
    'RightInFootMiddle': None,
    'RightInFootRing': None,
    'RightInFootPinky': None, 
    'RightInFootExtraFinger': None,
    'RightUpLegRoll' : None, #this isn't in the HIK UI
    'RightLegRoll': None, #this isn't in the HIK UI
    'RightArmRoll': None, #this isn't in the HIK UI
    'RightForeArmRoll': None, #this isn't in the HIK UI
    'LeafRightUpLegRoll1': 'thigh_r',
    'LeafRightUpLegRoll2': None,
    'LeafRightUpLegRoll3': None,
    'LeafRightUpLegRoll4': None,
    'LeafRightUpLegRoll5': None, 
    'LeafRightLegRoll1': 'calf_r',
    'LeafRightLegRoll2': None,
    'LeafRightLegRoll3': None,
    'LeafRightLegRoll4': None,
    'LeafRightLegRoll5': None, 
    'LeafRightArmRoll1': 'arm_r',
    'LeafRightArmRoll2': None,
    'LeafRightArmRoll3': None,
    'LeafRightArmRoll4': None,
    'LeafRightArmRoll5': None, 
    'LeafRightForeArmRoll1': 'forearm_r',
    'LeafRightForeArmRoll2': None,
    'LeafRightForeArmRoll3': None,
    'LeafRightForeArmRoll4': None,
    'LeafRightForeArmRoll5': None,
}

_ACTIVE_CHARACTER_NODE = None
_ACTIVE_USER_DATA = None



class QRigData(cg3dguru.user_data.BaseData):
    @classmethod
    def get_prefix(cls):
        return ''
    
    
    @staticmethod
    def get_attributes():
        attrs = [
            cg3dguru.user_data.create_attr('name', 'string'), 
            cg3dguru.user_data.create_attr('chestJoint', 'message'),
            cg3dguru.user_data.create_attr('leftWeapon', 'message'),
            cg3dguru.user_data.create_attr('rightWeapon', 'message'),
            cg3dguru.user_data.create_attr('alignPelvis', 'bool'),
            cg3dguru.user_data.create_attr('createLayers', 'bool'),
            cg3dguru.user_data.create_attr('exportExtras', 'message', multi = True, indexMatters = False),            
        ]
        
        return attrs
    
    
    def post_create(self, data):
        data.createLayers.set(1)



def _get_list_of_parents(transform, input_list):
    parent = transform.getParent()
    if parent is not None:
        input_list.append(parent.name())
        _get_list_of_parents(parent, input_list)
        
    else:
        input_list.reverse()
    


def _get_input_joint(key):
    global _ACTIVE_CHARACTER_NODE    

    attr = _ACTIVE_CHARACTER_NODE.attr(key)
    inputs = attr.inputs()
    if not inputs:
        return None
    
    return inputs[0]    



def _get_joint_struct(key):    
    #TODO: Default structure...Should this be written to disc if the structure is Null?
    joint_struct = {
        'Bone name': HIK_ATTRS[key],
        'Joint name': '',
        'Joint path': [],
    }    
    
    joint = _get_input_joint(key)
    if joint is None:
        return joint_struct
    
    parent_list = []
    _get_list_of_parents(joint, parent_list)
    
    joint_struct['Joint name'] = joint.name().lstrip('|')
    joint_struct['Joint path'] = parent_list
    return joint_struct
    

def _get_section(section_name, keys, user_data = None):
    names_list = []
    for key in keys:
        joint_struct = _get_joint_struct(key)
        ##let's skip invalid results
        #if joint_struct['Joint name']:
        names_list.append(joint_struct)        
    
    output = {
        'Section': section_name,
        'Names' : names_list
    }
    
    return output


def _get_settings_values(user_data):
    if user_data is None:
        return (False, True)
    
    return (user_data.alignPelvis.get(), user_data.createLayers.get())


def get_qrig_struct(user_data = None):
    
    default_spine = 'Spine1'
    if user_data:
        spine_joints = get_spine_joints(_ACTIVE_CHARACTER_NODE)
        if len(spine_joints) > 2:
            selected_chest_joint = user_data.chestJoint.inputs()[0]
            for spine_name, joint in spine_joints:
                if joint == selected_chest_joint:
                    default_spine = spine_name
                    print('spine name {}'.format(spine_name))
    
    
    body_title = {
        'Title' : 'Body',
        'Sections' :  [
            _get_section('Body', ['Hips', 'Spine', default_spine, 'Neck', 'Head']),
            _get_section('Left arm', ['LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand']),
            _get_section('Right arm', ['RightShoulder', 'RightArm', 'RightForeArm', 'RightHand']),
            _get_section('Left leg', ['LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase']),
            _get_section('Right leg', ['RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase']),
            ]
    }
    
    l_hand_title = {
        'Title' : 'Left hand',
        'Sections' :  [
            _get_section('Thumb', ['LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3']),
            _get_section('Index finger', ['LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3']),
            _get_section('Middle finger', ['LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3']),
            _get_section('Ring finger', ['LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3']),
            _get_section('Pinky finger', ['LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3']),
            ]
    }
    
    r_hand_title = {
        'Title' : 'Right hand',
        'Sections' :  [
            _get_section('Thumb', ['RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3']),
            _get_section('Index finger', ['RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3']),
            _get_section('Middle finger', ['RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3']),
            _get_section('Ring finger', ['RightHandRing1', 'RightHandRing2', 'RightHandRing3']),
            _get_section('Pinky finger', ['RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3']),
            ]
    }
    
    twists_title = {
        'Title' : 'Twist bones',
        'Sections' :  [
            _get_section('Left arm', ['LeafLeftArmRoll1', 'LeafLeftForeArmRoll1']),
            _get_section('Right arm', ['LeafRightArmRoll1', 'LeafRightForeArmRoll1']),
            _get_section('Left leg', ['LeafLeftUpLegRoll1', 'LeafLeftLegRoll1']),
            _get_section('Right leg', ['LeafRightUpLegRoll1', 'LeafRightLegRoll1']),
            ]
    } 
    
    root = {}
    root['Document'] = [body_title, l_hand_title, r_hand_title, twists_title]
    
    align_pelvis, create_layers = _get_settings_values(user_data)
    root['Settings'] = {
        'Is align pelvis': align_pelvis,
        'Is create layers' : create_layers,
    }
    
    return root



def get_root_parent(input_transform):
    """Returns the highest level transform node for the given input transform"""
    parent = input_transform.getParent()
    if parent:
        return get_root_parent(parent)
    else:
        return input_transform
    
    
def add_transform_roots(transform_list, root_set):
    """Find the top level parent of each item in the list and add it to the set"""
    for dag in transform_list:
        root_parent = get_root_parent(dag)
        if root_parent not in root_set:
            root_set.add(root_parent)




#def get_joint_roots(character_node):
    #"""Returns a list of all the hik character joint's top level transforms"""
    #global _ACTIVE_CHARACTER_NODE
    #_ACTIVE_CHARACTER_NODE = character_node
    
    #roots = set()
    #for key in HIK_ATTRS:
        #joint = _get_input_joint(key)
        #if joint:
            #root = get_root_parent(joint)
            #if root not in roots:
                #roots.add(root)
                
    #return roots
            
            

def get_skinned_meshes(character_node):
    """return a list of meshes that are deformed by the hik character joints"""
    global _ACTIVE_CHARACTER_NODE
    _ACTIVE_CHARACTER_NODE = character_node
    
    joints = []
    for key in HIK_ATTRS:
        joint = _get_input_joint(key)
        if joint:
            joints.append(joint)
            
    skin_clusters = {}
    for joint in joints:
        world_matrix = joint.attr('worldMatrix')
        outputs = world_matrix.outputs()
        for output in outputs:
            if output.type() == 'skinCluster':
                skin_clusters[output.name()] = output
                
    print(skin_clusters)
    results = []
    for key, skin_cluster in skin_clusters.items():
        output_geo = skin_cluster.attr('outputGeometry')
        for geo in output_geo.outputs():
            if geo not in results:
                results.append(geo)
                
    return results



def get_joint_skin_clusters(joints):
    """Given a list of joints, return a set of associated skinClusters"""
    
    clusters = set()
    for joint in joints:
        world_matrix = joint.attr('worldMatrix')
        outputs = world_matrix.outputs()
        for output in outputs:
            if output.type() == 'skinCluster' and output not in clusters:
                clusters.add(output)
                
    return clusters
                
                
                
def get_skin_cluster_joints(skin_clusters):
    """Given a list of skinClusters, return a set of associated joints"""
    joint_set = set()
    for skin_cluster in skin_clusters:
        temp_set = set(skin_cluster.matrix.inputs())
        joint_set.update(temp_set)
        
    return joint_set


def get_mesh_skin_clusters(meshes):
    """Given a list of meshes, return a set of associated skinClusters"""
    clusters = set()
    for m in meshes:
        inputs = m.inMesh.inputs()
        if inputs and isinstance(inputs[0], pm.nodetypes.SkinCluster):
            clusters.add(inputs[0])
            
    return clusters


def get_skin_cluster_meshes(skin_clusters):
    """Given a list of skinClusters, return a set of associated meshes"""
    meshes = set()
    for cluster in skin_clusters:
        output_geo = cluster.attr('outputGeometry')
        for geo in output_geo.outputs():
            if geo not in meshes:
                meshes.add(geo)
                
    return meshes
    
    
def get_hik_joints(character_node):
    """Returns a set containing all the joints used by a character"""
    
    global _ACTIVE_CHARACTER_NODE
    _ACTIVE_CHARACTER_NODE = character_node
    
    joints = []
    for key in HIK_ATTRS:
        joint = _get_input_joint(key)
        if joint:
            joints.append(joint)
            
    return set(joints)



#def get_character_root_nodes(character_node):
    #"""Return a list of all the top level transforms that should be exported
    
    #Inspect the joints that make up character node definition and find all
    #the top level transform nodes in the scene that need to be exported to an
    #FBX. This will consist of the root of any skinned meshes, joint
    #hierarchies, as well as extra objects included in custom user data.
    #"""
    #skinned_meshes = get_skinned_meshes(character_node)
    #roots = get_joint_roots(character_node)
    
    #for skinned_mesh in skinned_meshes:
        #skin_root = get_root_parent(skinned_mesh)
        #roots.add(skin_root)
        
    #return roots



def get_spine_joints(character_node):
    """returns a list of (spine_name, joint) that define the HIK spine"""
    
    spine_joints = []
    spine_names = ['Spine', 'Spine1', 'Spine2', 'Spine3', 'Spine4', 'Spine5',
                  'Spine6', 'Spine7', 'Spine8', 'Spine9']
    
    for spine_name in spine_names:
        attr = character_node.attr(spine_name)
        inputs = attr.inputs()
        if not inputs:
            return spine_joints
        else:
            spine_joints.append((spine_name, inputs[0]))
            
    return spine_joints
        


def export_qrig_file(character_node, user_data):
    """Exports the character definition to a qrig file"""
    global _ACTIVE_CHARACTER_NODE
    
    _ACTIVE_CHARACTER_NODE = character_node
    result = get_qrig_struct(user_data)
    
    result_string = json.dumps(result, indent=4)
    
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'hik_to_.qrigcasc')
    print(file_path)
    f = open(file_path, "w")
    f.write(result_string)
    f.close()


def export(user_data, character_node = None):
    """Exports an FBX file and optional qrig file"""
    
    joints = set()
    meshes = set()
    skin_clusters = set()
    transforms = set()
    selection_sets = set()

    #organize our exportExtra nodes into types
    for node in user_data.exportExtras.inputs():
        if isinstance(node, pm.nodetypes.Joint):
            joints.add(node)
        elif isinstance(node, pm.nodetypes.Mesh):
            meshes.add(node)
        elif isinstance(node, pm.nodetypes.SelectionSet):
            selection_sets.add(node)
        elif isinstance(node, pm.nodetypes.SkinCluster):
            skin_clusters.add(node)
        else:
            transforms.add(node)   
            
    #We need to combine all joints and skinned meshes into a set of
    #skin_clusters, which can then be used to build a complete list
    #of joints and meshes that need exporting.
    if character_node:
        hik_joints = get_hik_joints(character_node)
        joints.update(hik_joints)
        
    mesh_clusters = get_mesh_skin_clusters(meshes)
    skin_clusters.update(mesh_clusters)
    
    joint_skin_clusters = get_joint_skin_clusters(joints)
    skin_clusters.update(joint_skin_clusters)
    
    skinned_joints = get_skin_cluster_joints(skin_clusters)
    joints.update(skinned_joints)
    
    skinned_meshes = get_skin_cluster_meshes(skin_clusters)
    meshes.update(skinned_meshes)
    
    root_transforms = set()
    add_transform_roots(joints, root_transforms)
    add_transform_roots(meshes, root_transforms)
    add_transform_roots(transforms, root_transforms)

    user_selection = pm.ls(sl=True)
    pm.select(list(root_transforms), replace=True)
    
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'maya_to_casc.fbx')
    print('FBX location {}'.format(file_path))
    
    cg3dguru.animation.fbx.export(filename = file_path)
    
    pm.select(user_selection, replace=True)
    
    export_qrig_file(character_node, user_data)
    



def run():
    cg3dguru.user_data.editor.run('cg3dmaya.cascadeur.core')
    #character_definitions = pm.ls(type='HIKCharacterNode')
    #for character_node in character_definitions:
        #write_qrig_file(character_node)

    