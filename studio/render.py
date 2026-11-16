"""Render a scene spec to an mp4. bpy writes PNG frames (this bpy build has no
ffmpeg writer), imageio-ffmpeg encodes them, optionally muxing a voice track.
"""
import bpy, os, tempfile, subprocess, time, json, sys
import imageio_ffmpeg
import scene


def render_job(spec, out_path, audio_path=None, workdir=None):
    t0 = time.time()
    objs, cam = scene.build(spec)
    frames = spec.get("frames", 60)
    fps = spec.get("fps", 30)
    tmp = workdir or tempfile.mkdtemp(prefix="studio_")
    sc = bpy.context.scene
    for f in range(frames):
        scene.pose(spec, objs, cam, f)
        sc.render.filepath = os.path.join(tmp, f"frame_{f:05d}.png")
        bpy.ops.render.render(write_still=True)
    render_s = time.time() - t0

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg, "-y", "-framerate", str(fps),
           "-i", os.path.join(tmp, "frame_%05d.png")]
    if audio_path and os.path.exists(audio_path):
        cmd += ["-i", audio_path]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"]
    if audio_path and os.path.exists(audio_path):
        cmd += ["-c:a", "aac", "-shortest"]
    cmd += [out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    total_s = time.time() - t0
    return {"out": out_path, "frames": frames, "render_seconds": round(render_s, 1),
            "total_seconds": round(total_s, 1), "fps": fps,
            "objects": len(objs), "engine": sc.render.engine}


if __name__ == "__main__":
    # CLI test: python -m studio.render <spec.json> <out.mp4> [audio.wav]
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else "out.mp4"
    aud = sys.argv[3] if len(sys.argv) > 3 else None
    print(json.dumps(render_job(spec, out, aud), indent=2))
