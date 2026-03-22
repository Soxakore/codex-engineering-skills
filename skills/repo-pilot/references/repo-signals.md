# Repo Signals

Use this file when the repo is unfamiliar and you need to infer stack, commands, or scope quickly.

## Stack Signals

| Signal | Likely Ecosystem | First Commands To Inspect |
|---|---|---|
| `package.json` | Node / frontend / backend JS | `npm test`, `npm run lint`, `npm run build` |
| `pnpm-lock.yaml` | pnpm workspace or app | `pnpm test`, `pnpm lint`, `pnpm -r test` |
| `yarn.lock` | Yarn app or monorepo | `yarn test`, `yarn lint` |
| `turbo.json` | Turborepo | `turbo run test`, package-local scripts |
| `nx.json` | Nx monorepo | `nx test <project>`, `nx graph` patterns |
| `pyproject.toml` | Python app / library | `pytest`, `ruff check`, `mypy` |
| `poetry.lock` | Poetry-managed Python | `poetry run pytest`, `poetry run ruff check` |
| `requirements.txt` | Python app | `pytest`, project-specific scripts |
| `go.mod` | Go module | `go test ./...`, package-local `go test ./pkg/...` |
| `Cargo.toml` | Rust crate / workspace | `cargo test`, `cargo fmt --check`, `cargo clippy` |
| `Gemfile` | Ruby app | `bundle exec rspec`, `bundle exec rubocop` |
| `pom.xml` | Maven Java | `mvn test`, module-local test goals |
| `build.gradle` | Gradle Java / Kotlin | `./gradlew test`, module-local tasks |

## Monorepo Signals

Treat the repo as multi-surface when you see:

- `pnpm-workspace.yaml`
- `turbo.json`
- `nx.json`
- `rush.json`
- `lerna.json`
- multiple top-level apps or packages

In monorepos:

1. find the owning package first
2. prefer package-local commands before workspace-wide commands
3. avoid broad formatting or dependency churn unless requested

## Fast Ownership Clues

Start near:

- the file named in the request
- failing test paths
- stack traces
- route names, component names, handler names, or command names from the bug report
- nearest config or schema file tied to the behavior

Then expand to:

- imports and callers
- adjacent tests
- framework registration points

## Verification Selection

Choose the cheapest useful proof that matches the change:

- parser / formatter / type-only changes:
  run lint, typecheck, or compile on the touched package or file scope
- pure logic changes:
  run the nearest unit tests first
- API or handler changes:
  run focused integration tests or a targeted request path
- UI changes:
  run local render/build checks and a narrow browser proof when available
- config or wiring changes:
  verify the affected startup path, route, job, or command directly

## Dirty Worktree Rules

When the repo is already dirty:

- inspect the status before editing
- avoid reverting or reformatting unrelated files
- keep your change set isolated
- mention any nearby user changes that may affect confidence

## Escalation Signals

Pause and reconsider before editing when you notice:

- migrations or schema rewrites
- auth or permissions code
- shared low-level utilities used widely across the repo
- framework version or build-tool churn
- many failing tests unrelated to the request
- missing local setup needed for even narrow verification
