# Intrinsic — Automated Equity Research & Valuation Platform

A professional, institutional-grade web application for automated equity valuation of US large-cap stocks. Built with React + Flask.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
# Add your FMP API key to .env
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

## Configuration

Edit `backend/.env`:
```
FMP_API_KEY=your_key_here
```

## Architecture
- **Frontend**: React + Vite (port 3000)
- **Backend**: Flask (port 5000)
- **Database**: SQLite (development)
- **Data**: Financial Modeling Prep API
