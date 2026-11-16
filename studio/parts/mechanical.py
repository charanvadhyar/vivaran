"""Mechanical bucket — parametric part generators.

Every generator is PURE GEOMETRY: it builds a mesh object and returns it.
No camera, no lights, no render settings — those belong to the scene, so a
part can be dropped into any scene, any shot, any engine. Fixed params in →
fixed mesh out (deterministic). This is the 3D analogue of the 2D shape
vocabulary: a `gear` is make_gear(teeth, ...), not a frozen model.
"""
import bpy, bmesh, math


def _grey(name, rgb=(0.55, 0.57, 0.60)):
    m = bpy.data.materials.new(name)
    m.use_nodes = False
    m.diffuse_color = (*rgb, 1.0)
    return m


def make_gear(teeth=12, r_pitch=1.0, tooth_h=0.18, thickness=0.35,
              bore=0.32, name="gear", color=(0.55, 0.57, 0.60)):
    """Spur gear. Sockets: `axis` = the bore centre line (+Z).
    States are driven by the scene timeline (rotation), not baked here."""
    assert teeth >= 4, "a gear needs at least 4 teeth"
    r_root, r_tip = r_pitch - tooth_h * 0.5, r_pitch + tooth_h * 0.5
    tp = 2 * math.pi / teeth
    half_tip = tp * 0.5 / 2.0
    outline = []
    for i in range(teeth):
        c = i * tp
        for ang, r in [(c - tp / 2, r_root), (c - half_tip, r_root),
                       (c - half_tip, r_tip), (c + half_tip, r_tip),
                       (c + half_tip, r_root)]:
            outline.append((r * math.cos(ang), r * math.sin(ang)))
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0.0)) for (x, y) in outline]
    bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    top = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, thickness))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.location = (0, 0, -thickness / 2)
    # bore
    bpy.ops.mesh.primitive_cylinder_add(radius=bore, depth=thickness * 3,
                                        vertices=48, location=(0, 0, 0))
    cyl = bpy.context.active_object
    mod = ob.modifiers.new("bore", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cyl
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="bore")
    bpy.data.objects.remove(cyl, do_unlink=True)
    ob.data.materials.append(_grey(name + "_mat", color))
    # verify the generator agrees with the request (structure gate)
    assert len(ob.data.vertices) > teeth * 2
    ob["part"] = "gear"
    ob["teeth"] = teeth
    return ob
