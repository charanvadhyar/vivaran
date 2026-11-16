"""Build a bpy scene from a declarative spec, and animate it per frame.

A scene spec is data, not code — it names parts and sets params/transforms,
so it is editable at every level: change a part's params, its placement, its
motion, the camera, the engine, without touching Python.

spec = {
  "engine": "WORKBENCH" | "EEVEE" | "CYCLES",
  "resolution": [w, h], "fps": 30, "frames": 60,
  "samples": 16,                         # cycles/eevee only
  "world": [r, g, b],
  "camera": {"dist": 6, "elev": 55, "azim": 35, "orbit_deg": 0},
  "objects": [
     {"id": "g1", "part": "gear", "params": {"teeth": 12},
      "location": [-1.05, 0, 0], "rotation_deg": [0,0,0],
      "spin_dps": 90, "spin_phase": 0}     # degrees/sec about local Z
  ]
}
"""
import bpy, math
from mathutils import Vector
import parts

ENGINES = {
    "WORKBENCH": "BLENDER_WORKBENCH",
    "EEVEE": "BLENDER_EEVEE_NEXT",
    "CYCLES": "CYCLES",
}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build(spec):
    reset()
    objs = []
    for o in spec.get("objects", []):
        ob = parts.build(o["part"], o.get("params"))
        ob.name = o.get("id", ob.name)
        loc = o.get("location", [0, 0, 0])
        ob.location = (ob.location[0] + loc[0], ob.location[1] + loc[1],
                       ob.location[2] + loc[2])
        rot = o.get("rotation_deg", [0, 0, 0])
        ob.rotation_euler = tuple(math.radians(a) for a in rot)
        ob["_base_rot"] = list(ob.rotation_euler)
        ob["_spin_dps"] = o.get("spin_dps", 0)
        ob["_spin_phase"] = o.get("spin_phase", 0)
        objs.append(ob)
    # camera
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    # key light
    light = bpy.data.lights.new("sun", "SUN")
    light.energy = 4.0
    lo = bpy.data.objects.new("sun", light)
    bpy.context.collection.objects.link(lo)
    lo.rotation_euler = (math.radians(50), math.radians(10), math.radians(60))
    # world / engine / resolution
    sc = bpy.context.scene
    sc.render.engine = ENGINES.get(spec.get("engine", "WORKBENCH"),
                                   "BLENDER_WORKBENCH")
    if sc.render.engine == "BLENDER_WORKBENCH":
        sc.display.shading.light = "STUDIO"
        sc.display.shading.show_cavity = True
    elif sc.render.engine == "CYCLES":
        sc.cycles.samples = spec.get("samples", 16)
    w, h = spec.get("resolution", [1280, 720])
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.image_settings.file_format = "PNG"
    sc.world = bpy.data.worlds.new("w")
    sc.world.color = tuple(spec.get("world", [0.11, 0.12, 0.14]))
    return objs, cam


def pose(spec, objs, cam, frame):
    """Deterministic pose for a given frame: object spin + camera orbit."""
    fps = spec.get("fps", 30)
    total = spec.get("frames", 60)
    t = frame / fps
    for ob in objs:
        base = ob["_base_rot"]
        spin = math.radians(ob["_spin_dps"] * t + ob["_spin_phase"])
        ob.rotation_euler = (base[0], base[1], base[2] + spin)
    c = spec.get("camera", {})
    dist = c.get("dist", 6)
    elev = math.radians(c.get("elev", 55))
    azim = math.radians(c.get("azim", 35) + c.get("orbit_deg", 0) * (frame / max(total, 1)))
    loc = (dist * math.cos(elev) * math.cos(azim),
           dist * math.cos(elev) * math.sin(azim),
           dist * math.sin(elev))
    cam.location = loc
    cam.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
