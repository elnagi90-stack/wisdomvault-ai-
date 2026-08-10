# Branch Strategy

## Main Branches
- main: production-ready, protected branch
- develop: integration branch for ongoing work (optional)

## Supporting Branches
- feature/*: user-facing functionality
- fix/*: bug fixes and production patches
- refactor/*: internal structural improvements without behavior change
- docs/*: documentation updates

## Rules
- Branches must be short-lived.
- PRs required for merge into main.
- Rebase or squash commits when appropriate.
