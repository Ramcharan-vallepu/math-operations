# .coznt/

This directory is managed by the coznt CLI. Files here:

- **config.json** — connection metadata (server URL, project ID, API-key reference). Safe to commit; never holds the plaintext key.
- **skills/** — workflow choreographies pulled by `coznt sync`. Committed by design so teammates get them on `git pull`. Each skill has a `SKILL.md` (the workflow guide your AI editor consumes) and a `.lock` (per-skill content hash for drift detection).
- **.local/** — per-developer cache. Gitignored.

Refresh with `coznt sync`. Re-bootstrap with `coznt connect`.

See [docs/operate/cli.md](../docs/operate/cli.md) for the full reference.
