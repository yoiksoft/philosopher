# GitHub Actions workflows

### `deploy-beta.yml`

Deployment workflow for the beta environment. Whenever a tagged beta release is created, this workflow will run and deploy changes to the beta environment.

`https://philosopher.yoik.software/beta`

### `deploy-v1.yml`

Deployment workflow for the production environment, specifically major version 1. Whenever a tagged release is made following major version 1, this workflow will run and deploy changes to the v1 environment.

`https://philosopher.yoik.software/v1`
