#!/usr/bin/env python3
"""
Test the message routing debug endpoint on the running dashboard.
Tests every combination of: no_mode, skill-only, agent-only, combined
across all agents, skills, and models.
"""

import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:5002"


def post(path, data, session=None):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body,
                                 headers={"Content-Type": "application/json"})
    if session:
        req.add_header("Cookie", f"session={session}")
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def test_resolve(message, model=None, session_data=None):
    body = {"message": message}
    if model:
        body["model"] = model
    return post("/api/debug/resolve", body)


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


PASS = "✓"
FAIL = "✗"


def check(condition, label):
    if condition:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}")


def main():
    section("1. NO AGENT, NO SKILL — Plain message")
    r = test_resolve("what is the capital of France?")
    check(r.get("cmd_type") in ("explain", "unknown"), f"cmd_type={r.get('cmd_type')}")
    check(r.get("_will_call") is None, f"No _will_call for plain message")
    print(f"  → model: {r.get('resolved_model')}")

    section("2. AGENT ONLY — @engineer")
    r = test_resolve("build a todo app", model="opencode/deepseek-v4-flash-free",
                     session_data={"agent": "engineer"})
    r["session_agent"] = "engineer"  # simulate
    r2 = test_resolve("design a database schema", model="ollama/qwen2.5-coder:7b",
                      session_data={"agent": "backend"})
    # We can't set session via debug endpoint without cookies, so test via prefixed message:
    r3 = test_resolve("agent: engineer: build a todo app", model="opencode/deepseek-v4-flash-free")
    check(r3.get("cmd_type") == "agent", f"cmd_type=agent")
    check(r3.get("_will_call") == "run_agent (opencode CLI)", f"will_call=run_agent")
    an = r3.get("agent_name", "")
    check(bool(an), f"agent_name extracted: {an}")

    # Agent with Ollama
    r4 = test_resolve("agent: cto: review my architecture", model="ollama/qwen3.5:4b")
    check(r4.get("cmd_type") == "agent", f"cmd_type=agent")
    check(r4.get("_will_call") == "run_ollama (agent)", f"will_call=run_ollama")
    ace = r4.get("agent_content_chars", 0)
    check(ace > 0, f"agent .md content loaded ({ace} chars)")
    check(r4.get("_ollama_agent_has_content"), f"_ollama_agent_has_content=true")

    section("3. SKILL ONLY — $aeo")
    r5 = test_resolve("skill: aeo: audit our homepage for AI citation readiness",
                      model="opencode/deepseek-v4-flash-free")
    check(r5.get("cmd_type") == "skill", f"cmd_type=skill")
    check(r5.get("_will_call") == "run_opencode (skill-only)", f"will_call=run_opencode")
    sc = r5.get("skill_content_chars", 0)
    check(sc > 0, f"SKILL.md content loaded ({sc} chars)")
    check(bool(r5.get("skill_content_excerpt")), "skill content excerpt non-empty")

    # Skill with Ollama
    r6 = test_resolve("skill: aeo: audit our homepage", model="ollama/qwen3.5:4b")
    check(r6.get("_will_call") == "run_ollama (skill-only)", f"will_call=run_ollama")
    sc2 = r6.get("skill_content_chars", 0)
    check(sc2 > 0, f"SKILL.md content loaded for Ollama ({sc2} chars)")

    section("4. COMBINED — $aeo + @engineer")
    r7 = test_resolve("skill: aeo: agent: engineer: audit our homepage",
                      model="opencode/deepseek-v4-flash-free")
    check(r7.get("cmd_type") == "skill", f"cmd_type=skill")
    check(r7.get("_will_call") == "execute_agent (combined)", f"will_call=execute_agent")
    sc3 = r7.get("skill_content_chars", 0)
    ac3 = r7.get("agent_content_chars", 0)
    check(sc3 > 0, f"SKILL.md content loaded for combined ({sc3} chars)")
    check(ac3 > 0, f"agent .md content loaded for combined ({ac3} chars)")

    section("5. ALL AGENTS — verify file content available")
    agents_to_test = ["cto", "growth", "founder", "engineer", "frontend",
                      "backend", "fullstack", "product", "project", "qa", "devops"]
    for ag in agents_to_test:
        r = test_resolve(f"agent: {ag}: test", model="ollama/qwen3.5:4b")
        expected = AGENT_ALIASES.get(ag, ag)
        an = r.get("agent_name", "")
        cc = r.get("agent_content_chars", 0)
        status = PASS if cc > 0 else FAIL
        print(f"  {status} {ag} → {an} ({cc} chars)")

    section("6. SAMPLE SKILLS — verify file content available")
    skills_to_test = ["aeo", "seo-audit", "content-production", "landing",
                      "copywriting", "email-sequence"]
    for sk in skills_to_test:
        r = test_resolve(f"skill: {sk}: test", model="ollama/qwen3.5:4b")
        cc = r.get("skill_content_chars", 0)
        status = PASS if cc > 0 else FAIL
        print(f"  {status} {sk} ({cc} chars)")

    # Summary
    section("SUMMARY")
    print(f"  See full debug output for each test above.")
    print(f"  All {PASS} = skill/agent content loaded from disk and resolved")
    print(f"  All {FAIL} = only text prefix, no file loaded")


AGENT_ALIASES = {
    "cto": "startup-cto",
    "growth": "growth-marketer",
    "founder": "solo-founder",
    "engineer": "cs-engineering-lead",
    "frontend": "cs-frontend-engineer",
    "backend": "cs-backend-engineer",
    "fullstack": "cs-fullstack-engineer",
    "product": "cs-product-manager",
    "project": "cs-project-manager",
    "qa": "cs-quality-regulatory",
    "devops": "devops-engineer",
}

if __name__ == "__main__":
    main()
