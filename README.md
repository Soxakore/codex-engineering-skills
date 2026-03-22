# King of Codex Skills

Battle-tested Codex skills for real work.

This repository packages reusable Codex skills in a clean GitHub-friendly format so they can be:

- published and shared
- installed into a local Codex setup
- validated before release
- expanded over time without turning into a messy one-off dump

## Featured Skill

### `verified-operator`

Operate across live systems with verification, receipts, recovery, and state tracking.

Best for tasks where Codex needs to do more than explain:

- coordinate terminals, files, APIs, browsers, devices, or external services
- make bounded changes and verify each one with evidence
- recover from drift or partial failure
- leave a trustworthy summary instead of a hand-wavy “should be fixed”

Skill files live at [skills/verified-operator](/Users/ibe/Documents/NemoCodex/king-of-codex-skills/skills/verified-operator).

## Repo Layout

```text
king-of-codex-skills/
├── skills/
│   └── verified-operator/
│       ├── SKILL.md
│       ├── agents/
│       ├── templates/
│       └── examples/
├── scripts/
│   ├── install.sh
│   └── validate.sh
├── CONTRIBUTING.md
├── LICENSE
├── NOTICE
└── README.md
```

## Quick Start

Install the packaged skills into your local Codex setup:

```bash
git clone https://github.com/<your-username>/king-of-codex-skills.git
cd king-of-codex-skills
bash ./scripts/install.sh
```

By default, skills are installed into:

```text
${CODEX_HOME:-$HOME/.codex}/skills
```

## Validate Skills

Before publishing changes, run:

```bash
bash ./scripts/validate.sh
```

This uses Codex's local validator if it exists on the machine.

## Publish To GitHub

This repo is already initialized locally, so the publish flow is:

```bash
cd /Users/ibe/Documents/NemoCodex/king-of-codex-skills
git add .
git commit -m "Initial release: verified-operator skill under Apache-2.0"
gh repo create king-of-codex-skills --public --source=. --remote=origin --push
```

If you want it private first, replace `--public` with `--private`.

## Suggested GitHub Metadata

These work well when you create the repo:

- Description:
  `Battle-tested Codex skills for verified operations, live-system execution, and safer agent workflows.`
- Topics:
  `codex`, `openai`, `skills`, `ai-agents`, `automation`, `developer-tools`

## Adding More Skills

Add each skill under:

```text
skills/<skill-name>/
```

A good skill package usually includes:

- `SKILL.md`
- `agents/` for display metadata
- `templates/` for repeatable task scaffolds
- `examples/` for realistic usage patterns

Keep each skill self-contained so people can inspect or copy it without hunting through the whole repo.

## Contributing

See [CONTRIBUTING.md](/Users/ibe/Documents/NemoCodex/king-of-codex-skills/CONTRIBUTING.md) for contribution guidelines.

## License

This repository is licensed under Apache 2.0. See [LICENSE](/Users/ibe/Documents/NemoCodex/king-of-codex-skills/LICENSE).
