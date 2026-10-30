"""Render a Vivaran Studio scene with Blender's Cycles.

    blender -b -P render.py -- <dir with scene.glb and timeline.json> [options]
    python render.py -- <dir> [options]        (with the `bpy` module from PyPI)

Options:
    --out <dir>           where frames go (default <dir>/frames)
    --frames <list>       e.g. 1,48,120 or 1-90 (default: all); frames count from 1
    --samples <n>         override the scene's samples
    --scale <percent>     resolution scale, for quick previews (default 100)
    --device auto|cpu|gpu (default auto: the GPU when Blender finds one)
    --no-blur             turn motion blur off
    --save-blend <file>   also save the set-up scene, for inspection

Reads the two files `cevg studio build` writes: scene.glb holds geometry,
materials and the node tree; timeline.json is the authority on time
(transforms, opacity, glow, camera, lights, background, render settings).
Frames are written as frame_0001.png ... and `cevg studio finish` adds
callouts, captions and the watermark and encodes the video.
"""

import json
import math
import os
import sys
import time

import bpy


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv:
        sys.exit("usage: blender -b -P render.py -- <build dir> [--out dir] [--frames 1-90] [--samples n] [--scale pct] [--device auto|cpu|gpu]")
    opts = {"dir": argv[0], "out": None, "frames": None, "samples": None, "scale": 100, "device": "auto", "blur": True, "save_blend": None}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("--out", "--frames", "--samples", "--scale", "--device", "--save-blend"):
            if i + 1 >= len(argv):
                sys.exit(f"{a} needs a value")
            key = a[2:].replace("-", "_")
            opts[key] = argv[i + 1]
            i += 2
        elif a == "--no-blur":
            opts["blur"] = False
            i += 1
        else:
            sys.exit(f"unknown option {a}")
    return opts


def frame_list(spec, total):
    if not spec:
        return list(range(1, total + 1))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [f for f in out if 1 <= f <= total]


def _fcurves(id_data):
    """The F-curve collection of an ID's action: through its slot on Blender
    4.4 and later (layered actions), directly on older versions."""
    ad = id_data.animation_data
    try:
        from bpy_extras import anim_utils
        bag = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        if bag is not None:
            return bag.fcurves
    except (ImportError, AttributeError):
        pass
    return ad.action.fcurves


def fcurve_keys(id_data, path, index, frames, values, interpolation="LINEAR"):
    """Key a property at many frames quickly. Frames count from 0 in the
    timeline and from 1 in Blender. The first key goes in through
    keyframe_insert, which sets up the action (and its slot) the way the
    running Blender version expects; the rest are written in one go."""
    if not frames:
        return
    id_data.keyframe_insert(data_path=path, index=index, frame=frames[0] + 1)
    fcs = _fcurves(id_data)
    targets = [fc for fc in fcs if fc.data_path == path and (index < 0 or fc.array_index == index)]
    for fc in targets:
        n = len(frames)
        fc.keyframe_points.add(n - len(fc.keyframe_points))
        co = []
        for f, v in zip(frames, values):
            co.extend((f + 1, float(v)))
        fc.keyframe_points.foreach_set("co", co)
        code = {"CONSTANT": 0, "LINEAR": 1, "BEZIER": 2}[interpolation]
        fc.keyframe_points.foreach_set("interpolation", [code] * n)
        fc.update()


def principled(material):
    if material is None or not material.use_nodes:
        return None
    for node in material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    return None


def socket(node, *names):
    for name in names:
        if name in node.inputs:
            return node.inputs[name]
    return None


def socket_path(node, sock):
    index = list(node.inputs).index(sock)
    return f'nodes["{node.name}"].inputs[{index}].default_value'


# How strongly a glowing part takes on its glow colour: full tint is
# reached at this emission strength (a highlight is 0.3), and at most this
# much of the paint is replaced.
TINT_AT = 0.3
TINT_MAX = 0.9


def tint_toward(mat, bsdf, spec, strength, color):
    tree = mat.node_tree
    base = socket(bsdf, "Base Color")
    mix = tree.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MIX"
    by_id = {i.identifier: i for i in mix.inputs}
    fac, a, b = by_id["Factor_Float"], by_id["A_Color"], by_id["B_Color"]
    out = next(o for o in mix.outputs if o.identifier == "Result_Color")
    if base.is_linked:
        tree.links.new(base.links[0].from_socket, a)
    else:
        a.default_value = tuple(base.default_value)
    tree.links.new(out, base)
    frames, values = strength["frames"], strength["values"]
    fcurve_keys(tree, socket_path(mix, fac), -1, frames, [min(1.0, v[0] / TINT_AT) * TINT_MAX for v in values])
    if color is not None:
        for k in range(3):
            fcurve_keys(tree, socket_path(mix, b), k, color["frames"], [v[k] for v in color["values"]])
    else:
        b.default_value = (*spec.get("emission", [1.0, 1.0, 1.0])[:3], 1.0)


def setup_device(choice):
    prefs = bpy.context.preferences.addons["cycles"].preferences
    scene = bpy.context.scene
    if choice == "cpu":
        scene.cycles.device = "CPU"
        return "CPU"
    for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
        except TypeError:
            continue
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == kind]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == kind
            scene.cycles.device = "GPU"
            return f"{kind}: {', '.join(d.name for d in gpus)}"
    if choice == "gpu":
        sys.exit("no GPU found for Cycles; use --device cpu")
    scene.cycles.device = "CPU"
    return "CPU"


def main():
    opts = parse_args()
    build = os.path.abspath(opts["dir"])
    with open(os.path.join(build, "timeline.json"), encoding="utf-8") as fh:
        tl = json.load(fh)
    out = os.path.abspath(opts["out"] or os.path.join(build, "frames"))
    os.makedirs(out, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=os.path.join(build, "scene.glb"))

    # The timeline drives everything: drop what the importer animated or added.
    for ob in list(bpy.data.objects):
        if ob.type in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(ob, do_unlink=True)
        elif ob.animation_data:
            ob.animation_data_clear()
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)

    objects = {ob.name: ob for ob in bpy.data.objects}
    missing = [n["name"] for n in tl["nodes"] if n["name"] not in objects]
    if missing:
        print(f"warning: {len(missing)} node(s) not found after import, e.g. {missing[:3]}")

    # The rest pose, exactly as the timeline has it.
    for n in tl["nodes"]:
        ob = objects.get(n["name"])
        if ob is None:
            continue
        ob.rotation_mode = "QUATERNION"
        ob.location = n["translation"]
        ob.rotation_quaternion = n["rotation"]
        ob.scale = n["scale"]

    materials = {m["name"]: m for m in tl["materials"]}
    tracks = {}
    for t in tl["tracks"]:
        tracks.setdefault(t["node"], []).append(t)

    def own_material(ob, node):
        """A copy of the node's material for this object alone, so its opacity
        and glow can change without changing its siblings."""
        if not ob.material_slots:
            return None
        slot = ob.material_slots[0]
        if slot.link != "OBJECT":
            base = slot.material
            slot.link = "OBJECT"
            slot.material = base.copy() if base else None
        return slot.material

    node_info = {n["name"]: n for n in tl["nodes"]}
    for name, ts in tracks.items():
        ob = objects.get(name)
        if ob is None:
            continue
        info = node_info.get(name, {})
        spec = materials.get(info.get("material"))
        for t in ts:
            frames, values = t["frames"], t["values"]
            path = t["path"]
            if path in ("translation", "rotation", "scale"):
                data_path = {"translation": "location", "rotation": "rotation_quaternion", "scale": "scale"}[path]
                for k in range(len(values[0])):
                    fcurve_keys(ob, data_path, k, frames, [v[k] for v in values])
                continue
            mat = own_material(ob, info)
            bsdf = principled(mat)
            if bsdf is None:
                continue
            tree = mat.node_tree
            if path == "opacity":
                alpha = socket(bsdf, "Alpha")
                base_opacity = spec["opacity"] if spec else 1.0
                fcurve_keys(tree, socket_path(bsdf, alpha), -1, frames, [v[0] * base_opacity for v in values])
                # Fully hidden objects are left out of the render altogether.
                fcurve_keys(ob, "hide_render", -1, frames, [1.0 if v[0] <= 0.001 else 0.0 for v in values], "CONSTANT")
                mat.blend_method = "BLEND"
            elif path == "emission_strength":
                sock = socket(bsdf, "Emission Strength")
                fcurve_keys(tree, socket_path(bsdf, sock), -1, frames, [v[0] for v in values])
            elif path == "emission_color":
                sock = socket(bsdf, "Emission Color", "Emission")
                for k in range(3):
                    fcurve_keys(tree, socket_path(bsdf, sock), k, frames, [v[k] for v in values])

        # A part with no light of its own that is made to glow (a highlight,
        # hot metal) also takes on the glow's colour. Emission alone only adds
        # light on top of the paint, so amber over blue reads as cream.
        strength = next((t for t in ts if t["path"] == "emission_strength"), None)
        if strength is not None and spec is not None and spec.get("strength", 0.0) <= 0.0:
            mat = own_material(ob, info)
            bsdf = principled(mat)
            if bsdf is not None:
                tint_toward(mat, bsdf, spec, strength, next((t for t in ts if t["path"] == "emission_color"), None))

    # Camera: vertical field of view, keyed per frame where it moves.
    cam_data = bpy.data.cameras.new("camera")
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_height = 24.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 2000.0
    cam = bpy.data.objects.new("camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.rotation_mode = "QUATERNION"
    ct = tl["camera"]
    lens = [12.0 / math.tan(math.radians(f) / 2.0) for f in ct["fov"]]
    for k in range(3):
        fcurve_keys(cam, "location", k, ct["frames"], [p[k] for p in ct["position"]])
    for k in range(4):
        fcurve_keys(cam, "rotation_quaternion", k, ct["frames"], [q[k] for q in ct["rotation"]])
    fcurve_keys(cam_data, "lens", -1, ct["frames"], lens)

    # Lights, resolved by the timeline (the environment's rig or the scene's own).
    for light in tl["lights"]:
        kind = {"area": "AREA", "point": "POINT", "spot": "SPOT", "sun": "SUN"}[light["kind"]]
        data = bpy.data.lights.new(light["id"], kind)
        data.energy = light["power"]
        data.color = light["color"]
        if kind == "AREA":
            data.shape = "SQUARE"
            data.size = light["size"]
        elif kind in ("POINT", "SPOT"):
            data.shadow_soft_size = min(light["size"], 0.5)
        ob = bpy.data.objects.new(light["id"], data)
        ob.rotation_mode = "QUATERNION"
        ob.location = light["position"]
        ob.rotation_quaternion = light["rotation"]
        scene.collection.objects.link(ob)

    # World: the camera sees the background colour; everything else (light
    # bouncing, reflections in metal and glass) sees a soft gradient that is
    # brighter overhead, the way a photo studio's walls and ceiling are.
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    wt = world.node_tree
    for node in list(wt.nodes):
        wt.nodes.remove(node)
    env = tl["environment"]
    seen = wt.nodes.new("ShaderNodeBackground")
    seen.inputs["Color"].default_value = (*env["background"], 1.0)
    coords = wt.nodes.new("ShaderNodeTexCoord")
    split = wt.nodes.new("ShaderNodeSeparateXYZ")
    to01 = wt.nodes.new("ShaderNodeMapRange")
    to01.inputs["From Min"].default_value = -1.0
    to01.inputs["From Max"].default_value = 1.0
    ramp = wt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*env.get("reflection_bottom", env["background"]), 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (*env.get("reflection_top", env["background"]), 1.0)
    studio = wt.nodes.new("ShaderNodeBackground")
    studio.inputs["Strength"].default_value = env.get("strength", 1.0)
    path = wt.nodes.new("ShaderNodeLightPath")
    mix = wt.nodes.new("ShaderNodeMixShader")
    out_node = wt.nodes.new("ShaderNodeOutputWorld")
    wt.links.new(coords.outputs["Generated"], split.inputs["Vector"])
    wt.links.new(split.outputs["Z"], to01.inputs["Value"])
    wt.links.new(to01.outputs["Result"], ramp.inputs["Fac"])
    wt.links.new(ramp.outputs["Color"], studio.inputs["Color"])
    wt.links.new(path.outputs["Is Camera Ray"], mix.inputs["Fac"])
    wt.links.new(studio.outputs["Background"], mix.inputs[1])
    wt.links.new(seen.outputs["Background"], mix.inputs[2])
    wt.links.new(mix.outputs["Shader"], out_node.inputs["Surface"])
    scene.world = world

    # Render settings.
    r = scene.render
    r.engine = "CYCLES"
    device = setup_device(opts["device"])
    r.resolution_x = tl["width"]
    r.resolution_y = tl["height"]
    r.resolution_percentage = int(opts["scale"])
    r.fps = tl["fps"]
    scene.frame_start = 1
    scene.frame_end = tl["frames"]
    scene.cycles.samples = int(opts["samples"] or tl["samples"])
    # Denoise with OptiX on NVIDIA GPUs, Open Image Denoise elsewhere; some
    # distribution builds have neither, and then frames simply need more samples.
    import _cycles
    if device.startswith("OPTIX"):
        scene.cycles.denoiser = "OPTIX"
        scene.cycles.use_denoising = True
    elif getattr(_cycles, "with_openimagedenoise", False):
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
        scene.cycles.use_denoising = True
    else:
        scene.cycles.use_denoising = False
        print("vivaran-studio: this Blender has no denoiser; expect grain at low sample counts", flush=True)
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.max_bounces = 10
    scene.cycles.transmission_bounces = 10
    scene.cycles.transparent_max_bounces = 16
    scene.view_settings.view_transform = "AgX"
    r.use_motion_blur = opts["blur"]
    r.motion_blur_shutter = 0.5
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.image_settings.color_depth = "8"

    # Glow: a soft bloom on everything brighter than white, which is what
    # makes plasma and hot filaments read as light rather than paint.
    scene.use_nodes = True
    nt = scene.node_tree
    for node in list(nt.nodes):
        nt.nodes.remove(node)
    layers = nt.nodes.new("CompositorNodeRLayers")
    glare = nt.nodes.new("CompositorNodeGlare")
    glare.glare_type = "FOG_GLOW"
    glare.quality = "HIGH"
    glare.threshold = 1.6
    glare.size = 7
    glare.mix = -0.45
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(layers.outputs["Image"], glare.inputs["Image"])
    nt.links.new(glare.outputs["Image"], comp.inputs["Image"])

    if opts["save_blend"]:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(opts["save_blend"]))

    frames = frame_list(opts["frames"], tl["frames"])
    print(f"vivaran-studio: {tl['title']!r}, {len(frames)} frame(s) of {tl['frames']}, {r.resolution_x * r.resolution_percentage // 100}x{r.resolution_y * r.resolution_percentage // 100}, {scene.cycles.samples} samples, {device}", flush=True)
    started = time.time()
    for k, f in enumerate(frames):
        scene.frame_set(f)
        r.filepath = os.path.join(out, f"frame_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        done = k + 1
        per = (time.time() - started) / done
        print(f"vivaran-studio: frame {f} ({done}/{len(frames)}), {per:.1f} s per frame", flush=True)


main()
