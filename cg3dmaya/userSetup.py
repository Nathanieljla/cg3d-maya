import maya.cmds as cmds
import maya.utils



def make_guru_menu():
    print("building guru Menu!")
    from cg3dguru.utils import menu_maker
    menu_maker.run(menu_namespace = 'cg3dmaya.menu')

maya.utils.executeDeferred(make_guru_menu)



