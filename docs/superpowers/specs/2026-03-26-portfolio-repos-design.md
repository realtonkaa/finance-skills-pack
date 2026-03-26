# AI + Finance Portfolio — 4 Repo Design Spec

## Overview

A portfolio of 4 GitHub repos demonstrating AI and finance skills for college admissions and career portfolio. Two repos focus on finance + AI, two on pure AI/dev tools. All repos tie together under the narrative: "I build AI-powered tools — from finance infrastructure to developer productivity."

### Target Audience
- College admissions officers (shows initiative, depth, and technical range)
- Recruiters / hiring managers (demonstrates real, usable projects)
- Other developers (skills and MCP servers they can actually install and use)

### Tech Stack (shared defaults)
- **Language:** Python (primary), TypeScript where needed
- **AI:** Claude API via Anthropic SDK
- **APIs:** Free-tier financial APIs (Alpha Vantage, Finnhub, CoinGecko, news APIs)
- **Distribution:** npm/pip packages, GitHub releases

---

## Repo 1: `finance-mcp-server`

### What It Is
An MCP server that connects Claude to financial data — but unlike the existing [financial-datasets/mcp-server](https://github.com/financial-datasets/mcp-server), this one doesn't just serve raw data. It has an AI analyst layer that reasons about the data and a paper trading simulator.

### Unique Differentiator
The existing finance MCP server is a data pipe. Ours is an **AI analyst** — it interprets, scores sentiment, builds bull/bear cases, and lets you paper trade. It's the difference between a database and a financial advisor.

### Features

#### AI Analyst Layer
- **Structured analysis:** Ask "What's the outlook on AAPL?" → get a bull case, bear case, key risks, and a confidence score
- **Sentiment scoring:** Aggregates news and social sentiment into a numeric score per ticker
- **Comparison:** "Compare TSLA vs F" → side-by-side analysis with AI commentary
- **Earnings digest:** Summarize recent earnings calls and their implications

#### Paper Trading Simulator
- **Virtual portfolio:** Start with a configurable amount of virtual cash
- **Trade execution:** Buy/sell stocks and crypto through Claude with natural language ("Buy 10 shares of AAPL")
- **P&L tracking:** Real-time portfolio value based on live prices
- **Trade history:** Full log of all trades with timestamps and prices
- **Performance metrics:** Total return, win rate, best/worst trades

#### Data Sources (Free APIs)
- **Alpha Vantage:** Stock quotes, historical data, fundamentals
- **Finnhub:** Real-time quotes, news, earnings calendars
- **CoinGecko:** Crypto prices and market data
- **News API / Finnhub News:** Financial news for sentiment analysis

### MCP Tools Exposed
- `analyze_stock(ticker)` — full AI analysis with bull/bear case
- `get_sentiment(ticker)` — sentiment score from news/social
- `compare_stocks(ticker1, ticker2)` — side-by-side comparison
- `paper_trade(action, ticker, quantity)` — execute virtual trade
- `get_portfolio()` — current paper trading portfolio
- `get_trade_history()` — all past paper trades
- `market_overview()` — broad market summary with AI commentary

### Architecture
```
finance-mcp-server/
├── src/
│   ├── server.py          # MCP server entry point
│   ├── tools/             # MCP tool handlers
│   │   ├── analyst.py     # AI analysis logic
│   │   ├── sentiment.py   # Sentiment scoring
│   │   ├── trading.py     # Paper trading engine
│   │   └── market.py      # Market data fetching
│   ├── data/
│   │   ├── providers/     # API wrappers (Alpha Vantage, Finnhub, etc.)
│   │   └── cache.py       # Response caching to avoid rate limits
│   └── portfolio/
│       ├── engine.py      # Portfolio state management
│       └── storage.py     # Persist portfolio to local JSON/SQLite
├── tests/
├── README.md
├── pyproject.toml
└── mcp.json               # MCP server manifest
```

### Key Design Decisions
- **Local storage for portfolio:** Paper trading state stored in local JSON or SQLite — no external database needed
- **Caching:** Cache API responses to stay within free tier rate limits
- **AI analysis uses Claude API:** The MCP server calls Claude to generate the analyst commentary, creating a "Claude calling Claude" loop that's architecturally interesting

---

## Repo 2: `finance-skills-pack`

### What It Is
A collection of Claude Code skills (slash commands) for financial analysis and strategy backtesting. The star feature is `/backtest` — describe a trading strategy in plain English, and it codes it, runs it against real historical data, and shows results directly in the terminal.

### Features

#### `/backtest` (Star Feature)
- User describes a strategy in natural language: "Buy when RSI drops below 30, sell when it goes above 70"
- Skill translates this into executable Python code
- Runs against real historical data (pulled from free APIs)
- Displays results in terminal:
  - Total return vs buy-and-hold
  - Win rate, max drawdown, Sharpe ratio
  - Trade log with entry/exit points
  - ASCII chart of equity curve
- AI feedback: "This strategy underperformed buy-and-hold by 12%. The RSI threshold might be too aggressive — here's why..."

#### `/stock-check`
- Quick stock lookup by ticker
- Current price, day change, 52-week range
- AI-generated one-paragraph analysis
- Key metrics (P/E, market cap, volume)

#### `/budget`
- Interactive budget planning session
- Input income and expense categories
- AI suggests optimizations and savings targets
- Generates a monthly budget breakdown

#### `/portfolio`
- Track holdings (manual input or connect to paper trading MCP)
- Portfolio allocation visualization (ASCII pie chart)
- AI analysis: diversification score, risk assessment, rebalancing suggestions

### Architecture
```
finance-skills-pack/
├── skills/
│   ├── backtest/
│   │   ├── skill.md           # Skill definition
│   │   ├── strategy_parser.py # NL → code translation
│   │   ├── backtester.py      # Backtesting engine
│   │   └── reporter.py        # Terminal output formatting
│   ├── stock-check/
│   │   └── skill.md
│   ├── budget/
│   │   └── skill.md
│   └── portfolio/
│       └── skill.md
├── lib/
│   ├── data_fetcher.py        # Shared data fetching (reuses finance-mcp APIs)
│   └── charts.py              # ASCII chart generation
├── tests/
├── README.md
└── package.json               # For npm distribution (Claude Code skills)
```

### Key Design Decisions
- **Plain English → code:** The backtester uses Claude to translate strategies into Python, then executes them. This is the core innovation.
- **Terminal-native output:** Everything renders in the terminal — ASCII charts, tables, colored text. No browser needed.
- **Shared data layer with Repo 1:** Can optionally use the Finance MCP server for data, or fetch directly.

---

## Repo 3: `ai-research-agent`

### What It Is
A universal AI research and content analyzer. Feed it a topic, URL, YouTube video, tweet, Reddit post, or podcast — and it produces a structured, in-depth analysis. Works as Claude Code skills (`/research`, `/analyze`) or as a standalone Python tool.

### Features

#### Topic Research (`/research`)
- Input: any topic or question
- Agent searches the web, reads multiple sources
- Produces a structured research brief:
  - Executive summary
  - Key findings (with citations)
  - Different perspectives/viewpoints
  - Knowledge gaps / areas of uncertainty
- Configurable depth: "quick" (3-5 sources) vs "deep" (10+ sources)

#### URL/Content Analysis (`/analyze`)
Accepts any URL and auto-detects the content type:

**Websites/Articles:**
- Content summary: what it's about, key points, bias detection, credibility rating
- Technical teardown: tech stack detection, SEO audit, performance notes, security headers, accessibility score

**YouTube Videos:**
- Extract transcript (via YouTube transcript API)
- Chapter-by-chapter summary
- Key takeaways and timestamps
- Sentiment and tone analysis
- Speaker identification (if multiple)

**Twitter/X Threads:**
- Full thread extraction
- Summary of argument/narrative
- Fact-check flags on claims
- Engagement analysis

**Reddit Posts/Threads:**
- Post + top comments extraction
- Summary of discussion and consensus
- Key disagreements highlighted

**Podcasts:**
- Transcript extraction (via RSS feed audio → transcription)
- Topic segmentation
- Key quotes and timestamps
- Guest/host identification

#### Output Format
- Clean markdown reports
- Saved to a local `/reports` directory
- Optional: push to GitHub Gist

### Architecture
```
ai-research-agent/
├── skills/
│   ├── research/
│   │   └── skill.md
│   └── analyze/
│       └── skill.md
├── src/
│   ├── agent.py              # Core research agent orchestrator
│   ├── extractors/
│   │   ├── web.py            # Website content extraction
│   │   ├── youtube.py        # YouTube transcript extraction
│   │   ├── twitter.py        # Twitter/X thread extraction
│   │   ├── reddit.py         # Reddit post/comment extraction
│   │   └── podcast.py        # Podcast transcript extraction
│   ├── analyzers/
│   │   ├── content.py        # Content/bias/credibility analysis
│   │   ├── technical.py      # Tech stack/SEO/security analysis
│   │   └── sentiment.py      # Sentiment and tone analysis
│   ├── search/
│   │   └── web_search.py     # Web search for topic research
│   └── report/
│       ├── formatter.py      # Markdown report generation
│       └── templates/        # Report templates by content type
├── tests/
├── README.md
└── pyproject.toml
```

### Key Design Decisions
- **Auto-detection:** The agent detects content type from the URL — user doesn't need to specify
- **Extractor pattern:** Each platform has its own extractor module, making it easy to add new platforms
- **Graceful degradation:** If transcript extraction fails (e.g., private video), fall back to metadata analysis
- **Rate limiting:** Built-in delays and caching to respect API limits

---

## Repo 4: `auth-kit`

### What It Is
A Claude Code skill that sets up authentication in any project with one command. Detects your framework, asks what auth method you want, and scaffolds the entire auth system — routes, middleware, database models, frontend components, everything.

### The Problem It Solves
Every vibecoder skips auth until it's too late, then bolts on something insecure. Auth is the #1 thing that's boring to set up, critical to get right, and different for every framework. This tool eliminates that friction.

### Features

#### `/auth` Skill
1. **Framework detection:** Scans the project and identifies the stack (Next.js, Express, Flask, Django, FastAPI, etc.)
2. **Interactive setup:** Asks what you need:
   - Auth method: OAuth (Google, GitHub, etc.), email/password, magic link, API keys, JWT
   - Features: signup, login, logout, password reset, email verification, session management
   - Database: what ORM/database you're using
3. **Code generation:** Scaffolds everything:
   - Auth routes/endpoints
   - Middleware/guards
   - Database models/migrations
   - Frontend components (login form, signup form, protected routes)
   - Environment variable templates
   - Security best practices baked in (CSRF, rate limiting, password hashing)
4. **Validation:** After scaffolding, runs a check to verify everything is wired up correctly

#### Supported Frameworks (v1)
- **Next.js** (App Router + Pages Router)
- **Express.js**
- **Flask**
- **FastAPI**
- **Django** (stretch goal)

#### Supported Auth Methods (v1)
- Email/password with bcrypt hashing
- OAuth 2.0 (Google, GitHub)
- JWT tokens
- Session-based auth

### Architecture
```
auth-kit/
├── skills/
│   └── auth/
│       └── skill.md           # Main skill definition
├── src/
│   ├── detector.py            # Framework/stack detection
│   ├── frameworks/
│   │   ├── nextjs/
│   │   │   ├── templates/     # Code templates for Next.js auth
│   │   │   └── scaffolder.py
│   │   ├── express/
│   │   │   ├── templates/
│   │   │   └── scaffolder.py
│   │   ├── flask/
│   │   │   ├── templates/
│   │   │   └── scaffolder.py
│   │   └── fastapi/
│   │       ├── templates/
│   │       └── scaffolder.py
│   ├── auth_methods/
│   │   ├── email_password.py
│   │   ├── oauth.py
│   │   └── jwt.py
│   └── validator.py           # Post-scaffold validation
├── tests/
├── README.md
└── package.json
```

### Key Design Decisions
- **Template-based, not AI-generated:** Auth code comes from vetted templates, not LLM generation — security-critical code shouldn't be hallucinated
- **Framework-specific:** Each framework gets its own scaffolder rather than a generic one-size-fits-all approach
- **Opinionated defaults:** Secure by default (bcrypt, CSRF protection, rate limiting) — user doesn't need to know security to get it right
- **No lock-in:** Generated code is plain, standard code for each framework — no dependency on auth-kit after scaffolding

---

## Build Order

Recommended order based on complexity and impact:

1. **`finance-skills-pack`** — Start here. Skills are self-contained and quick to ship. The `/backtest` feature is the portfolio centerpiece.
2. **`finance-mcp-server`** — Builds on the same finance APIs. MCP server is a natural companion to the skills pack.
3. **`ai-research-agent`** — Standalone project, no dependencies on the finance repos. Good variety piece.
4. **`auth-kit`** — Most complex (many frameworks to support). Ship last but start with 1-2 frameworks.

## Cross-Repo Connections
- `finance-skills-pack` can optionally use `finance-mcp-server` as its data layer
- All repos share consistent README style, documentation quality, and branding
- Each repo works independently — no hard dependencies between them

## Success Criteria
- Each repo has a clear, professional README with demos/screenshots
- Each repo is installable and usable by others (published to npm/pip)
- Each repo has tests
- Each repo solves a real problem, not just a demo
