import pymel.core as pm
import cg3dguru.utils as gutils

class ShapeCloner():
    @staticmethod
    def _move_shapes():
        result = pm.confirmDialog(title='Shape Cloner', message='Move Shape(s) to joint(s)?', messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', dismissString='No')
        return result == 'Yes'
    
    
    @staticmethod
    def _get_temp_transforms(transform_list):
        temp_transforms = pm.duplicate(transform_list)
        pm.parent(temp_transforms, world=True, absolute=True)
        pm.makeIdentity(temp_transforms, apply=True, translate=False, rotate=True, scale=True)
        
        return temp_transforms
        
    
    @staticmethod
    def _shapes_to_ctrl(transform_set, ctrl_set, only_match=False, move_shapes=None, bake=True):
        transform_list = list(transform_set)
        
        if bake:
            pm.select(transform_list)
            pm.mel.eval('BakeCustomPivot')

        ctrl = list(ctrl_set)[0]
        temp_transforms = ShapeCloner._get_temp_transforms(transform_list)
        shapes = pm.listRelatives(temp_transforms, shapes=True)
        
        if move_shapes is None:
            move_shapes = ShapeCloner._move_shapes()
        
        if not move_shapes:
            ctrl_matrix = gutils.MatrixUtils.get_world_matrix(ctrl)
            for i in temp_transforms:
                temp_matrix = gutils.MatrixUtils.get_world_matrix(i)
                adjusted_matrix = temp_matrix * ctrl_matrix.inverse()
                gutils.MatrixUtils.set_world_matrix(i, adjusted_matrix, no_scale=True)
                
            pm.makeIdentity(temp_transforms, apply=True, translate=True, rotate=True, scale=True)
            
        else:
            #TODO:Eventually make the shapes align to the user defined foward and up vects.
            pass
        
        if only_match:
            for transform in temp_transforms:
                gutils.MatrixUtils.set_world_matrix(transform,
                                                   gutils.MatrixUtils.get_world_matrix(ctrl), no_scale=True)
        else:
            for shape in shapes:
                if not shape.type() == 'nurbsCurve':
                    continue
                
                pm.parent(shape, ctrl, relative=True, shape=True)
    
            pm.delete(temp_transforms)
                

    @staticmethod
    def _shape_to_ctrls(transform_set, ctrl_set, only_match=False, bake=True):
        ctrls = list(ctrl_set)
        transform_list = list(transform_set)
        if bake:
            pm.select(transform_list)
            pm.mel.eval('BakeCustomPivot')

        for ctrl in ctrls:
            #This should be a list with one element
            temp_transforms = ShapeCloner._get_temp_transforms(transform_list)
            shapes = pm.listRelatives(temp_transforms, shapes=True)

            #TODO:Eventually make the shapes align to the user defined foward and up vects.
            #where we assume Z=forward and Y=Up

            if only_match:
                gutils.MatrixUtils.set_world_matrix(temp_transforms[0],
                                                   gutils.MatrixUtils.get_world_matrix(ctrl), no_scale=True)
            else:
                for shape in shapes:
                    if not shape.type() == 'nurbsCurve':
                        continue
                    
                    pm.parent(shape, ctrl, relative=True, shape=True)
        
                pm.delete(temp_transforms)
        
    
    @staticmethod
    def _shapes_to_ctrls(transform_set, ctrl_set):
        #The size of the two lists is assumed to match
        
        #the only_match command doesn't make sense in this context
        #since the shapes have to already be in place to do joint trasnform matching.

        #Let's match each joint to the closest transform
        ctrls = list(ctrl_set)
        transforms = list(transform_set)
        pairing = []
        
        pm.select(transforms)
        pm.mel.eval('BakeCustomPivot')
        
        for transform in transforms:
            t_pos = gutils.MatrixUtils.get_world_pos(transform)
            j_pos = gutils.MatrixUtils.get_world_pos(ctrls[0])

            distance = t_pos.distanceTo(j_pos)
            closest_ctrl = ctrls[0]

            for ctrl in ctrls:
                j_pos = gutils.MatrixUtils.get_world_pos(ctrl)
                current_distance = t_pos.distanceTo(j_pos)
                
                if current_distance < distance:
                    distance = current_distance
                    closest_ctrl = ctrl

            pairing.append((transform, closest_ctrl))
            #we might have mutlipel shapes attaching to one joint, so let's not
            #reduce our list.
            #ctrls.pop(ctrls.index(closest_ctrl))

        #now that things are paired up we can
        for transform, ctrl in pairing:
            ShapeCloner._shapes_to_ctrl([transform], [ctrl], only_match=False, move_shapes=False, bake=False)
            
        

    @staticmethod
    def run(only_match=False):
        selected_ctrls = pm.ls(sl=True, type=['joint', 'ikHandle'])
        selected_transforms = pm.ls(sl=True, et='transform')

        #empty groups and locators needs to be found and added
        #to the ctrls set
        ctrl_transforms = set()
        for i in selected_transforms:
            shapes = pm.listRelatives(i, shapes=True)
            if not shapes:
                ctrl_transforms.add(i)
            elif len(shapes) == 1 and shapes[0].type() == 'locator':
                ctrl_transforms.add(i)
                #pm.delete(shapes[0])

        ctrl_set = set(selected_ctrls)
        ctrl_set.update(ctrl_transforms)
        
        transform_set = set(selected_transforms)
        transform_set.difference_update(ctrl_set)

        if not ctrl_set:
            pm.error("Not joint(s) (or other controls) found in selection!")

        if not transform_set:
            pm.error("No transform(s) found in selection!")

        if len(ctrl_set) == 1:
            ShapeCloner._shapes_to_ctrl(transform_set, ctrl_set, only_match=only_match)

        elif len(transform_set) == 1:
            ShapeCloner._shape_to_ctrls(transform_set, ctrl_set, only_match=only_match)

        #we don't need this condition now that we don't pop the ctrls as they're
        #paired with a transform.
        #elif len(transform_set) <= len(ctrl_set):
        else:
            ShapeCloner._shapes_to_ctrls(transform_set, ctrl_set)

        #else:
            #pm.error("Can't resolve transform and ctrl counts.")
            

        
        
        
def run():
    ShapeCloner.run()
