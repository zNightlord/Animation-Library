bl_info = {
    "name": "Animation Library",
    "description": "Animation Library based on the Asset Browser.",
    "author": "Arjhi P. Moscosa",
    "version": (1, 0),
    "blender": (3, 2, 0),
    "warning": "In heavily development, things may change",
    "location": "Asset Browser -> Animations, and 3D Viewport -> Animation panel",
    "support": "OFFICIAL",
    "category": "Animation",
}

import inspect
from typing import Optional, FrozenSet, Set, Union, Iterable, cast
import bpy
from bpy import [
        Action,
        Operator
]

class CreateAnimationAsset(Operator):
    bl_idname = "pose.create_animation_asset"
    bl_label = "Create Animation Asset"
    bl_description = (
        "Creates an Action that contains the selected keyframes of the selected bones, marks it as an asset"
    )
    bl_options = {"REGISTER", "UNDO"} 


    @classmethod
    def poll(cls, context: Operator) -> bool:
        return context.active_object is not None

    def execute(self, context: Operator) -> Set[str]:
        new_action = bpy.data.actions.new("Asset")
        src_action = context.object.animation_data.action
        bone_names = {bone.name for bone in bpy.context.selected_pose_bones_from_active_object}
        for bone_name in sorted(bone_names):
            for location_index in range(3):
                bone = bpy.context.object.pose.bones[bone_name]
                rna_path = bone.path_from_id("location")
                new_fcurve = new_action.fcurves.find(rna_path, index=location_index)
                if new_fcurve is None:
                    new_fcurve = new_action.fcurves.new(rna_path, index=location_index, action_group=bone_name)
                src_fcurve = src_action.fcurves.find(rna_path, index=location_index)
                for keyframe in src_fcurve.keyframe_points:
                    new_fcurve.keyframe_points.insert(frame=keyframe.co.x, value=keyframe.co.y)
                
                new_action.asset_mark()
                new_action.asset_generate_preview()
        
        return {'FINISHED'}


class ApplyAnimationAsset(Operator):
    bl_idname = "pose.apply_animation_asset"
    bl_label = "Apply Animation Asset"
    bl_description = (
        "Creates an Action that contains the selected keyframes of the selected bones, marks it as an asset"
    )
    bl_options = {"REGISTER", "UNDO"}

    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context) -> Set[str]:
        
        frame_current = context.scene.frame_current
        target_action = context.object.animation_data.action
        from_action = bpy.data.actions["Asset"]
        # smallest_x = min(from_action.fcurves.keyframe_points.co.x)
        bone_names = {bone.name for bone in bpy.context.selected_pose_bones_from_active_object}

        for bone_name in sorted(bone_names):
            for location_index in range(3):
                bone = bpy.context.object.pose.bones[bone_name]
                rna_path = bone.path_from_id("location")
                target_fcurve = target_action.fcurves.find(rna_path, index=location_index)
                from_fcurve = from_action.fcurves.find(rna_path, index=location_index)
                if target_fcurve is None:
                    target_fcurve = target_action.fcurves.new(rna_path, index=location_index, action_group=bone_name)
                    
                target_fcurve.update()

                for keyframe in from_fcurve.keyframe_points:
                    target_fcurve.keyframe_points.insert(frame=keyframe.co.x + frame_current, value=keyframe.co.y)
                
        # print(smallest_x)

        return {'FINISHED'}
        


def menu_func(self, context):
    self.layout.operator(CreateAnimationAsset.bl_idname, text=CreateAnimationAsset.bl_label)
    self.layout.operator(ApplyAnimationAsset.bl_idname, text=ApplyAnimationAsset.bl_label)

def register():
    bpy.utils.register_class(CreateAnimationAsset)
    bpy.utils.register_class(ApplyAnimationAsset)
    bpy.types.VIEW3D_MT_pose.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CreateAnimationAsset)
    bpy.utils.unregister_class(ApplyAnimationAsset)
    bpy.types.VIEW3D_MT_pose.remove(menu_func)

if __name__ == "__main__":
    register()
