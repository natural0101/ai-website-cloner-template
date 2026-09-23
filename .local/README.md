# Local runtime

This project has two isolated Docker modes:

- `./local.ps1 dev` runs the Next.js development server with source mounts at `http://ai-website-cloner.localhost:3101`.
- `./local.ps1 parity` builds the repository Dockerfile and runs its standalone production server at `http://ai-website-cloner.localhost:3100`.

No `.env` file is loaded automatically. Add explicit local-safe variables to the Compose overlays only when the application actually requires them. This static frontend has no database, migrations, seed data, queue, storage, or SMTP service.

Use `./local.ps1 down` to stop containers without deleting data and `./local.ps1 reset` for project-scoped volumes.
