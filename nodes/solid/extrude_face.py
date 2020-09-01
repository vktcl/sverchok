# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE

import numpy as np

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty

from sverchok.node_tree import SverchCustomTreeNode, throttled
from sverchok.data_structure import zip_long_repeat, ensure_nesting_level, updateNode
from sverchok.utils.nurbs_common import SvNurbsMaths
from sverchok.utils.curve.core import SvCurve
from sverchok.utils.surface.core import SvSurface
from sverchok.utils.curve.freecad import SvFreeCadCurve, SvFreeCadNurbsCurve, curves_to_wire
from sverchok.utils.surface.freecad import SvSolidFaceSurface, curves_to_face, surface_to_freecad, is_solid_face_surface
from sverchok.utils.curve.nurbs import SvNurbsCurve
from sverchok.utils.dummy_nodes import add_dummy

from sverchok.dependencies import FreeCAD

if FreeCAD is None:
    add_dummy('SvSolidFaceExtrudeNode', 'Extrude Face (Solid)', 'FreeCAD')
else:
    import Part
    from FreeCAD import Base

class SvSolidFaceExtrudeNode(bpy.types.Node, SverchCustomTreeNode):
    """
    Triggers: Extrude Solid Face
    Tooltip: Make a Solid by extruding one face
    """
    bl_idname = 'SvSolidFaceExtrudeNode'
    bl_label = 'Extrude Face (Solid)'
    bl_icon = 'EDGESEL'
    solid_catergory = "Operators"

    refine_solid: BoolProperty(
            name="Refine Solid",
            description="Removes redundant edges (may slow the process)",
            default=False,
            update=updateNode)

    def sv_init(self, context):
        self.inputs.new('SvSurfaceSocket', "SolidFace")
        p = self.inputs.new('SvVerticesSocket', "Vector")
        p.use_prop = True
        p.prop = (0.0, 0.0, 1.0)
        self.outputs.new('SvSolidSocket', "Solid")
        self.update_sockets(context)

    def process(self):
        if not any(socket.is_linked for socket in self.outputs):
            return

        face_surfaces_s = self.inputs['SolidFace'].sv_get()
        face_surfaces_s = ensure_nesting_level(face_surfaces_s, 2, data_types=(SvSurface,))
        offset_s = self.inputs['Vector'].sv_get()
        offset_s = ensure_nesting_level(offset_s, 3)

        solids_out = []
        for face_surfaces, offsets in zip_long_repeat(face_surfaces_s, offset_s):
            #new_solids = []
            for face_surface, offset in zip_long_repeat(face_surfaces, offsets):
                if not is_solid_face_surface(face_surface):
                    # face_surface is an instance of SvSurface,
                    # but not a instance of SvFreeCadNurbsSurface
                    self.info("Surface %s is not a face of a solid, will convert automatically", face_surface)
                    face_surface = surface_to_freecad(face_surface, make_face=True) # SvFreeCadNurbsSurface

                fc_face = face_surface.face
                fc_offset = Base.Vector(*offset)
                shape = fc_face.extrude(fc_offset)
                solids_out.append(shape)
            #solids_out.append(new_solids)

        self.outputs['Solid'].sv_set(solids_out)

def register():
    if FreeCAD is not None:
        bpy.utils.register_class(SvSolidFaceExtrudeNode)

def unregister():
    if FreeCAD is not None:
        bpy.utils.unregister_class(SvSolidFaceExtrudeNode)
