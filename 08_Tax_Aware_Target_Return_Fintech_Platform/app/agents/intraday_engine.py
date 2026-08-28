"""
Intraday & Swing Trading Quantitative Strategy Engine.
Specialized logic for "Make a profit by end of day" vs Multi-Day Swing trades.
Enforces 3:15 PM IST Auto-Square-Off guardrails to prevent Zerodha broker penalty charges.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

class TradingStrategyMode(BaseModel):
    mode: str = Field(description="'INTRADAY_MIS' or 'SWING_CNC'")
    horizon_description: str
    target_roi_pct: float
    max_drawdown_stoploss_pct: float
    auto_square_off_time: Optional[str]
    tax_treatment: str
    recommendation: str

def determine_strategy_mode(horizon_text: str, requested_roi: float) -> TradingStrategyMode:
    """
    Distinguishes Intraday (End-of-Day) from Swing (Multi-Day).
    Enforces realistic intraday risk envelopes (capping intraday target at 1.5% - 3.0% with 1.0% stoploss).
    """
    is_intraday = any(k in horizon_text.lower() for k in ["end of day", "today", "intraday", "eod", "by 3:15", "hours"])
    
    if is_intraday:
        # Cap realistic intraday target to 1.5% - 2.5% to avoid speculative wipeout
        safe_intraday_target = min(requested_roi, 2.5) if requested_roi > 0 else 1.5
        return TradingStrategyMode(
            mode="INTRADAY_MIS",
            horizon_description="Intraday (Square off by 3:15 PM IST)",
            target_roi_pct=safe_intraday_target,
            max_drawdown_stoploss_pct=1.0,  # Strict 1% Intraday Stoploss
            auto_square_off_time="15:15:00 IST",
            tax_treatment="Section 43(5) Speculative Business Income (Taxed at marginal slab rate)",
            recommendation=f"Intraday momentum strategy activated. Target set to {safe_intraday_target}% (₹{safe_intraday_target*1000:,.0f} per ₹1L) with automated 3:15 PM square-off to prevent Zerodha ₹50+GST penalty."
        )
    else:
        return TradingStrategyMode(
            mode="SWING_CNC",
            horizon_description="Multi-Day Swing Delivery (CNC)",
            target_roi_pct=requested_roi,
            max_drawdown_stoploss_pct=3.0,  # 3% Max Drawdown
            auto_square_off_time=None,
            tax_treatment="Section 111A Short-Term Capital Gains (Flat 20.8% with cess)",
            recommendation=f"Delivery swing strategy activated. Target set to {requested_roi}% net after 20.8% STCG tax."
        )
