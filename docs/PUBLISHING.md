# Deploy the interactive lab with Pages

The same static site can be deployed with GitHub Pages or GitLab Pages. Both
pipelines build and validate the public artifact without repository-specific
URLs, names, or secrets.

## GitHub Pages

The `Deploy Pages` workflow in `.github/workflows/pages.yml` is ready for a
future GitHub repository. No owner, repository name, hostname, or custom domain
is configured. GitHub supplies the deployment URL when the workflow runs.

### After pushing to GitHub

1. Open **Settings → Pages** in the GitHub repository.
2. Under **Build and deployment**, select **GitHub Actions** as the source.
3. Open **Actions → Deploy Pages → Run workflow** and select `main`.
4. Follow the URL reported by the `github-pages` deployment environment.

Later pushes to `main` that change the site, public documentation, or build
inputs deploy automatically. Pull requests build and validate the artifact
without deploying. Manual runs on branches other than `main` also validate only.
If the default branch is renamed, update the branch filters and deployment
conditions in the workflow.

The workflow uses the standard `GITHUB_TOKEN` and GitHub's Pages actions. It
needs no personal access token, repository-specific secret, or dedicated
deployment branch. Enable Actions if the repository or organization restricts
them, and allow deployments to the `github-pages` environment from `main`.

## GitLab Pages

The `.gitlab-ci.yml` pipeline builds and validates the site on branch and tag
pipelines. A successful pipeline on `main` passes the validated artifact to the
`pages` job, which publishes its contents from `public/`. Merge request pipelines
are not explicitly configured.

After pushing this configuration and the `main` branch to GitLab, make sure a
runner that can use the `python:3.12-slim` image is available and GitLab Pages
is enabled for the project. Check **Build → Pipelines** for the job results and
**Deploy → Pages** for the URL and access settings. Menu names and Pages
availability can vary with the GitLab instance and its configuration.

The pipeline does not require a personal access token or a hard-coded domain.
To deploy from a different branch later, update the branch filter in
`.gitlab-ci.yml`.

## What is published

`tools/build_pages.py` stages an explicit set of public files in the ignored
`artifacts/pages/` directory. It includes the interactive lab, rendered guide,
project overview, testing and recording instructions, MIT license, and reviewed
media. Local notes, raw screenshots, Git history, and the rest of the workspace
are excluded. GitHub uploads that staging directory; GitLab copies its validated
contents into the `public/` Pages artifact.

All site navigation and assets use relative URLs. The same artifact works at
a domain root or beneath a repository path. Repository README links stay
relative until the repository's final hosted URL is known.

The GIFs are committed, reviewed assets. Deployment does not record a browser
session or contact Virtuoso; regenerate animations separately using
[the media instructions](../test/DEMO_MEDIA.md).

## Build locally

From the repository root:

```sh
uv venv .venv
uv pip install --python .venv/Scripts/python.exe -r test/pages-requirements.txt
.venv/Scripts/python.exe tools/build_pages.py
.venv/Scripts/python.exe test/check_pages.py
.venv/Scripts/python.exe -m http.server 8000 --bind 127.0.0.1 --directory artifacts/pages
```

On Linux/macOS, use `.venv/bin/python`. Visit `http://127.0.0.1:8000/` to
preview the deployed layout. With the optional browser dependencies installed,
`python test/check_pages.py --browser --channel msedge` also checks the site
under a simulated repository prefix. Omit `--channel` to use Playwright Chromium.
