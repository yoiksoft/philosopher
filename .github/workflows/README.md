# GitHub Actions workflows

### `lint-and-format.yaml`

Runs linting and formatting checks on the codebase to ensure that it follows a consistent style.

### `deploy-beta.yml`

Deployment workflow for the beta environment. Whenever a tagged beta release is created, this workflow will run and deploy changes to the beta environment.

`https://api.kwot.io/beta`

### `deploy-v1.yml`

Deployment workflow for the production environment, specifically major version 1. Whenever a tagged release is made following major version 1, this workflow will run and deploy changes to the v1 environment.

`https://api.kwot.io/v1`

### `codeql-analysis.yml`

GitHub provided workflow for CodeQL analysis of the codebase.
