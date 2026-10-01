"""Experimental scene helpers retained without import-time side effects."""

from maya import cmds
from maya.api import OpenMaya as om


def link_joints():
    selection = cmds.ls(selection=True, type="joint", long=True) or []
    for joint in selection:
        short_name = joint.rsplit("|", 1)[-1]
        epic_joint = "epic:{}".format(short_name)
        if not cmds.objExists(epic_joint):
            continue

        source = om.MVector(*cmds.getAttr(joint + ".translate")[0])
        target = om.MVector(*cmds.getAttr(epic_joint + ".translate")[0])
        delta = target - source
        add_node = cmds.createNode("plusMinusAverage")
        cmds.connectAttr(joint + ".translate", add_node + ".input3D[0]")
        cmds.setAttr(
            add_node + ".input3D[1]", delta.x, delta.y, delta.z, type="double3"
        )
        cmds.connectAttr(add_node + ".output3D", epic_joint + ".translate")
        cmds.connectAttr(joint + ".rotate", epic_joint + ".rotate")


def run():
    selection = cmds.ls(selection=True, long=True) or []
    if len(selection) != 2:
        cmds.warning("Please select a joint and constraint")
        return

    joints = cmds.ls(selection=True, type="joint", long=True) or []
    if len(joints) != 1:
        cmds.warning("Can't find one joint in the selection")
        return

    joint = joints[0]
    constraint = next(node for node in selection if node != joint)
    rig_root = "Rig:root"
    if not cmds.objExists(rig_root):
        cmds.warning("Can't find Rig:root")
        return

    cmds.setAttr(rig_root + ".TopSimWeight", 0.0)
    cmds.setAttr(rig_root + ".BottomSimWeight", 0.0)
    p1 = om.MVector(*cmds.xform(joint, query=True, translation=True, worldSpace=True))

    cmds.setAttr(rig_root + ".TopSimWeight", 1.0)
    cmds.setAttr(rig_root + ".BottomSimWeight", 1.0)
    cmds.pointConstraint(constraint, edit=True, offset=(0, 0, 0))
    p2 = om.MVector(*cmds.xform(joint, query=True, translation=True, worldSpace=True))
    delta = p1 - p2
    cmds.pointConstraint(
        constraint, edit=True, offset=(delta.x, delta.y, delta.z)
    )


if __name__ == "__main__":
    run()
