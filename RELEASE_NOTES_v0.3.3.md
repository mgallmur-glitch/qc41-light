# QC 4.1 Light v0.3.3

Launch-gap closure release. Schema contract remains `qc41-light-0.2`.

## Fixed
- Package / skill / Claude marketplace / plugin / MCP / CONTRIBUTING / SECURITY aligned at `0.3.3`
- MCP server version reads from `package.json`
- `__pycache__` excluded from npm tarball (`prepack` + `.npmignore`)

## Ops
- GitHub topics + homepage set
- `main` ruleset: block deletion/force-push; CI required on PRs; admin bypass for maintainer
- `publish-npm.yml` workflow on release (needs `NPM_TOKEN` secret once)

## Install
```bash
hermes skills install --yes https://raw.githubusercontent.com/mgallmur-glitch/qc41-light/v0.3.3/SKILL.md
```
