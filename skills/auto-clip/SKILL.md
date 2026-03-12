---
name: auto-clip
description: 自动口播视频精剪工具。给定视频源文件，自动转录、分析逻辑结构、删除冗余片段（填充词、重复表达、自我纠正等），输出精剪版本。当用户说"帮我剪视频"、"auto clip"、"精剪口播"、"删掉废话"、"视频剪辑"时触发。
---

# Auto Clip — 口播视频自动精剪

**工作流总览：**
```
./input/ → whisper_transcribe.py → Claude 分析 → ffmpeg_cut.py → ./output/
```

---

## 环境准备（首次使用）

**Step 0：检查依赖**

运行一键检查：
```bash
python skills/auto-clip/server/ffmpeg_cut.py check
```

期望输出：
```
ffmpeg:  /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
ffprobe: /opt/homebrew/opt/ffmpeg-full/bin/ffprobe
  filter 'subtitles': OK
  filter 'drawtext': OK
  filter 'ass': OK
```

如果 filter 显示 MISSING，说明 ffmpeg 缺少 libass（字幕烧录必需）。修复方式：
```bash
brew install ffmpeg-full
```
脚本会自动优先使用 `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`。

安装 Python 依赖：
```bash
pip install -r skills/auto-clip/server/requirements.txt
```

---

## Step 1：确认输入文件

检查当前目录的 input 文件夹：
```bash
ls ./input/
```

- 如果目录不存在或为空，提示用户将视频文件放入 `./input/`
- 如果有多个文件，询问用户处理哪一个
- 支持格式：mp4 / mov / avi / mkv / m4v

---

## Step 2：探测视频信息

用 `ffmpeg_cut.py probe` 获取视频基本信息：

```bash
python skills/auto-clip/server/ffmpeg_cut.py probe \
  --input "./input/<FILENAME>"
```

**示例输出：**
```json
{
  "duration": 187.4,
  "size_bytes": 284672000,
  "video": {
    "codec": "h264",
    "width": 1920,
    "height": 1080
  }
}
```

记录 `duration`（总时长），后续计算 keep_segments 需要用到。

---

## Step 3：语音转录

调用 `whisper_transcribe.py`，默认输出紧凑行内格式（compact），token 消耗比 JSON 少约 77%，同时保留 word 级时间戳：

```bash
python skills/auto-clip/server/whisper_transcribe.py \
  "./input/<FILENAME>" \
  --model medium \
  --language zh \
  --format compact > ./output/transcribe/<FILENAME_WITHOUT_EXT>_subtitle.compact
```

转录结果保存到 `./output/transcribe/<FILENAME_WITHOUT_EXT>_subtitle.compact`，后续字幕步骤会复用此文件。

**参数说明：**
- `--model`：模型大小，推荐 `medium`（速度/精度平衡）；纯英文可用 `base`
- `--language`：语言代码，中文 `zh`，英文 `en`，不确定则省略（自动检测）
- `--format compact`：默认，紧凑格式，供 Claude 分析用；`--format json` 仅调试时使用

**输出格式说明（compact）：**
```
# 第1行：语言|总时长
zh|187.40
# 后续每行：段落开始|段落结束|词(词开始,词结束) 词(词开始,词结束) ...
0.00|3.20|好(0.00,0.30) 那个(0.40,0.80) 今天(1.10,1.50) 我们来聊聊(1.50,3.20)
3.20|7.80|就是说(3.20,3.80) 内容创作(3.80,5.20) 这件事情(5.20,7.80)
7.80|12.40|嗯(7.80,8.10) 其实(8.20,8.60) 我觉得吧(8.70,9.30) 就是(9.40,9.70)
12.40|18.60|核心在于(12.40,13.80) 你得先找到(13.80,15.20) 自己的(15.20,16.00) 表达方式(16.00,18.60)
```

- 每个词后括号内为 `(开始秒, 结束秒)`，精度 0.01s
- 若某段无 word 时间戳，显示为 `start|end|[完整文本]`

将转录结果保存供分析使用。

---

## Step 4：分析转录，识别删除片段

直接将 Step 3 的 compact 格式输出传入分析，无需再次转换。

**格式解读（分析前先确认）：**
- 每行：`段落开始|段落结束|词(词开始,词结束) ...`
- 可用 word 级时间戳做精准切割（如只删段落内某个填充词）
- 也可用段落的 start/end 做整段切割

**分析 Prompt（Claude 自行执行此分析）：**

你是一位专业的口播视频剪辑师。以下是视频转录（compact 格式）：

格式说明：每行 `段开始|段结束|词(词起,词止) ...`，括号内为该词的精确时间戳（秒）。

请识别所有需要**删除**的片段，包括：

1. **独立填充词**：段落内孤立的"嗯"、"啊"、"那个"、"就是说"、"然后"等词，用 word 级时间戳精确切除，不影响前后内容
2. **重复表达**：同一意思说了两遍，保留更清晰的那次，删整段
3. **自我纠正前的错误部分**：说错后说"不对"/"我是说"/"让我重新说"之前的内容
4. **无意义铺垫**：纯铺垫短语，用 word 级时间戳精确切除开头铺垫，保留后续核心
5. **逻辑跑偏**：明显跑题、与主题无关的闲聊段落

**切割粒度：**
- **优先 word 级切割**：对段落内的填充词、铺垫词，直接用 word 的 `(start, end)` 定位，精准切除单个词或短语
- **整段切割**：对整段重复/跑偏内容，使用段落的 start/end

**保守原则：**
- 优先保留内容完整性，宁少删勿误删
- 单次删除不超过视频总时长的 30%
- 切割点必须落在词边界，不得在词中间切断

**输出严格 JSON：**
```json
{
  "cuts": [
    {"start": 0.40, "end": 0.80, "reason": "填充词：那个（word级精确切除）"},
    {"start": 3.20, "end": 3.80, "reason": "填充词：就是说（word级精确切除）"},
    {"start": 7.80, "end": 12.40, "reason": "重复表达，与后面 18.6s 的内容重复（整段切除）"}
  ],
  "summary": "视频主题：内容创作方法论，讲解如何找到个人表达方式",
  "estimated_removal_ratio": 0.12
}
```

---

## Step 5：计算 keep_segments

根据 cuts 列表和视频总时长，计算需要**保留**的区间（cuts 的补集）：

**示例：**
- 视频总时长：187.4s
- cuts：`[{0.4, 0.8}, {3.2, 4.6}, {7.8, 12.4}]`
- keep_segments：
  ```json
  [
    {"start": 0.0,  "end": 0.4},
    {"start": 0.8,  "end": 3.2},
    {"start": 4.6,  "end": 7.8},
    {"start": 12.4, "end": 187.4}
  ]
  ```

注意：起点为 0.0，终点为视频 duration。

---

## Step 6：执行剪辑

调用 `ffmpeg_cut.py cut`：

```bash
python skills/auto-clip/server/ffmpeg_cut.py cut \
  --input "./input/<FILENAME>" \
  --keep '[{"start":0.0,"end":0.4},{"start":0.8,"end":3.2},...]' \
  --output "./output/<FILENAME_WITHOUT_EXT>_clipped.mp4"
```

**示例输出：**
```json
{
  "output_path": "./output/demo_clipped.mp4",
  "segments_kept": 4,
  "kept_duration_seconds": 164.8,
  "output_size_bytes": 248123456
}
```

---

## Step 7：烧录字幕

将转录文本以字幕形式烧录到剪辑后的视频中。时间戳自动根据 cuts 重映射，对应已删除的片段会从字幕中跳过。

```bash
python skills/auto-clip/server/ffmpeg_cut.py subtitle \
  --input "./output/<FILENAME_WITHOUT_EXT>_clipped.mp4" \
  --transcript ./output/transcribe/<FILENAME_WITHOUT_EXT>_subtitle.compact \
  --cuts '[{"start":0.4,"end":0.8},{"start":3.2,"end":3.8},...]' \
  --output "./output/<FILENAME_WITHOUT_EXT>_final.mp4"
```

**参数说明：**
- `--input`：Step 6 输出的剪辑视频
- `--transcript`：Step 3 保存的 `./output/transcribe/<FILENAME_WITHOUT_EXT>_subtitle.compact`
- `--cuts`：Step 4 分析得到的 cuts 数组（与 Step 6 计算 keep_segments 时所用的相同）
- `--output`：带字幕的最终视频

**示例输出：**
```json
{
  "output_path": "./output/demo_final.mp4",
  "subtitle_count": 42,
  "output_size_bytes": 251456789
}
```

**字幕样式：** 白色文字 + 黑色描边，底部居中，字号 12，字间距 1.5，每行最多 12 字符（超出自动换行）。字幕文本自动去除空格。音频流直接复制（不重新编码），仅视频层重编。

---

## Step 8：输出剪辑报告

完成后向用户汇报：

```
剪辑完成！

原始时长：187.4 秒（3分07秒）
剪辑后：  164.8 秒（2分44秒）
删除片段：8 处，共 22.6 秒（12%）

删除内容分类：
  - 填充词：5 处
  - 重复表达：2 处
  - 无意义铺垫：1 处

字幕：42 条，已烧录至画面底部

视频主题：内容创作方法论
最终文件：./output/demo_final.mp4
```

---

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| `ModuleNotFoundError: faster_whisper` | 运行 `pip install -r skills/auto-clip/server/requirements.txt` |
| `ffmpeg not found` | macOS: `brew install ffmpeg`，Linux: `apt install ffmpeg` |
| 转录结果为空 | 检查视频是否有音轨：`ffprobe -i <file>` |
| FFmpeg 剪辑失败 | 检查磁盘空间和 `./output/` 目录是否存在 |
| 转录语言识别错误 | 手动指定 `--language zh` 或 `--language en` |
| `subtitle error: No such filter: subtitles` | 系统 ffmpeg 缺少 libass：`brew install ffmpeg-full`，脚本会自动检测并使用 |
| 字幕乱码/方块字 | 系统缺少对应字体；macOS 通常正常；Linux 需安装 `fonts-noto-cjk` |
| `./output/transcribe/<FILENAME_WITHOUT_EXT>_subtitle.compact not found` | Step 3 忘记加 `> ./output/transcribe/<FILENAME_WITHOUT_EXT>_subtitle.compact` 重定向输出 |

---

## 目录结构

```
<用户项目目录>/       ← Claude Code 运行目录
├── ./input/          # 放置原始视频
└── ./output/         # 精剪结果输出
    └── ./transcribe/ # 转录字幕文件

skills/auto-clip/     ← Skill 所在位置（固定）
├── SKILL.md
└── server/
    ├── whisper_transcribe.py
    ├── ffmpeg_cut.py
    └── requirements.txt
```
