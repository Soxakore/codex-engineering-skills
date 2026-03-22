# Contributing

Thanks for contributing to King of Codex Skills.

## Goal

Keep the repo small, useful, and easy to trust.

That means each skill should be:

- focused on a clear class of work
- practical in a real Codex environment
- validated locally before publishing
- self-contained enough to understand without hidden dependencies

## Skill Structure

Each skill should live in:

```text
skills/<skill-name>/
```

Recommended contents:

- `SKILL.md`
- `agents/openai.yaml` when a display name or default prompt helps
- `templates/` for reusable task scaffolds
- `examples/` for realistic usage

## Before Opening a PR

1. Add or update the skill files.
2. Run:

```bash
bash ./scripts/validate.sh
```

3. Make sure examples do not expose secrets, tokens, webhook URLs, or private identifiers.
4. Keep docs concise and action-oriented.

## Style

- Prefer practical instructions over theory.
- Prefer realistic examples over toy examples.
- Redact secrets in examples.
- Avoid environment-specific assumptions unless the skill is explicitly platform-specific.

## Pull Request Notes

A good PR description should say:

- what skill was added or changed
- why it is useful
- how it was validated
- any limitations or environment assumptions
