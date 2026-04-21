#!/usr/bin/env bash
# setup.sh — bootstrap backend + frontend in one shot
set -e

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${CYAN}[info]${NC}  $*"; }
ok()    { echo -e "${GREEN}[ok]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $*"; }
err()   { echo -e "${RED}[err]${NC}   $*"; exit 1; }

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Multi-Agent AI System — Ollama Setup            ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

command -v python3 >/dev/null 2>&1 || err "python3 not found — install Python 3.11+"
command -v node    >/dev/null 2>&1 || err "node not found — install Node 18+"
command -v npm     >/dev/null 2>&1 || err "npm not found"

info "Python $(python3 --version)  |  Node $(node -v)"

# ── Ollama check ──────────────────────────────────────────────────────────
if ! command -v ollama >/dev/null 2>&1; then
  warn "ollama not found. Install from https://ollama.ai then run: ollama pull llama3:8b"
else
  ok "Ollama found: $(ollama --version 2>/dev/null || echo 'installed')"
  if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    warn "'ollama serve' does not appear to be running. Start it before running the backend."
  else
    ok "Ollama server is reachable"
  fi
fi

# ── Backend ───────────────────────────────────────────────────────────────
info "Setting up backend…"
cd backend
python3 -m venv venv
venv/bin/pip install --quiet --upgrade pip
venv/bin/pip install --quiet -r requirements.txt
mkdir -p logs data
ok "Backend ready"
cd ..

# ── Frontend ──────────────────────────────────────────────────────────────
info "Setting up frontend…"
cd frontend
npm install --silent
ok "Frontend ready"
cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "  1. Start Ollama (if not running):"
echo "     ${CYAN}ollama serve${NC}   (separate terminal)"
echo "     ${CYAN}ollama pull llama3:8b${NC}"
echo ""
echo "  2. Start backend:"
echo "     ${CYAN}cd backend && source venv/bin/activate && uvicorn main:app --reload${NC}"
echo ""
echo "  3. Start frontend (new terminal):"
echo "     ${CYAN}cd frontend && npm run dev${NC}"
echo ""
echo "  Dashboard → ${CYAN}http://localhost:3000${NC}"
echo "  API docs  → ${CYAN}http://localhost:8000/docs${NC}"
echo ""
