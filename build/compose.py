"""Compose the 1-hour notebooks from the tested cells of the full workshop (../student360_workshop)."""
import json, glob, os, hashlib
SRC = os.path.join(os.path.dirname(__file__), "..", "..", "student360_workshop", "notebooks")
OUT = os.path.join(os.path.dirname(__file__), "..", "notebooks")
code = {}
for f in sorted(glob.glob(SRC + "/*.ipynb")):
    for c in json.load(open(f))["cells"]:
        if c["cell_type"] == "code":
            n = c["metadata"]["name"]
            code[os.path.basename(f)[9:11] + ":" + n] = c
            code.setdefault(n, c)

def md(t, i):
    return {"cell_type": "markdown", "id": hashlib.md5(t.encode()).hexdigest()[:8] + str(i), "metadata": {"codeCollapsed": True}, "source": t.strip("\n")}

def pick(name):
    c = json.loads(json.dumps(code[name]))
    c["source"] = c["source"].replace("ROWCOUNT => 2000", "ROWCOUNT => 1200")
    return c

def build(fname, steps):
    cells = []
    for i, s in enumerate(steps):
        cells.append(md(s, i) if s.startswith(("#", ">", "⏱", "🛠", "📌")) or "\n" in s or " " in s else pick(s))
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "SQL", "language": "sql", "name": "sql"}, "language_info": {"name": "sql"}}, "nbformat": 4, "nbformat_minor": 5}
    json.dump(nb, open(os.path.join(OUT, fname), "w"), indent=1)
    print(fname, len(cells))

build("Express_1_Build_Student360.ipynb", [
"""# Student 360 in 1 Hour - Part 1: Build the Student 360
⏱ **~20 min** (mostly waiting for cells to run). Icons: 🛠️ action, 📌 note.

**Scenario:** Lakeside University loses students and finds out too late. The signals exist in **six systems that each call a student something different** (SIS, LMS, Financial Aid, Bursar, Advising CRM, Campus card). All data is synthetic.

**What you will do:** create an isolated lab, load the six sources, resolve identity, engineer features with **dynamic tables**, clean advising notes with **Cortex AI functions**, and assemble one governed row per student.

**Snowflake features you touch:** roles and grants, dynamic tables (incremental), `AI_REDACT`, `AI_CLASSIFY`, data quality checks.""",
"## 1. Lab foundation (isolated role, database, warehouse)\n🛠️ Everything lives under `STUDENT360_LAB` so it can be dropped as a unit. Run the next cells in order.",
"create_role", "create_db", "create_wh_grants", "cross_region", "00:set_context", "sim_helper",
"## 2. Load six source systems\n🛠️ Each source has its **own student key format**: `S0000123`, login email, `FA-100007` plus a bare number, `STU-0000123`, card id. ~1,200 students. Deterministic, so every attendee gets identical data.",
"load_sis_student", "load_sis_enrollment", "load_lms", "load_finaid_bursar", "load_crm", "load_campus", "validate_raw",
"## 3. Identity resolution\n🛠️ The SIS id is the golden key. Other systems link by exact id, prefix, exact email, and a fallback on the email local part (rescues the legacy `@lakeside.com` domain).\n📌 **Best practice:** deterministic matching first, keep the method, and **measure the match rate** before anything flows downstream.",
"create_xwalk", "match_report",
"## 4. Feature tables as dynamic tables\n🛠️ Declare the result; Snowflake keeps it fresh. We set `REFRESH_MODE = INCREMENTAL` so only changed data is reprocessed.",
"create_academic", "create_lms_feat", "create_fin_feat", "create_campus_feat",
"## 5. Unstructured advising notes with Cortex AI\n🛠️ `AI_REDACT` strips names, phones and emails; `AI_CLASSIFY` tags a theme. Only the redacted text flows on.\n📌 **Best practice:** redact in the data layer, not in a prompt. A prompt asks; the data layer guarantees.",
"create_notes_enriched", "check_redaction", "create_adv_feat",
"## 6. Assemble the Student 360\n🛠️ One row per student, an explainable risk score and the **drivers** behind it. Every join is a LEFT JOIN from the SIS roster, so no student disappears.",
"create_student360", "check_360",
"""## ✅ Part 1 complete
You built an identity crosswalk, five incremental feature tables, PII-safe advising notes and `CURATED.STUDENT_360`.

**Takeaways:** resolve identity deterministically and measure it; declarative pipelines (dynamic tables) beat orchestration code; redact PII before AI can read it; make scores explainable.

**Next:** Part 2 gives the data meaning and governs access.""",
])

build("Express_2_Context_and_Governance.ipynb", [
"""# Student 360 in 1 Hour - Part 2: Context and Governance
⏱ **~20 min.**

**What you will do:** give the data business meaning with a **semantic view** and **Cortex Search**, then enforce who can see what with **roles, row access and masking**, and prove it by switching roles.

**Snowflake features you touch:** semantic views (metrics, synonyms, verified queries, custom instructions), Cortex Search (fuzzy match + RAG), row access policies, masking policies, the four-layer access model.""",
"02:set_context",
"## 1. Search services and a course view\n🛠️ `STUDENT_NAME_SEARCH` resolves typos in names to the exact value. `ADVISING_NOTES_SEARCH` gives semantic retrieval over the **redacted** notes.\n📌 Use literal matching for identifier columns; use RAG for document text.",
"create_course_view", "create_name_search", "create_notes_search",
"## 2. The semantic view\n🛠️ This is where business meaning is written once: what *DFW* and *HIGH risk* mean, synonyms like *at-risk students*, verified queries, and rules for rejecting out-of-bounds questions (contact details, adverse action).\n📌 **Best practices:** descriptions are the #1 accuracy input; leave PII out of the model entirely; define metrics in the view, not in prompts.",
"create_semantic_view",
"## 3. Validate before building any agent\n🛠️ Query the view directly and reconcile to source. If the view is wrong, the agent will be wrong.",
"test_sv_college", "test_sv_reconcile",
"## 4. Roles and the four-layer access model\n🛠️ Two personas: an **Engineering advisor** (their college's rows, PII visible) and an **IR analyst** (all rows, PII masked). Layers: platform, agent, tools, data. We grant three now; the agent layer comes in Part 3. Note there is **no grant on RAW**.",
"four_layer_grants",
"## 5. Row-level and column-level policy\n🛠️ One expression-based row policy scopes by college; masking policies hide email, phone and date of birth.\n📌 A row policy containing a **subquery** disables change tracking and would break dynamic tables and search services, so this lab uses an expression policy.",
"create_scope", "create_masking",
"## 6. Prove it: same query, different roles\n📌 Persona tests use `USE SECONDARY ROLES NONE`. Otherwise your session keeps ACCOUNTADMIN privileges and the test proves nothing.",
"test_as_advisor", "test_as_ir", "test_no_raw",
"## 7. The Cortex Search owner's-rights gotcha\n⚠️ Search services run with the **owner's** rights. Row policies on the source table do not scope them. Run the next cell to see notes from other colleges leak, then fix it with a per-audience index.",
"naive_grant", "scoped_search", "verify_scoped_search", "reset_role",
"""## ✅ Part 2 complete
A validated semantic view, two search services plus a scoped one, two persona roles, row and column policies, all proven by role switching.

**Takeaways:** write meaning once; least exposure; enforce access on the **data**, not the prompt; scope search indexes per audience.

**Next:** Part 3 builds the agents and puts them in CoWork.""",
])

build("Express_3_Agents_and_CoWork.ipynb", [
"""# Student 360 in 1 Hour - Part 3: Agents and CoWork
⏱ **~20 min.**

**What you will do:** create two agents from one pattern, grant the last access layer, test as each persona, add cost controls, publish to **CoWork**, and clean up.

**Snowflake features you touch:** Cortex Agents (`CREATE AGENT ... FROM SPECIFICATION`), `DATA_AGENT_RUN`, tags and budgets, Snowflake Intelligence (CoWork).""",
"04:set_context",
"## 1. Create the two agents\n🛠️ An agent is a **declarative spec**: orchestration budget, response and routing instructions, tools (semantic view for numbers, search for notes, a chart tool), and where each tool points.\n📌 Same code, different persona: the data layer decides what each can answer. The Advisor Assistant uses the Engineering-scoped notes index; the Analyst uses the institution-wide one.",
"create_advisor_agent", "create_ir_agent",
"## 2. Layer 2: grant `USAGE ON AGENT`\n🛠️ This completes the four layers. Without it a role sees the data but cannot call the agent.",
"grant_agents",
"## 3. Test each persona\n🛠️ These call `SNOWFLAKE.CORTEX.DATA_AGENT_RUN`, the same API CoWork uses. The result is the full event stream; the final answer is the item with `type = text`. The third test asks for a phone number and must be **refused**.",
"test_advisor_agent", "test_ir_agent", "test_guardrail", "test_no_access",
"## 4. Cost control: attribute and constrain\n🛠️ Tag the agents and warehouse for chargeback, then set a spending budget with an alert.\n📌 Observe (`CORTEX_AGENT_USAGE_HISTORY`), attribute (tags), control (timeout, budget, quota).",
"create_tag", "create_budget",
"""## 5. Publish to CoWork
🔹 The CoWork object is a **shared, account-level singleton**. Publishing only adds your agents; it never replaces the object. Publishing controls *visibility*; agent grants control *who can invoke*.""",
"publish_agents", "grant_me_persona",
"""## 6. Try it in CoWork
Open **Snowsight → AI & ML → Snowflake Intelligence** and pick **Advisor Assistant**. Ask:
1. *I am advisor Dana Whitfield. Who are the 5 students on my caseload I should reach out to first, and why?*
2. *What is the email address of one of my students?* (expect a refusal)

Then swap your persona and ask the **Student Success Analyst**: *How many high-risk students are in each college?*
```sql
USE ROLE ACCOUNTADMIN;
REVOKE ROLE STUDENT360_LAB_ADVISOR_ENGINEERING FROM USER <your_user>;
GRANT  ROLE STUDENT360_LAB_IR_ANALYST TO USER <your_user>;
```

### Going further (not run in the hour)
The full workshop adds a scored **evaluation gate** (`EXECUTE_AI_EVALUATION`, with a refusal test), agent-as-code spec capture, per-user quotas and CoWork branding: https://github.com/sfc-gh-isuryawinata/student360_workshop""",
"## 7. Clean up\n🛠️ Removes only this lab's objects and only your own agents from the shared CoWork object.",
"unpublish", "revoke_me", "drop_cost_objects", "drop_database", "drop_roles", "verify_clean",
"""## ✅ Done
Six siloed sources became one governed Student 360, an AI assistant that respects who is asking, and a CoWork experience, in about an hour.""",
])
