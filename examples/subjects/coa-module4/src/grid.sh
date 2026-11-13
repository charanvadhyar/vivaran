#!/bin/bash
# usage: grid.sh json outprefix scene:step ...
J=$1; O=$2; shift 2; C=/home/claude/cevg/target/release/cevg
rm -rf /tmp/g_$O; mkdir -p /tmp/g_$O
for ss in "$@"; do sc=${ss%:*}; n=${ss#*:}; timeout 25 $C frame $J --scene $sc --step $n --at 1 -o /tmp/g_$O/$(printf %02d $i)_$sc-$n.png >/dev/null 2>&1 || echo fail $ss; i=$((i+1)); done
python3 - "$O" <<'PY'
import sys,glob
from PIL import Image
o=sys.argv[1];fs=sorted(glob.glob(f'/tmp/g_{o}/*.png'));ims=[Image.open(f).resize((800,450)) for f in fs]
for k in range((len(ims)+5)//6):
  part=ims[k*6:(k+1)*6];g=Image.new('RGB',(1600,450*((len(part)+1)//2)))
  for i,im in enumerate(part): g.paste(im,((i%2)*800,(i//2)*450))
  g.save(f'/home/claude/playlist/m4/{o}_{k}.png')
print(len(ims))
PY
