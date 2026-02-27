<p align="center">
  <img src="mobile/assets/icon.png" width="80" height="80" alt="Intrinsic Logo" style="border-radius: 16px;" />
</p>

<h1 align="center">Intrinsic</h1>

<p align="center">
  <strong>Institutional-Grade Equity Research & Valuation Intelligence Platform</strong>
</p>

<p align="center">
  <a href="https://intrinsic.onrender.com/api/analyze/AAPL">Live API</a> •
  <a href="https://expo.dev/artifacts/eas/4yAtgAfhhE6SQdZKHakq9G.apk">Download APK</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## What is Intrinsic?

Intrinsic is a quantitative equity research system that runs **9 institutional valuation models** simultaneously, applies **dynamic model weighting**, and generates a composite investment rating. It goes beyond a simple DCF calculator — it's a complete valuation intelligence engine.

Enter any US-listed ticker → get a full institutional-grade equity research report in seconds.

---

## Features

### 🔬 9 Valuation Models
| Model | Method | Key Input |
|-------|--------|-----------|
| **DCF** | Discounted Cash Flow | FCF projections |
| **Relative** | P/E, P/B, EV/EBITDA multiples | Sector averages |
| **DDM** | Dividend Discount (Gordon Growth) | Dividend history |
| **Residual Income** | Excess return on equity | ROE vs cost of equity |
| **Asset-Based** | Net tangible asset value | Balance sheet |
| **EPV** | Earnings Power Value | Normalized NOPAT |
| **Graham** | Graham Formula | EPS × growth factor |
| **SOTP** | Sum of the Parts (proxy) | EBITDA × sector multiple |
| **EVA** | Economic Value Added | NOPAT − capital charge |

### 🧠 Intelligence Layers
- **Dynamic Model Weighting** — Classifies companies (High Growth / Stable / Mature Dividend / Asset Heavy / Loss-Making) and assigns optimal model weights
- **Confidence Score (0–100)** — Measures reliability of the valuation based on earnings stability, FCF quality, balance sheet strength, return metrics, growth visibility, and model agreement
- **Moat Score (0–100)** — Quantifies competitive advantage using gross margin stability, ROIC spread, growth vs industry, R&D intensity, brand proxy, and operating leverage
- **Quality Score (0–100)** — Assesses business quality via ROE consistency, FCF consistency, debt levels, margin expansion, earnings predictability, CapEx discipline, and share dilution
- **Composite Investment Rating** — Combines all scores into a final rating: **Strong Buy → Buy → Hold → Weak → Avoid**

### 📊 Premium Dashboard
- Dark-gradient hero card with weighted intrinsic value and investment rating
- 9-model tile grid with individual weights and upside/downside
- Animated ring charts for Confidence, Moat, and Quality scores
- Horizontal bar chart showing model weight distribution
- Risk assessment with flagged concerns
- Professional executive summary

### 📱 Mobile App (Android APK)
- Full React Native rebuild of the web dashboard
- Same 9-model analysis, intelligence scores, and rating system
- Downloadable APK — no app store required

---

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌────────────┐
│  React Web  │────▶│  Flask Backend   │────▶│  FMP API   │
│  (Vite)     │     │  (Python)        │     │            │
└─────────────┘     └────────┬────────┘     └────────────┘
                             │
┌─────────────┐              │
│  React      │──────────────┘
│  Native APK │
└─────────────┘

Backend Services:
├── ValuationEngine     (9 models)
├── WeightingEngine     (dynamic model weights)
├── ConfidenceEngine    (valuation reliability)
├── MoatEngine          (competitive advantage)
├── ScoringEngine       (business quality)
├── MasterEngine        (composite rating)
├── RiskEngine          (risk flags)
├── SummaryEngine       (executive summary)
├── FMPService          (data fetching + caching)
└── SectorService       (peer analysis)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, PWA |
| Mobile | React Native, Expo |
| Backend | Python 3, Flask |
| Database | SQLite (development) |
| Data Source | Financial Modeling Prep API |
| Deployment | Render (backend), EAS Build (APK) |

---

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- [FMP API Key](https://financialmodelingprep.com/developer) (free tier available)

### Backend
```bash
cd backend
pip install -r requirements.txt

# Create .env file
echo "FMP_API_KEY=your_key_here" > .env

python app.py
# Backend runs on http://localhost:5000
```

### Frontend (Web)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Mobile (Android APK)
```bash
cd mobile
npm install
npx eas login          # Log in to Expo account
eas build --platform android --profile preview
# Downloads a .apk file you can install on any Android device
```

---

## API

```
GET /api/analyze/<TICKER>
```

**Example:** `GET /api/analyze/AAPL`

**Response:**
```json
{
  "company": { "name": "Apple Inc.", "ticker": "AAPL", "price": 270.08, ... },
  "valuation": {
    "intrinsic_value": 90.78,
    "model_count": 7,
    "models": {
      "dcf": { "value": 90.78 },
      "epv": { "value": 59.01 },
      "residual_income": { "value": 109.72 },
      ...
    }
  },
  "weighting": { "weighted_intrinsic_value": 88.28, "company_type_label": "Stable", ... },
  "confidence": { "score": 50, "badge": "Low", ... },
  "moat": { "score": 45, "classification": "No Moat", ... },
  "scores": { "quality_score_100": 59, ... },
  "master": { "investment_score": 31, "rating": "Avoid" },
  "risk": { "overall_risk": "Moderate", "flags": [...] },
  "summary": { "valuation_verdict": "...", ... }
}
```

---

## Deployment

The project includes a `render.yaml` blueprint for one-click Render deployment:

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your repo → Deploy
4. Set `FMP_API_KEY` environment variable

**Live API:** https://intrinsic.onrender.com

---

## Project Structure

```
investogram/
├── backend/
│   ├── app.py                    # Flask app factory
│   ├── wsgi.py                   # Production WSGI entry
│   ├── config.py                 # Configuration & constants
│   ├── models/models.py          # SQLAlchemy models
│   ├── routes/api.py             # API endpoint
│   └── services/
│       ├── fmp_service.py        # FMP data fetching
│       ├── valuation_engine.py   # 9 valuation models
│       ├── weighting_engine.py   # Dynamic model weights
│       ├── confidence_engine.py  # Confidence scoring
│       ├── moat_engine.py        # Moat scoring
│       ├── scoring_engine.py     # Quality scoring
│       ├── master_engine.py      # Composite rating
│       ├── risk_engine.py        # Risk assessment
│       ├── summary_engine.py     # Executive summary
│       └── sector_service.py     # Sector analysis
├── frontend/
│   ├── src/App.jsx               # Main dashboard
│   ├── src/components/           # React components
│   ├── src/index.css             # Design system
│   └── vite.config.js            # Vite + PWA config
├── mobile/
│   ├── App.js                    # React Native entry
│   ├── src/components/           # RN components
│   ├── app.json                  # Expo config
│   └── eas.json                  # EAS Build config
└── render.yaml                   # Render deployment blueprint
```

---

## License

MIT

---

<p align="center">
  <sub>Built with ❤️ — Data provided by Financial Modeling Prep</sub>
</p>
