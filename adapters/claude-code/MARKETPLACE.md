# QC 4.1 Light — Claude Code marketplace

Install this package as a Claude Code plugin / skill so agents diagnose sales-call transcripts with the Light contract.

## Option A — Plugin marketplace (recommended)

From a clone of this repo (or after publishing to GitHub):

```text
/plugin marketplace add mgallmur-glitch/qc41-light
/plugin install qc41-light@qc41-light
```

Marketplace manifest: [`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json)  
Plugin manifest: [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json)

The plugin ships a skill at `skills/qc41-light/` that points Claude at the repo-root `SKILL.md`, prompt, and schema.

## Option B — Manual skill / project instructions

1. Copy or symlink this repository into your project (or clone it nearby).
2. Merge [`CLAUDE.md`](./CLAUDE.md) into your project `CLAUDE.md`, **or** copy the skill folder:

```bash
mkdir -p .claude/skills
cp -R adapters/claude-code/skills/qc41-light .claude/skills/
```

3. Ask Claude Code:

```text
Analyze this call with QC 4.1 Light. Return only schema-valid JSON.
```

4. Validate:

```bash
python3 scripts/validate_report.py qc41-light-report.json
```

## Option C — MCP server

```bash
npm install
# In Claude Code MCP settings, add a stdio server:
#   command: node
#   args: ["path/to/qc41-light/bin/qc41-light.js", "mcp"]
# Put ANTHROPIC_API_KEY or OPENAI_API_KEY in the MCP server environment (BYOK — never commit keys).
```

Tools exposed: `analyze_sales_call`, `get_qc41_light_prompt`, `get_schema`.
