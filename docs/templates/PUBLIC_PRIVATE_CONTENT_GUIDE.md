# Public / Private Content Guide

This project is public-facing, so content should be separated carefully.

## Public-safe content

Put public-safe content in:

```text
data/questions.json
data/formulas.json
```

Suitable content:

- standard interview questions
- public textbook-level formulas
- general coding questions
- public-safe examples
- non-sensitive notes

## Private or research-sensitive content

Keep private content in a folder such as:

```text
private/
```

Examples:

- unpublished PhD research details
- supervisor discussions
- private datasets
- draft paper ideas
- confidential methods
- non-public notes

## Gitignore recommendation

Add this to `.gitignore`:

```text
private/
*.local.json
research_private/
```

## Practical rule

When unsure, keep the content private first. Move it into the public app only after reviewing it.
