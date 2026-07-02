# Dejan Vitomirov

Pancevo | 0631610818 | [dejan.vitomirov@gmail.com](mailto:dejan.vitomirov@gmail.com) | [LinkedIn](https://www.linkedin.com/in/dejan-vitomirov/) | [Portfolio](https://dejanvitomirov.com) | [GitHub](https://github.com/Vitomirov)

## Professional Summary

AI-focused fullstack engineer building production-grade applications with LLM integrations, intent parsing, domain-constrained retrieval, and structured extraction pipelines. Experienced shipping AI-powered products with OpenAI APIs, Tavily search, prompt engineering, and async FastAPI and Next.js stacks. Built end-to-end parse → retrieve → prefilter → extract workflows with Redis and PostgreSQL caching, cost-aware quotas, structured JSON logging, and containerized deployment on AWS Lightsail. Strong frontend delivery with Next.js BFF patterns, TypeScript interfaces, and accessible search UX. Previous background in financial operations and structured data workflows, with focus on reliability, truthful structured outputs, and practical product delivery.

## Professional Experience

### AiCrateDigger

AI Engineer / Fullstack Developer | Independent Product Development  
Mar 2026 – Present | [live demo](https://aicratedigger.dejanvitomirov.com/) / [source code](https://github.com/Vitomirov/AiCrateDigger)

- Built production AI search platform turning natural-language queries into actionable vinyl, CD, and cassette listings across geo-aware regional record shops
- Designed end-to-end async pipeline: LLM intent parsing → domain-constrained Tavily retrieval → Python prefilter gating → structured JSON extraction (OpenAI gpt-4o-mini)
- Implemented whitelist-first retrieval with Postgres-backed store registry and LLM-assisted store discovery when local indie coverage is thin
- Built FastAPI backend (Python 3.11+, Pydantic v2, SQLAlchemy 2.0 async, httpx) with single-call search orchestration and explicit failure states (e.g. album_unresolved)
- Developed Next.js 14 BFF with server-side API proxy and TypeScript search UX; backend isolated from public exposure in production deployment
- Integrated Redis caching (7-day TTL) and PostgreSQL for repeat-query performance, store policies, and operator visibility
- Added cost-aware controls: daily parse/Tavily/extract quotas, circuit breakers, and capped candidate pools before LLM extraction
- Implemented snippet-first extraction with RapidFuzz validation and configurable retrieval policies, avoiding full-page scraping for latency and compliance
- Added structured JSON logging with request-scoped pipeline stages, per-IP rate limiting, and fail-closed guards for production observability
- Wrote backend unit tests and eval harness (18 curated edge cases); GitHub Actions CI blocks Lightsail deploy on test failure
- Containerized fullstack application with Docker Compose (Postgres, Redis, backend, frontend)

### Shopify AI Store Analyzer

Fullstack Developer | Startup Product Collaboration  
Oct 2025 – May 2026 | [live demo](https://shopifyanalyzer.dejanvitomirov.com/) / [source code](https://github.com/UkisAI-Academy/nedelja-3-vas-app-Vitomirov)

- Built Next.js 16 storefront audit tool turning public Shopify URLs into structured AI recommendations across conversion, SEO, UX, visuals, and trust
- Designed scrape → snapshot → AI pipeline fetching only public HTML, allow-listed stylesheets, and theme JSON—no admin access or full raw HTML sent to the model
- Implemented Shopify store validation heuristics (.myshopify.com, /cart.js, HTML fingerprints) before analysis runs
- Built POST /api/analyze orchestration: per-IP rate limiting → URL validation → in-memory cache → scrape → OpenAI → Zod-validated JSON response
- Added SSRF-safe outbound fetch with HTTPS-only URLs, private-range blocking, redirect caps, and bounded HTML/CSS response sizes
- Developed Cheerio-based scraper producing compact feature snapshots (headings, sections, CSS cues, theme keys) from live storefronts
- Structured AI output as actionable report: summary, single biggest opportunity, and five categorized recommendation lists
- Built responsive React 19 + TypeScript UI with Tailwind CSS v4, sticky results sidebar on large screens, and clear loading/error states
- Validated request bodies and model JSON responses with Zod end-to-end before returning results to clients
- Wrote Vitest unit tests; enforced TypeScript strict compilation and secret scanning in GitHub Actions CI

### Backend Microservices Platform (Distributed RPG System)

Backend Engineer | System Architecture  
Oct 2025 – Mar 2026 | [source code](https://github.com/Vitomirov/distributed-rpg-services)

- Designed 3-service microservices architecture, enabling modular system scalability
- Built REST APIs supporting authentication, character management, and combat workflows
- Implemented JWT authentication with RBAC, securing service interactions
- Modeled isolated PostgreSQL databases, improving data ownership and reducing coupling
- Integrated Redis caching, reducing database load and improving response time (~30%)
- Containerized services with Docker Compose, enabling consistent environments
- Automated migrations and seeding, simplifying setup and onboarding
- Added unit tests and logging, improving system reliability and debugging

### Warranty Wallet

Fullstack Developer | Independent Product Development  
Jul 2024 – May 2025 | [live demo](https://dejanvitomirov.com/warrantywallet/) / [source code](https://github.com/Vitomirov/warranty-wallet)

- Built production full-stack warranty platform for digitizing PDF receipts, tracking expiration dates, automated reminders, and one-click seller claims
- Designed layered Express API (route → middleware → controller → service) with MySQL 8 connection pooling and volume-mounted PDF storage
- Implemented JWT auth with 15-minute access tokens and 7-day httpOnly refresh cookies, including silent refresh interceptors and proactive token renewal
- Developed React 19 + Vite SPA with feature-based modules, custom hooks, AuthProvider context, and mobile-first Bootstrap/SCSS 7-1 theming
- Built warranty CRUD with Multer PDF upload, inline PDF streaming, and active/expired status tracking on a personal dashboard
- Added node-cron daily job sending Mailgun expiration reminders 14 days before warranty end dates
- Integrated OpenAI gpt-4o-mini in-app assistant scoped to warranty workflows and product feature guidance
- Implemented one-click claim emails to sellers with attached PDFs, account deletion with cascade cleanup, and server-side audit logging
- Added marketing site (Landing, About, Features, FAQ) with per-route SEO meta tags, Framer Motion transitions, and lazy-loaded routes
- Wrote Jest and React Testing Library tests for authentication flows; automated GitHub Actions build and SSH deploy to DigitalOcean VPS via Docker Compose
- Iterated based on feedback from ~10 users, improving usability and core workflows

## Skills & Abilities

### AI & LLMs

OpenAI API, Prompt Engineering, Intent Parsing, Structured JSON Extraction, AI Retrieval Pipelines, Domain-Constrained Search, LLM Pipeline Orchestration, Structured Output Validation, Zod Schema Validation

### Frontend

React (Hooks, Context API), TypeScript, JavaScript (ES6+), Next.js, Next.js BFF / Server-Side API Proxying, Vite, React Router, Axios, Tailwind CSS, Bootstrap / React Bootstrap, Sass (SCSS 7-1), Framer Motion, Responsive Design (Mobile-First), Component Architecture, Reusable Components, Form Handling & Validation, Error Handling, SEO Meta Tags

### Backend

Python, FastAPI, Pydantic, httpx, Async Services, Node.js, Express, TypeScript, REST APIs, Layered API Architecture, Microservices Architecture, JWT Authentication, File Upload (Multer), Zod, Rate Limiting

### Databases & Caching

PostgreSQL, MySQL, Redis, SQLAlchemy, TypeORM, Relational Modeling, Query Optimization

### DevOps

Docker, Docker Compose, CI/CD (GitHub Actions), Structured Logging, DigitalOcean VPS, AWS Lightsail, Linux

### Systems & Integrations

Tavily Search, RapidFuzz, Cheerio, Web Scraping, SSRF Mitigation, Node-cron, Multer, Mailgun, Nodemailer, API Integration

### Testing & Tools

Python unittest, Pipeline Evaluation Harnesses, Jest, React Testing Library, Vitest, Postman, Git, GitHub

## Certifications

### The Ultimate Bootstrap Guide - Bootstrap 5 from Scratch

- Completed project-based certification in Bootstrap 5, focusing on rapid UI development and responsive architecture
- Built Employee Management Dashboard using advanced grid systems and tables
- Implemented interactive modals, offcanvas navigation, and dynamic forms
- Leveraged utility-first classes to accelerate frontend delivery for full-stack applications
- Ensured 100% mobile-first compatibility across all UI templates

### Skills for UkisAI - 5 Week AI Bootcamp (Vibe Coding)

- Completed intensive 5-week AI bootcamp covering practical LLM-assisted development workflows
- Trained in vibe coding methodologies and AI-native product delivery with Cursor AI
- Applied prompt-driven development patterns for full-stack application builds

## Professional Background

### Loan Processing Specialist · xSource, Belgrade

Feb 2020 – Sep 2023

- Processed and verified large volumes of financial data within CRM systems, ensuring accuracy and consistency
- Worked with complex multi-step loan processing and verification workflows, improving data reliability and operational efficiency
- Maintained operational accuracy and data consistency across financial processes

### Team Lead / Market Research · SHG, Belgrade

Dec 2018 – Dec 2019

- Managed data collection workflows and structured large datasets for internal use
- Coordinated small teams and ensured data quality across research processes
- Coordinated structured data collection and reporting workflows

## Education

- Bachelor of Archaeology · University of Belgrade
- Secondary School of Electrical Engineering "Nikola Tesla"
