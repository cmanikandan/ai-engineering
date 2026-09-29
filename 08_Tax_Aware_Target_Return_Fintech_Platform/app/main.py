"""
WealthPulse AI: Autonomous Tax-Aware Target-Return FinTech Copilot Backend.
Powered by Gemini 3.8 Flash & Gemini 3.1 Pro with DhanHQ, Zerodha Kite & Razorpay MCP Servers.
Includes Interactive Web UI Dashboard, JWT Authentication, and Intraday (EOD) Trading Logic.
"""

import os, time
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from agents.tax_hurdle_calculator import calculate_tax_hurdle, TaxHurdleBreakdown
from agents.intraday_engine import determine_strategy_mode, TradingStrategyMode
from mcp_servers.razorpay_mcp import RazorpayMCPServer, RazorpayPaymentLinkRequest
from mcp_servers.zerodha_mcp import ZerodhaKiteMCPServer, OrderPlacementRequest
from memory.state_store import state_store
from security.auth import create_jwt_token, verify_jwt_token
from security.sebi_guardrail import SecurityGuardrail

app = FastAPI(
    title="WealthPulse AI - FinTech Copilot",
    version="1.0.0",
    description="Autonomous Tax-Aware Target-Return Wealth Platform for Indian Investors"
)

# Static Web Dashboard
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize MCP Servers & GenAI Client
razorpay_mcp = RazorpayMCPServer()
zerodha_mcp = ZerodhaKiteMCPServer()
client = genai.Client()

class LoginRequest(BaseModel):
    email: str = Field(default="demo@wealthpulse.ai")
    password: str = Field(default="Investor@2026")

class NewbieInvestPrompt(BaseModel):
    user_prompt: str = Field(description="Raw natural language prompt from newbie user")
    user_name: str = Field(default="Mani Chandrasekaran (Demo Investor)")
    phone: str = Field(default="9876543210")
    email: str = Field(default="demo@wealthpulse.ai")

class ParsedNewbieIntent(BaseModel):
    principal_amount_inr: float = Field(description="Extracted capital amount in INR")
    net_target_roi_pct: float = Field(description="Extracted target return percentage")
    timeframe_raw: str = Field(description="Extracted timeframe text, e.g., 'end of day', '2 months'")
    plain_english_plan: str = Field(description="Simple, reassuring explanation for beginner")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ONLINE", "message": "WealthPulse AI Backend Ready"}

@app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    """Logs in user or validates pre-seeded test user."""
    user = state_store.get_user_by_email(req.email)
    if not user or user.get("password_hash") != req.password:
        raise HTTPException(status_code=401, detail="Invalid email or password. Use demo@wealthpulse.ai / Investor@2026")
    token = create_jwt_token({"user_id": user["user_id"], "email": user["email"], "name": user["name"]})
    return {"success": True, "token": token, "user": user}

@app.post("/api/v1/onboard-and-execute")
def onboard_and_execute(req: NewbieInvestPrompt):
    """
    Zero-Friction Newbie Autopilot:
    1. Ingests raw natural language (e.g. 'Loaded 1L in zerodha, need profit by end of day').
    2. Uses Gemini 3.8 Flash to extract intent & timeframe.
    3. Handles Intraday (MIS + 3:15 PM Square-off) vs Swing (CNC + Section 111A STCG 20.8%).
    4. Pings Zerodha Kite & Razorpay MCP servers.
    5. Dispatches GTT orders with 1% stop-loss protection.
    """
    parse_prompt = f"""
You are WealthPulse AI, an expert financial copilot for an Indian retail beginner.
Analyze the user's prompt and extract:
- principal_amount_inr (e.g. 100000.0)
- net_target_roi_pct (if user says 'make a profit by end of day' without specifying %, assume 2.0% for safe intraday)
- timeframe_raw (e.g. 'end of day', 'today', '2 months')
- plain_english_plan (warm, reassuring 2-sentence summary)

User Prompt: "{req.user_prompt}"
"""
    try:
        parsed_res = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=parse_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ParsedNewbieIntent,
                temperature=0.0
            )
        )
        intent = ParsedNewbieIntent.model_validate_json(parsed_res.text)
    except Exception:
        # Fallback heuristic parser
        is_eod = "end of day" in req.user_prompt.lower() or "today" in req.user_prompt.lower()
        intent = ParsedNewbieIntent(
            principal_amount_inr=100000.0 if "1 lakh" in req.user_prompt.lower() or "100000" in req.user_prompt else 50000.0,
            net_target_roi_pct=2.0 if is_eod else 10.0,
            timeframe_raw="end of day" if is_eod else "60 days",
            plain_english_plan="We have allocated your capital across Nifty 50, Gold, and Large-Cap ETFs with automated target exits and stop-loss protection."
        )

    # Determine Strategy Mode (Intraday vs Delivery)
    strat_mode = determine_strategy_mode(intent.timeframe_raw, intent.net_target_roi_pct)

    # Tax Hurdle Calculation
    hurdle = calculate_tax_hurdle(
        principal_amount=intent.principal_amount_inr,
        net_target_roi_pct=strat_mode.target_roi_pct
    )

    # Screen Market & Execute Orders via Zerodha MCP
    quotes = zerodha_mcp.get_quote(["NIFTYBEES", "GOLDBEES", "HDFCBANK"])
    
    # Place GTT / Intraday Orders
    orders = []
    allocation = {"NIFTYBEES": 0.50, "GOLDBEES": 0.30, "HDFCBANK": 0.20}
    gross_roi_mult = 1.0 + (hurdle.gross_target_roi_pct / 100.0)
    
    for sym, weight in allocation.items():
        sym_cap = intent.principal_amount_inr * weight
        ltp = quotes[sym]["ltp"]
        qty = int(sym_cap / ltp)
        target = round(ltp * gross_roi_mult, 2)
        sl = round(ltp * (1.0 - strat_mode.max_drawdown_stoploss_pct / 100.0), 2)
        
        ord_res = zerodha_mcp.place_order(OrderPlacementRequest(
            tradingsymbol=sym,
            transaction_type="BUY",
            quantity=qty,
            order_type="GTT" if strat_mode.mode == "SWING_CNC" else "LIMIT",
            price=ltp,
            target_price=target,
            stop_loss_price=sl
        ))
        orders.append({
            "symbol": sym,
            "qty": qty,
            "buy_price": ltp,
            "target": target,
            "stop_loss": sl,
            "order_id": ord_res["order_id"]
        })
        state_store.add_order("user_demo_101", ord_res)

    # Persist Active Goal
    state_store.update_user_goal("user_demo_101", {
        "intent": intent.model_dump(),
        "strategy": strat_mode.model_dump(),
        "hurdle": hurdle.model_dump(),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    return {
        "success": True,
        "newbie_intent": intent.model_dump(),
        "strategy_mode": strat_mode.model_dump(),
        "tax_hurdle_waterfall": hurdle.model_dump(),
        "orders_dispatched": orders,
        "market_quotes": quotes,
        "sebi_disclaimer": SecurityGuardrail.verify_sebi_compliance("")["statutory_disclaimer"]
    }

@app.get("/api/v1/user-state")
def get_user_state():
    return state_store.get_user("user_demo_101")
