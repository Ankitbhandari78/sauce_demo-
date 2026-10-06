# Locator Strategy — Stable, Non-Flaky Test Scripts

## Purpose
This document defines the rules for choosing element locators in all
generated or hand-written test scripts. The goal is to eliminate
flaky tests caused by dynamic IDs, ephemeral refs, and unstable DOM
structure.

## Core Rule
**Never rely on anything that can change between runs.** If a locator
would break after a page reload, a framework re-render, or a new
snapshot, it is forbidden.

## Forbidden Locators (DO NOT USE)

- ❌ Playwright MCP refs (e.g. `e5`, `aria-ref=e5`) — valid only for
  one snapshot, dead on the next.
- ❌ Auto-generated IDs — anything matching:
  - random strings: `id="input-3a8f9c2"`
  - numeric suffixes: `id="user-12345"`
  - UUIDs
  - framework prefixes: `react-select-`, `mui-`, `ant-`, `chakra-`,
    `headlessui-`, `radix-`, `input-`, `select-`, `field-`
- ❌ Deep CSS/XPath chains tied to layout:
  - `div > div:nth-child(3) > span`
  - `//div[@class='row'][2]/input`
- ❌ Styling classes that change with design:
  - `.mt-4`, `.text-red-500`, `.btn-primary-v2`
- ❌ Index-based selectors: `.nth(0)`, `.first()`, `.last()` — unless
  the list is guaranteed stable and ordered.

## Allowed Locators — Use in This Priority Order

Always climb from top to bottom. Stop at the first one that matches.

| Priority | Locator | When to use |
|----------|---------|-------------|
| 1 | `getByRole(role, { name })` | Any element with an accessible role + name. **Default choice.** |
| 2 | `getByLabel(text)` | Form inputs with an associated `<label>`. |
| 3 | `getByPlaceholder(text)` | Inputs with a placeholder and no label. |
| 4 | `getByTestId(testid)` | When a `data-testid` attribute exists. |
| 5 | `getByText(text)` | Stable, unique visible text (buttons, links, headings). |
| 6 | `getByAltText(text)` | Images with meaningful alt text. |
| 7 | `getByTitle(text)` | Elements with a stable `title` attribute. |
| 8 | CSS with a stable attribute | Only as last resort: `[name="email"]`, `[aria-label="..."]`, `[type="submit"]`, `[href="/login"]`. |

## Anti-Pattern → Fix Table

| ❌ Flaky | ✅ Stable |
|---------|----------|
| `page.locator('#input-3a8f9c2')` | `page.getByLabel('Email')` |
| `page.locator('[ref=e5]')` | `page.getByRole('button', { name: 'Submit' })` |
| `page.locator('div:nth-child(2) > button')` | `page.getByRole('button', { name: 'Save' })` |
| `page.locator('.btn-primary')` | `page.getByTestId('save-btn')` |
| `page.locator('#user-12345')` | `page.getByRole('link', { name: 'Profile' })` |
| `page.locator('text=Click here')` (ambiguous) | `page.getByRole('link', { name: 'Click here' })` |

## Rules for AI-Generated Scripts

When generating test code from a page snapshot:

1. **Never output a ref.** The word `ref` must not appear in the
   generated script.
2. **Never output an auto-generated ID.** Reject anything matching
   the forbidden patterns above.
3. **Apply the priority order.** Try role first; only fall back if
   nothing higher matches.
4. **One locator per element.** Do not chain multiple brittle
   selectors to "be safe" — pick the single best one.
5. **Verify against a fresh snapshot.** Before finalizing, confirm
   the locator still resolves after a new snapshot is taken. If it
   does not, move to the next locator in the priority list.
6. **If no stable locator exists**, add a `data-testid` to the
   element (or ask the developer to) and use `getByTestId(...)`. Do
   **not** fall back to DOM-chain, index-based, styling-class, or
   auto-generated-ID selectors. Do not guess. Do not emit a brittle
   fallback silently.

## Notes for This Project (Python + pytest)

- This suite uses `pytest-playwright`, so the same priority order
  applies with the snake_case method names:
  `get_by_role(role, name=...)`, `get_by_label(...)`,
  `get_by_placeholder(...)`, `get_by_test_id(...)`,
  `get_by_text(...)`, `get_by_alt_text(...)`, `get_by_title(...)`.
- SauceDemo exposes stable `data-test` attributes, which map to
  `page.get_by_test_id("...")` (priority 4). Prefer `get_by_role`
  and `get_by_test_id` for assertions that currently use
  `page.locator('[data-test="..."]')`.
- Avoid styling-class selectors such as `.app_logo`; use a
  role/text/test-id locator instead.

## Rules for Developers (Testability Contract)

To keep tests stable, the application must expose:

- `data-testid` on all interactive elements that lack a clear
  role/label (icons, custom widgets, drag handles, modals).
- Proper `<label>` associations for every form input.
- Meaningful `aria-label` on icon-only buttons.
- Stable `name` attributes on form fields.
- Avoid dynamically generated `id` values in components that will be
  tested. If unavoidable, always pair with `data-testid`.

### Naming convention for test IDs

## Verification Checklist (Before Committing a Script)

- [ ] No refs (`e5`, `aria-ref=...`) anywhere in the file.
- [ ] No numeric or random-looking IDs.
- [ ] No `nth-child`, `nth()`, `.first()`, `.last()` unless justified
      in a comment.
- [ ] Every locator follows the priority order.
- [ ] Every locator resolves against a fresh snapshot.
- [ ] If a testid was needed, a ticket/comment exists to add it to
      the source.
- [ ] Script runs green twice in a row without edits.

## Example — Correct Pattern

```python
# ✅ Stable, semantic, survives reloads and re-renders
page.get_by_label("Email address").fill("user@example.com")
page.get_by_label("Password").fill("secret")
page.get_by_role("button", name="Sign in").click()
expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
```

## Environment Integrity

- Never copy or move a `.venv`. It is not portable — paths are baked at
  creation. If a project is relocated, delete `.venv` and recreate with
  `python3 -m venv .venv`.
- The `(.venv)` prompt label is NOT proof the venv is active. It reflects
  `VIRTUAL_ENV_PROMPT` and can be inherited from a copied environment.
- Before any test run, verify the interpreter:
  `which python3` → must resolve inside the CURRENT project's `.venv`.
- Always invoke pytest as: `python3 -m pytest` (never bare `pytest`).
- `.venv/` must always be listed in `.gitignore`.
- If "No module named pytest" appears, check `which python3` FIRST — it
  usually means the wrong interpreter, not a missing package.

## Pricing / Cart Test Rules

- NEVER hard-code expected prices or totals.
- Read prices from the page, compute the expected value in code,
  then assert the page's displayed value equals it.
- Always parse currency with a helper (strip `$`, commas, spaces).
- Round to 2 decimals, or work in integer cents, to avoid float errors.
- Verify in this order:

    1. `sum(item_prices) == subtotal`
    2. `subtotal + tax == total`
    3. `total == computed expected total`

- Use `data-testid` locators for prices and totals, never positional
  CSS or `nth-child`.

## Pre-Push Safety Rules
- NEVER run `git add .` — stage explicit paths only.
- ALWAYS run `git status` and `git diff --staged` before committing.
- NEVER commit `.env` or any file containing credentials.
- Verify `.gitignore` covers: .venv/, __pycache__/, test-results/, .playwright-mcp/, .env
- Run `python3 -m pytest` before pushing.