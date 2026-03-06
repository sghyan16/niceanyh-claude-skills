---
name: product-feasibility
description: Systematic product feasibility analysis framework to evaluate product ideas, validate user needs, and avoid "self-indulgent innovation" (自嗨型创新). Use when users need to analyze new product concepts, validate market opportunities, assess user demand authenticity, design MVP experiments, or create comprehensive feasibility reports. Triggered by requests like "产品可行性分析", "analyze this product idea", "validate market demand", "需求验证", "MVP设计", or "feasibility study".
---

# 产品可行性分析 (Product Feasibility Analysis)

## Overview

This skill provides a systematic framework for conducting product feasibility analysis from scratch. It helps evaluate product ideas through structured analysis of user needs, market potential, competitive landscape, and MVP validation—ensuring decisions are data-driven rather than based on assumptions.

**Core principle**: Validate product concepts through multiple perspectives (user research, market data, competitive analysis, MVP testing) to avoid building products nobody wants.

## Workflow: Full Product Feasibility Analysis

When users want to analyze a new product idea, guide them through this four-phase process:

### Phase 1: Pre-Analysis (前期洞察)

**Objective**: Screen ideas and understand market context

**Key Activities**:
1. **Identify driving force**: Market Pull (user demand-driven) vs Technology Push (technology-driven)
2. **Apply Demand Triangle Model** (需求三角模型): Validate three elements
   - 缺乏感 (Pain): Does the user have a real pain point?
   - 目标物 (Solution): Does the product actually solve it?
   - 能力 (Ability): Can users afford it (money, time, learning cost)?
3. **Define user value & positioning**: Who are target users? What core value does the product provide?
4. **Conduct preliminary competitive & market analysis**: Understand competitive landscape
5. **Estimate resources & expected outcomes**: Rough ROI assessment

**Key Questions**:
- "Why do target users need this product? Is there real scenario support?"
- "What are users' current solutions? What pain points remain unsatisfied?"
- "How do existing competitors position themselves? What's our differentiation?"
- "Can current technology support core functions? How long to develop?"

**Reference**: For detailed methodology on this phase, see [methodology.md](references/methodology.md) Section 1.

**Frameworks**: See [frameworks.md](references/frameworks.md) for Demand Triangle Model template, SWOT analysis template, and competitive comparison matrix.

### Phase 2: Deep Research (深入调研)

**Objective**: Validate demand authenticity through user research

**Key Activities**:
1. **User research**: Conduct interviews, surveys, observations
   - Use the **interview guide template** in [assets/interview-guide.md](assets/interview-guide.md)
   - Apply Google Ventures 5-step interview method
   - Create empathy maps and user journey maps
2. **Demand validation**: Verify through multiple methods
   - Landing page tests
   - Questionnaire surveys
   - **KANO Model analysis**: Classify features (Basic/Performance/Excitement/Indifferent/Reverse)
3. **User value assessment**: Use Value Proposition Canvas to match user pains/gains with product features
4. **Deeper competitive & market research**: User reviews, industry reports, trend analysis

**User Interview Framework** (5 parts):
1. Opening (5 min): Build trust, explain purpose
2. Background (10 min): Understand user context
3. Pain point exploration (15 min): Deep dive into problems
4. Demand validation (10 min): Test product concept
5. Closing (5 min): Thank and follow-up

**Reference**: For detailed research methods and validation techniques, see [methodology.md](references/methodology.md) Section 2.

**Templates**:
- Interview guide: [assets/interview-guide.md](assets/interview-guide.md)
- KANO model, Value Proposition Canvas: [frameworks.md](references/frameworks.md) Sections 2 & 3

### Phase 3: Rapid Validation (快速验证)

**Objective**: Test core hypotheses with MVP (Minimum Viable Product)

**Key Activities**:
1. **Define MVP scope**: Use "addition then subtraction" method
   - List all possible features
   - Prioritize by user value vs. implementation difficulty
   - Select minimal feature set that solves core pain point
2. **Choose validation method**:
   - Online: A/B testing, gray release, analytics tracking
   - Offline: Usability testing, user observation
   - Other: Paper prototypes, video demos, Wizard of Oz
3. **Evaluate results**: Measure against pre-set success criteria
   - User behavior metrics: Activation rate, retention rate, feature usage
   - Satisfaction metrics: User satisfaction score, NPS
   - Business metrics: Registration conversion, payment conversion, ARPU

**MVP Feature Prioritization Matrix**:
```
High   │ 💎 Priority      │ ⭐ Quick Win
Value  │ Do First         │ Implement Fast
       │                  │
       ├──────────────────┼──────────────────
Low    │ 📋 Backlog       │ ❌ Don't Do
Value  │ Plan Later       │ Skip
       │                  │
       └──────────────────┴──────────────────
         High Difficulty     Low Difficulty
```

**Success criteria example**: "Among 100 target users, at least 30 willing to pay" or "Feature usage rate reaches X%"

**Reference**: For MVP design principles and validation methods, see [methodology.md](references/methodology.md) Section 3.

**Templates**: MVP function evaluation table and metrics framework in [frameworks.md](references/frameworks.md) Sections 5 & 7.

### Phase 4: Decision & Review (决策与团队评审)

**Objective**: Create comprehensive report and make go/no-go decision

**Key Activities**:
1. **Compile feasibility report**: Use the structured template
   - Product background, user research results
   - Market & competitive analysis
   - MVP testing data
   - Resource investment & ROI estimation
   - Risk assessment
2. **Team review**: Multi-stakeholder discussion (product, tech, operations, business, management)
3. **Final decision**: Go / No-Go / Further validation needed
4. **Avoid "self-indulgent innovation"**: Ensure all decisions backed by data and user feedback

**Feasibility Report Structure**:
- Executive Summary
- Demand Analysis (Demand Triangle validation)
- Market Analysis (TAM/SAM/SOM, growth trends)
- Competitive Analysis (SWOT, differentiation)
- Product Solution (positioning, MVP design)
- MVP Validation Results (key metrics, user feedback)
- Technical Assessment
- Resource Planning (team, timeline, budget)
- Business Model (revenue model, cost structure, ROI)
- Risk Assessment
- Conclusion & Recommendations

**Decision Matrix** (Go/No-Go):
- **≥4.0/5.0**: Strongly recommend execution
- **3.0-4.0**: Recommend with risk control
- **2.0-3.0**: Needs improvement, proceed cautiously
- **<2.0**: Not recommended

**Reference**: For report structure and decision frameworks, see [methodology.md](references/methodology.md) Section 4.

**Template**: Complete feasibility report template: [assets/feasibility-report-template.md](assets/feasibility-report-template.md)

## Core Analysis Frameworks

This skill leverages several proven frameworks. Detailed templates and usage guides are in [frameworks.md](references/frameworks.md):

1. **Demand Triangle Model** (需求三角模型): Validate demand authenticity through Pain-Solution-Ability
2. **KANO Model**: Classify features into Basic/Performance/Excitement/Indifferent/Reverse
3. **Value Proposition Canvas**: Match user pains/gains with product features
4. **SWOT Analysis**: Analyze Strengths/Weaknesses/Opportunities/Threats
5. **MVP Validation Framework**: Lean startup approach with priority matrix
6. **User Interview Framework**: Google Ventures 5-step method
7. **Metrics Framework**: Acquisition, Activation, Retention, Revenue, Referral metrics

## Usage Guidelines

### For complete analysis from scratch:
1. Start with Phase 1 (Pre-Analysis) to understand the idea and context
2. Guide user through each phase sequentially
3. Use templates and frameworks from references/ and assets/
4. Generate structured report using feasibility-report-template.md

### For specific analysis steps:
- **User interviews**: Use [assets/interview-guide.md](assets/interview-guide.md)
- **Demand validation**: Apply Demand Triangle or KANO from [frameworks.md](references/frameworks.md)
- **MVP design**: Use priority matrix and metrics from [frameworks.md](references/frameworks.md)
- **Competitive analysis**: Use SWOT template from [frameworks.md](references/frameworks.md)

### For writing reports:
- Use the comprehensive template: [assets/feasibility-report-template.md](assets/feasibility-report-template.md)
- Fill in sections based on completed analysis
- Include data, charts, and evidence throughout

## Key Principles

1. **Data-Driven**: Base all decisions on real data, not intuition
2. **User-Centric**: Validate from user perspective, not self-assumption
3. **Multi-Angle Validation**: Verify through interviews, surveys, data, competitive analysis
4. **MVP Testing**: Validate value through actual product testing
5. **Team Review**: Involve multiple stakeholders to avoid individual bias

## Warning Signs of "Self-Indulgent Innovation"

- "I think users should need..."
- "This feature is cool, people will definitely use it"
- "We don't need research, I understand users"
- Starting large-scale development without real user feedback

## References

**Detailed methodology**: [methodology.md](references/methodology.md) - Complete methodology guide with all frameworks, methods, and best practices

**Framework templates**: [frameworks.md](references/frameworks.md) - All analysis frameworks, templates, matrices, and tools

**Interview guide**: [assets/interview-guide.md](assets/interview-guide.md) - Complete user interview template with questions and techniques

**Report template**: [assets/feasibility-report-template.md](assets/feasibility-report-template.md) - Comprehensive feasibility report structure

## Workflow Adaptation

The four-phase workflow can be adapted based on user needs:

- **Need guidance on specific steps**: Jump to relevant phase
- **Already have some research**: Start from validation phase
- **Just need report writing**: Use report template directly
- **Want complete analysis**: Follow full four-phase workflow

Always begin by understanding where the user is in their analysis journey and provide contextually appropriate guidance.
