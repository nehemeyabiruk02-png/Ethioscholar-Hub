# EthioScholar Hub 21.0

A GitHub Pages scholarship/opportunity discovery website for students, with a real-data refresh pipeline.

## What is automatic?

The single GitHub Actions workflow `update-and-deploy.yml` runs:

- manually from **Actions → EthioScholar Hub — refresh and deploy → Run workflow**
- automatically every **6 hours**
- after changes are pushed to `main`

The workflow fetches records from the configured public sources, creates `data.json`, and then deploys the **same generated dataset** to GitHub Pages. This fixes the common problem where a data-refresh workflow changes a file but the live Pages deployment does not receive that change.

GitHub Pages supports custom GitHub Actions workflows for deployment. See the official GitHub documentation for Pages and Actions.

## Important: no fake 10,000

The site is designed to handle 10,000+ records, but it does **not** manufacture 10,000 scholarships. The number shown is the number actually returned by connected sources.

To reach 10,000+ real records, more legitimate open datasets/APIs must be added and their licensing/provenance checked.

## Current sources

- Open Scholarships — `https://scholarships.grudged.io/scholarships.json` — CC BY 4.0
- WorqNow USA/UK/Canada/Australia scholarship endpoints — provider terms

Every imported record must contain an HTTP(S) URL. Records are deduplicated by URL.

## Safety against API failure

If every source is temporarily unreachable, the updater **does not erase the previous `data.json`**. The site keeps its previous dataset. The frontend also has a small starter fallback so the interface remains usable on a brand-new repository.

## Publish on GitHub Pages

1. Create a **public** GitHub repository.
2. Upload every file in this folder, keeping `.github/workflows/update-and-deploy.yml` exactly in place.
3. Go to **Settings → Pages**.
4. Under **Build and deployment → Source**, choose **GitHub Actions**.
5. Open **Actions**, select **EthioScholar Hub — refresh and deploy**, and run it manually once.
6. Open the Pages URL shown by GitHub.

GitHub says Pages is available for public repositories on GitHub Free, and custom Actions workflows can publish the site.

## Project claim for scholarship applications

A truthful description is:

> Built EthioScholar Hub, a scalable scholarship and opportunity discovery platform for Ethiopian students, with personalized filtering, application tracking, source-linked records, and an automated GitHub Actions data-refresh/deployment pipeline.

Do not claim that the platform already contains 10,000 real scholarships unless the connected sources actually return that many.
