# observer-library

Analysis **tools** and **skills** for the heating observer (HeatpumpsN
`observer/`), kept apart from the observer's code so they can be shared
between houses and versioned on their own.

* A **tool** is code the observer's agent runs in its sandbox: a folder
  `tools/<name>/` with `tool.yaml` (name, version, purpose, the kind of data
  it needs, typed inputs, output), `tool.py` (a `run(...)` function; numpy,
  pandas, scipy) and `test_tool.py` (pytest on synthetic data, `from tool
  import run`).
* A **skill** is a recipe: `skills/<name>/SKILL.md` with front matter
  (version, title, description, the tools it uses) and the steps in Markdown:
  domain knowledge and methods that worked.

Everything is written against generic inputs (time series, data frames,
roles such as "a room temperature", "the circuit's pump state"), never
against one house's signal ids.

## Versions

`library.yaml` carries the library version (semantic versioning, see
`CHANGELOG.md`). Every item has an integer `version`, raised whenever it
changes. The observer records which item versions a run used; its audit
flags are bound to the content hash of an item.

## Using it with an observer

* **Development:** add the checkout to the observer's `config.yaml`:

  ```yaml
  agent:
    library_paths: [~/Work/observer-library]
  ```

  Edits are live; house items of the observer (written by agents) take
  precedence over items of the same name here.
* **As a pack:** `observer library import observer-library-0.2.0.tgz` (or
  the portal's Library tab); build the archive with `scripts/pack.sh`.
* **Bringing items back:** export them from the observer (`observer library
  export --item tools/<name> -o x.tgz`, or the portal), unpack into this
  repository, raise the versions, update the changelog, run the checks,
  commit.

## Checks

```bash
python3 scripts/check.py          # manifests, versions, every tool's tests (needs pytest, numpy, pandas, pyyaml)
```
