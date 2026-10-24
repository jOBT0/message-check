# Save the working prototype in Git

This step creates a local version history and an annotated `v0.1.0` tag. Run
the commands yourself in PowerShell on the laptop containing `AI_Project`.
The files supplied here do not create a repository on your laptop by themselves.

## 1. Copy the documentation files

Extract `message-check-baseline.zip`, then copy its five files directly into
`AI_Project`, beside `app.py`:

- `README.md`
- `BASELINE.md`
- `GIT_SETUP.md`
- `.gitignore`
- `.gitattributes`

The archive contains documentation and Git configuration, not replacement
application code or datasets. If a same-named file already contains your own
work, merge the relevant additions instead of overwriting it. Keep the leading
dots in the two configuration filenames; neither should end in `.txt`.

## 2. Check Git and the current folder

Open PowerShell inside `AI_Project` and run:

```powershell
git --version
git rev-parse --show-toplevel
```

If Git is not installed, use the official
[Git for Windows installer](https://git-scm.com/install/windows), reopen
PowerShell, and retry.

If the second command reports that this is not a Git repository, initialize it:

```powershell
git init
```

If it prints the `AI_Project` path, use the existing repository. If it prints
a parent folder containing other projects, use that existing repository's
structure deliberately before continuing; do not accidentally stage its other
projects. These commands assume `AI_Project` is the repository root.

```powershell
git status --short
```

In an existing repository, inspect any changes already staged so that unrelated
work is not accidentally included in this baseline commit.

## 3. Stage the intended files

The main command names only the supplied documentation, current application,
dependency file, and synthetic datasets:

```powershell
git add -- README.md BASELINE.md GIT_SETUP.md .gitignore .gitattributes app.py analyze.py evaluate_v2.py requirements-ui.txt data/test_cases.json data/validation_cases.json
```

If `evaluate.py` is still present, retain the historical v1 evaluator too:

```powershell
git add -- evaluate.py
```

The older `UI_START.md` and `NEXT_STEPS.md` guides are optional. If you want to
retain them and both files exist, add them explicitly:

```powershell
git add -- UI_START.md NEXT_STEPS.md
```

If a named file is missing, check its location and exact filename before moving
on. Stop on command errors rather than committing an incomplete snapshot.

Review what is staged:

```powershell
git diff --cached --stat
git diff --cached --name-only
git diff --cached
```

Press `q` to exit Git's viewer if it opens. The staged files should include
source, documentation, and the two synthetic datasets. They should not include
the virtual environment, raw analysis reports, or local settings.

The ignore file applies to untracked files. To check for already tracked
environment or report files:

```powershell
git ls-files -- .venv venv results .env
```

If this prints files that should remain local, remove those paths from Git's
index while retaining the files on disk:

```powershell
git rm -r --cached --ignore-unmatch -- .venv venv results .env
```

Then review the staged list again. This does not erase copies from older
commits. Other already tracked private paths also need deliberate review.

## 4. Commit the reviewed files

```powershell
git commit -m "Record working Message Check prototype and evaluation baseline"
```

If Git asks for an author identity, set it for this repository and retry the
commit. These PowerShell commands prompt for the values you want recorded:

```powershell
git config user.name (Read-Host "Name to record in commits")
git config user.email (Read-Host "Email to record in commits")
```

The email is commit metadata. If using a GitHub no-reply address, copy the exact
address supplied by your own account rather than inventing one.

## 5. Name the baseline and verify it

First check whether the tag already exists:

```powershell
git tag --list v0.1.0
```

If it prints nothing, create the tag after the commit succeeds:

```powershell
git tag -a v0.1.0 -m "Working local prototype with prompt v2 and output checks v2"
```

If it already exists, retain it and choose a new unused version name when
appropriate. Do not force-replace an existing baseline tag.

```powershell
git log -1 --oneline --decorate
git status --short
```

The log should show your commit and, when newly created, `tag: v0.1.0`.
An empty status output means there are no remaining tracked changes or
unignored untracked files. Optional older guides can still appear as untracked
if you chose not to include them. Generated reports remain on disk and are
ignored.

The commit and tag are local. A local Git history is not an off-device backup.
A GitHub remote can be set up as a separate next step once you choose the
repository and its visibility.

## Official references

- [Initialize a repository](https://git-scm.com/docs/git-init)
- [Ignore rules and already tracked files](https://git-scm.com/docs/gitignore)
- [Remove paths from the index with --cached](https://git-scm.com/docs/git-rm)
- [Annotated tags](https://git-scm.com/docs/git-tag)
- [Text-file line endings](https://git-scm.com/docs/gitattributes)
