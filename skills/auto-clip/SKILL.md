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

检查依赖是否安装：
```bash
pip install -r skills/auto-clip/server/requirements.txt
```

同时确保系统已安装 ffmpeg：
```bash
ffmpeg -version
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

调用 `whisper_transcribe.py`，输出段落级文本和时间戳：

```bash
python skills/auto-clip/server/whisper_transcribe.py \
  "./input/<FILENAME>" \
  --model medium \
  --language zh
```

**参数说明：**
- `--model`：模型大小，推荐 `medium`（速度/精度平衡）；纯英文可用 `base`
- `--language`：语言代码，中文 `zh`，英文 `en`，不确定则省略（自动检测）

**示例输出（截取）：**
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 3.2,
      "text": "好，那个，今天我们来聊聊",
      "words": [
        {"word": "好", "start": 0.0, "end": 0.3, "probability": 0.98},
        {"word": "那个", "start": 0.4, "end": 0.8, "probability": 0.91},
        {"word": "今天", "start": 1.1, "end": 1.5, "probability": 0.99}
      ]
    },
    {
      "start": 3.2,
      "end": 7.8,
      "text": "就是说，内容创作这件事情",
      "words": [...]
    }
  ],
  "language": "zh",
  "duration": 187.4
}
```

将转录结果保存供分析使用。

---

## Step 4：分析转录，识别删除片段

将转录的 segments 格式化为如下形式供分析：

```
[0.000 → 3.200] 好，那个，今天我们来聊聊
[3.200 → 7.800] 就是说，内容创作这件事情
[7.800 → 12.400] 嗯，其实我觉得吧，就是
[12.400 → 18.600] 核心在于你得先找到自己的表达方式
...
```

**分析 Prompt（Claude 自行执行此分析）：**

你是一位专业的口播视频剪辑师。以下是视频转录文本（格式：[开始 → 结束] 文本）。

请识别所有需要**删除**的片段，包括：

1. **独立填充词**：单独出现的"嗯"、"啊"、"那个"、"就是说"、"然后"等，不携带实质信息
2. **重复表达**：同一意思说了两遍，保留更清晰的那次，删除另一次
3. **自我纠正前的错误部分**：说错后说"不对"/"我是说"/"让我重新说"之前的内容
4. **无意义铺垫**：超过 10 字的纯铺垫（"好了，那个，下面我们来说一下……"→ 仅保留核心内容）
5. **逻辑跑偏**：明显跑题、与主题无关的闲聊段落

**保守原则：**
- 优先保留内容完整性，宁少删勿误删
- 单次删除不超过视频总时长的 30%
- 不拆分句子中间（必须在句子边界切割）
- 切割点选在 segment 的 start/end，不要使用 word 级时间戳（除非该 word 恰好是句子开头/结尾）

**输出严格 JSON：**
```json
{
  "cuts": [
    {"start": 0.4, "end": 0.8, "reason": "填充词：那个"},
    {"start": 3.2, "end": 4.6, "reason": "填充词：就是说"},
    {"start": 7.8, "end": 12.4, "reason": "重复表达，与后面 18.6s 的内容重复"}
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

## Step 7：输出剪辑报告

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

视频主题：内容创作方法论
输出文件：./output/demo_clipped.mp4
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

---

## 目录结构

```
<用户项目目录>/       ← Claude Code 运行目录
├── ./input/          # 放置原始视频
└── ./output/         # 精剪结果输出

skills/auto-clip/     ← Skill 所在位置（固定）
├── SKILL.md
└── server/
    ├── whisper_transcribe.py
    ├── ffmpeg_cut.py
    └── requirements.txt
```
