# Folder Structure

```text
app/
  api/
    v1/
  core/
  domain/
  application/
  infrastructure/
  repositories/
  services/
  schemas/
  models/
  tests/
config/
docs/
frontend/
infra/
migrations/
storage/
tests/
```

## Notes
- The current repository will be refactored gradually to match this structure.
- Routes remain thin and delegate to application services.
- Infrastructure concerns such as storage and persistence remain isolated.
