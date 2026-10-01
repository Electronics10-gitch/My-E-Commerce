# Deployment Plan

## Platform choice
ElectroMart is a single static HTML file with no server-side code, so
it fits any static host. In order of simplicity for a course
deliverable:

| Platform | Why it fits | Trade-off |
|---|---|---|
| GitHub Pages | Free, ties directly to the repo, HTTPS by default | Repo must be public (or GitHub Pro for private) |
| Netlify / Vercel | Drag-and-drop or repo-connected deploy, free tier, HTTPS, custom domain support | One more account to manage |
| Any VPS/cloud static bucket (AWS S3 + CloudFront, Azure Static Web Apps) | Matches the course's "Cloud, VPS, AWS, Azure" deployment options directly | More setup than needed for one static file |

Recommendation for this project: **GitHub Pages**, since the codebase
is already meant to live in a Git repository and Pages needs no extra
account or configuration beyond enabling it on the repo.

## Configuration
- No build command, no environment variables, no server config —
  point the host at the repo root (or a `/docs` or `/public` folder,
  depending on the host's convention) containing `ElectroMart.html`.
- Set `ElectroMart.html` as the site's index/entry file (rename to
  `index.html` at the hosting root, or configure the host's entry-file
  setting, depending on platform).

## Staging
Before treating a deploy as production:
1. Deploy to the host's preview/staging URL (GitHub Pages branch
   preview, or a Netlify/Vercel deploy preview).
2. Run the **Beta** checklist from `09-testing-plan.md` against that
   staging URL, on a real device.
3. Only promote to the production URL/domain once Beta passes.

## Push to repository
```
git init                      # if not already a repo
git add ElectroMart.html docs/
git commit -m "ElectroMart: app + SDLC documentation set"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

## Deploy
- **GitHub Pages**: repo Settings → Pages → deploy from `main` branch
  (root or `/docs`, matching where `index.html` lives).
- **Netlify/Vercel**: connect the repo (or drag-and-drop the file for a
  one-off deploy), no build command needed.

## Go-live checklist
- [ ] `ElectroMart.html` renamed/served as the site's index file
- [ ] HTTPS is active (default on all platforms above)
- [ ] Beta checklist passed on the live/staging URL
- [ ] Footer links (Terms, Privacy, Returns, Requirements, Standards,
      Project Docs) all open correctly on the deployed URL
- [ ] Fresh browser profile confirmed to seed correctly (no leftover
      `localStorage` from development skews the demo)

## Production-ready definition
The app is "production-ready" for this course's purposes once it is
reachable at a public HTTPS URL, the go-live checklist above is
complete, and UAT feedback from `09-testing-plan.md` has been reviewed.
It is **not** production-ready in the sense of handling real payments or
real user data — the simulated backend and local-only storage
(`03-system-requirements.md`) are explicit, documented limitations, and
the migration path to a real backend is described in
`07-design-backend.md`.
