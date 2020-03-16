# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#  
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE

import bpy
import numpy as np
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode

class SvVectorAccumulate(bpy.types.Node, SverchCustomTreeNode):
    
    """
    Triggers: SvVectorAccumulate
    Tooltip: 
    
    A short description for reader of node code
    """

    bl_idname = 'SvVectorAccumulate'
    bl_label = 'Vector Accumulate'
    bl_icon = 'GREASEPENCIL'

    as_numpy: bpy.props.BoolProperty(
        description="output as numpy",
        name="np", default=True, update=updateNode) 
    prepend_zero_vec: bpy.props.BoolProperty(
        description="prepend a zero vec",
        name="Prepend Null", default=True, update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvVerticesSocket", 'Vectors')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "as_numpy")
        row.separator()
        row.prop(self, "prepend_zero_vec")

    def process(self):
        if not self.inputs[0].is_linked:
            return
        vectors_in = self.inputs['Vectors'].sv_get(deepcopy=False)
        if not vectors_in:
            return

        ...




classes = [SvVectorAccumulate]
register, unregister = bpy.utils.register_classes_factory(classes)
