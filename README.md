# Student 360 for Higher Education in 1 Hour (CoWork)

A condensed, one-hour version of the [full Student 360 workshop](https://github.com/sfc-gh-isuryawinata/student360_workshop). Attendees unify six siloed campus systems into one governed **Student 360**, govern it, and put AI agents on top that advisors and analysts use in **CoWork** (Snowflake Intelligence). All data is synthetic.

## Agenda (60 minutes)

| Min | Notebook | You do | Snowflake features |
|---|---|---|---|
| 0-5 | Intro | The story: six systems, six student keys | |
| 5-25 | `Express_1_Build_Student360` | Load sources, resolve identity, dynamic tables, `AI_REDACT` + `AI_CLASSIFY`, assemble `STUDENT_360` | Roles, dynamic tables (incremental), Cortex AI functions |
| 25-45 | `Express_2_Context_and_Governance` | Semantic view, search services, roles, row + column policy, prove it by switching roles, owner's-rights gotcha | Semantic views, Cortex Search, row access and masking policies, four-layer access |
| 45-58 | `Express_3_Agents_and_CoWork` | Two agents, persona tests, refusal test, tags + budget, publish to CoWork | Cortex Agents, `DATA_AGENT_RUN`, budgets, Snowflake Intelligence |
| 58-60 | `Express_4_Cleanup` | Remove everything the lab created (run when finished) | |

Measured compute time for all SQL is about 11 minutes; the rest is reading, discussion and trying the agents in CoWork.

## Run it

1. Snowsight → Projects → Workspaces → *From Git repository* → paste this repo's URL (public, no token needed).
2. Open `notebooks/` and run `Express_1` → `Express_2` → `Express_3` on the SQL kernel, and `Express_4_Cleanup` when you are done.

**Prerequisites:** `ACCOUNTADMIN`, Cortex AI features and cross-region inference allowed, Snowflake Intelligence (CoWork) enabled.

## What was cut from the full workshop

Smaller data (about 1,200 students), no tags/classification step, no match-method deep dive, no warehouse-timeout or per-user quota, and **no scored evaluation gate** (it takes several minutes and needs a YAML upload). Use the full workshop for those, plus agent-as-code and CoWork branding.

## Things worth saying out loud

- **Secondary roles** (default `ALL`) keep ACCOUNTADMIN privileges after `USE ROLE`, so persona tests use `USE SECONDARY ROLES NONE`.
- **Cortex Search runs with owner's rights**: row policies on the source do not scope it. Part 2 demonstrates the leak and the per-audience fix.
- **A row policy with a subquery disables change tracking**, which breaks dynamic tables and search services reading that table.
- **The CoWork object is shared**: add and remove only your own agents.
- Branding the CoWork object is account-wide, so it is not run here.

## Regenerating

The notebooks are composed from the tested cells of the full workshop. With both repos cloned side by side as `student360_workshop` and `student360_1hr`:

```bash
python3 build/compose.py
```
