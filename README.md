# AMASS

AMASS is a dashboard that keeps track of security vulnerabilities and shows how risky they are for a company.

New vulnerabilities get published every day. AMASS collects them, scores how dangerous each one is, and shows the results on a simple dashboard — so a security team can see what's risky at a glance instead of digging through raw data.

## Screenshots

| Dashboard | Threat Monitor |
|---|---|
| ![Dashboard](stitch_designs/dashboard.png) | ![Threat Monitor](stitch_designs/threat.png) |

| Endpoint Management | Landing Page |
|---|---|
| ![Endpoints](stitch_designs/endpoint.png) | ![Landing](stitch_designs/landing.png) |

## What it does

- **Collects vulnerabilities** — automatically pulls new ones from CISA, a public vulnerability database.
- **Scores how dangerous each one is** — turns two technical scores into one simple rating: LOW, MEDIUM, HIGH, or CRITICAL.
- **Shows the big picture** — a heatmap of risk, a timeline of new vulnerabilities, and a chart comparing that against the company's stock price.
- **Sends alerts** — users can follow a company and get an email when something new affects it.
- **Scans real computers** — a script (`scanner/pc_scanner.ps1`) checks what software is installed on a Windows PC and flags anything with a known vulnerability.

## How it's built

- **Frontend**: a React dashboard (`frontend/`).
- **Backend**: small Python programs (one per job — collecting data, scoring risk, sending alerts, login) that run on AWS.
- **Database**: PostgreSQL.
- **Infrastructure**: set up automatically with Terraform (`terraform/`), with separate staging and production copies.
- **CI/CD**: every code change is checked and tested automatically, then rolled out to staging before production (`.github/workflows/main.yml`).

## Running it locally

**Backend**

```bash
pip install -r requirements.txt
python3 -m pytest --cov=. --ignore=microservices/testing
```

**Frontend**

```bash
cd frontend
npm install
npm start
```

**Docker (everything at once)**

```bash
docker compose up --build
```
