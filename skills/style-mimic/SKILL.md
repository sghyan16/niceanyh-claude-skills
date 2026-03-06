---
name: style-mimic
description: "Analyzes writing style from reference text and creates new content matching that style. Use when users want to: (1) Mimic a specific author's writing style, (2) Create content with consistent brand voice, (3) Transform ideas into styled articles, or (4) Generate personal content matching an established writing pattern. Triggered by requests like '模仿这篇文章', 'write in the style of', 'match this writing style', or 'create content using this tone'."
---

# Style Mimic

Systematically analyze writing style from reference text and generate new content that matches the identified stylistic patterns.

## Workflow

### Step 1: Choose Analysis Mode

Ask the user to choose:
- **Option A**: Use a pre-saved style analysis from `references/` directory
- **Option B**: Analyze new reference text

If Option A, list available saved styles in `references/` directory (e.g., "李盆风格.md") and load the selected one.

If Option B, proceed to receive reference text.

### Step 1B: Receive Reference Text (if Option B chosen)

Ask the user to provide the reference text for style analysis. Accept:
- Direct text paste
- File path to read
- URL to fetch

### Step 2: Conduct Style Analysis (if Option B chosen)

Load the comprehensive analysis framework:

```bash
Read references/style-analysis-framework.md
```

Analyze the reference text across all dimensions in the framework:
- 句法结构 (Syntax structure)
- 词汇特征 (Vocabulary features)
- 修辞手法 (Rhetorical devices)
- 语气与情感 (Tone and emotion)
- 段落与结构 (Paragraph and structure)
- 节奏与韵律 (Rhythm and cadence)
- 文化与语境 (Cultural context)
- 特殊标志 (Unique markers)

Output the analysis in Markdown format following the structure in the framework. Focus on:
1. **Core characteristics** (3-5 most prominent features)
2. **Detailed dimension-by-dimension breakdown**
3. **Overall style summary**

**Optional**: If the user wants to save this analysis for future use, save it to `references/[StyleName].md` with a descriptive name.

### Step 3: Receive Source Content

(This step applies whether using a saved style or newly analyzed style)

Ask the user to provide:
- The idea/content to be transformed
- Any specific requirements (length, structure, focus)

### Step 4: Generate Styled Content

Apply the analyzed style patterns to create new content:

1. **Match sentence patterns**: Replicate length distribution, complexity, and punctuation style
2. **Mirror vocabulary choices**: Use similar formality level, specificity, and word variety
3. **Adopt rhetorical devices**: Incorporate the same types of metaphors, parallelism, or other figures of speech
4. **Maintain tone and emotion**: Match the emotional baseline, intensity, and perspective
5. **Follow structural patterns**: Use similar paragraph organization and transition methods
6. **Preserve rhythm**: Maintain the pacing and flow characteristics
7. **Include cultural markers**: Reference similar cultural touchpoints if appropriate
8. **Replicate signature elements**: Incorporate unique opening/closing patterns or recurring phrases

Output the generated content in Markdown format **without explanatory commentary** - deliver only the styled content itself.

## Key Principles

- **Comprehensive analysis**: Cover all eight dimensions from the framework, not just surface features
- **Pattern recognition**: Identify recurring patterns rather than one-off occurrences
- **Authentic replication**: Aim for natural style matching, not mechanical mimicry
- **Content integrity**: Transform the style while preserving the core message and information
- **Clean output**: The final content should stand alone without meta-commentary

## Notes

- The analysis phase can be verbose and detailed (for reference)
- The generation phase should produce only the final styled content
- For long reference texts, identify the most consistent patterns
- For varied reference texts, note and account for intentional style shifts
- **Saved styles**: Pre-analyzed styles are stored in `references/` directory and can be reused without re-analysis
- When saving a new style analysis, use a descriptive name that identifies the author or style characteristics
