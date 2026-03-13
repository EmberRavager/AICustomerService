#!/usr/bin/env bash
set -e

OUT=~/Desktop/ai_hot_30s.mp4
FONT="/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
WORKDIR="${HOME}/Desktop/ai_hot_frames"

mkdir -p "${WORKDIR}"

make_frame() {
  local file="$1"
  local text="$2"
  local size="$3"

  magick -size 1080x1920 xc:black \
    -fill "rgba(139,0,0,0.12)" -draw "rectangle 0,0 1080,1920" \
    -fill "rgba(255,68,68,0.5)" -font "${FONT}" -pointsize 140 -gravity north -annotate +0+80 "BREAKING" \
    -fill white -font "${FONT}" -pointsize "${size}" -gravity center -annotate +0-200 "${text}" \
    "${file}"
}

make_frame "${WORKDIR}/1.png" "AI 圈刚刚发生\n地动山摇级大事！" 90
make_frame "${WORKDIR}/2.png" "某巨头突然发布更强新模型\n行业洗牌！" 70
make_frame "${WORKDIR}/3.png" "这不是更新\n是规则重写！" 90
make_frame "${WORKDIR}/4.png" "旧方案可能被淘汰\n价格和体验都要变！" 70
make_frame "${WORKDIR}/5.png" "未来 48 小时\n是关键窗口" 90
make_frame "${WORKDIR}/6.png" "想第一时间看懂影响\n记得关注！" 80

cat > "${WORKDIR}/concat.txt" <<EOF
file '${WORKDIR}/1.png'
duration 3
file '${WORKDIR}/2.png'
duration 4
file '${WORKDIR}/3.png'
duration 5
file '${WORKDIR}/4.png'
duration 6
file '${WORKDIR}/5.png'
duration 5
file '${WORKDIR}/6.png'
duration 7
file '${WORKDIR}/6.png'
EOF

"/usr/local/bin/ffmpeg" -y -f concat -safe 0 -i "${WORKDIR}/concat.txt" \
  -r 30 -c:v libx264 -pix_fmt yuv420p -t 30 "${OUT}"

echo "OK -> ${OUT}"
