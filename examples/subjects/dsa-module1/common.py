"""Small helpers for writing scene scripts: a title line and a bottom takeaway that
remember whether they are on screen, so the right action (write or replace) is used."""
import json


class Script:
    def __init__(self, title):
        self.title = title
        self.objects = [
            {"id": "head", "type": "text", "region": "title", "text": " "},
            {"id": "takeaway", "type": "text", "region": "bottom", "text": " "},
        ]
        self.scenes = []
        self._shown = {"head": False, "takeaway": False}

    def obj(self, o):
        self.objects.append(o)

    def scene(self, id):
        self.scenes.append({"id": id, "steps": []})

    def step(self, say, do=()):
        out = []
        for a in do:
            out.extend(a if isinstance(a, list) else [a])
        st = {"say": {"en": say}}
        if out:
            st["do"] = out
        self.scenes[-1]["steps"].append(st)

    def _text(self, id, t):
        if self._shown[id]:
            return {"action": "replace", "target": id, "text": t}
        self._shown[id] = True
        return [{"action": "write", "target": id}, {"action": "replace", "target": id, "text": t}]

    def head(self, t):
        return self._text("head", t)

    def take(self, t):
        return self._text("takeaway", t)

    def unhead(self):
        if not self._shown["head"]:
            return []
        self._shown["head"] = False
        return {"action": "hide", "target": "head"}

    def untake(self):
        if not self._shown["takeaway"]:
            return []
        self._shown["takeaway"] = False
        return {"action": "hide", "target": "takeaway"}

    def save(self, path):
        script = {"version": 1, "title": self.title,
                  "canvas": {"width": 1920, "height": 1080, "fps": 30, "theme": "dark"},
                  "objects": self.objects, "scenes": self.scenes}
        json.dump(script, open(path, "w"), ensure_ascii=False, indent=1)
        steps = [st for sc in self.scenes for st in sc["steps"]]
        secs = sum(max(1.5, len(st["say"]["en"]) / 16) + 0.35 for st in steps)
        print(f"{len(steps)} steps, estimate {secs / 60:.1f} min, likely {secs * 1.26 / 60:.1f} min with Gnani")
