"""
Episodic Financial Memory & Tax Ledger: Persists investor profiles, target goals,
open positions, and realized capital gains for Section 111A tax accounting.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class InvestorGoal(BaseModel):
    principal: float
    net_target_roi: float
    gross_target_profit: float
    timeframe_days: int
    created_at: str

class TradeRecord(BaseModel):
    symbol: str
    qty: int
    buy_price: float
    sell_price: Optional[float] = None
    realized_gain_inr: float = 0.0
    stcg_tax_liability_inr: float = 0.0
    status: str = "OPEN"

class FinancialMemoryStore:
    def __init__(self):
        self.active_goal: Optional[InvestorGoal] = None
        self.trade_history: List[TradeRecord] = []
        self.total_deposited_inr: float = 0.0
        self.cumulative_realized_profit_inr: float = 0.0
        self.cumulative_stcg_tax_inr: float = 0.0

    def set_goal(self, goal: InvestorGoal):
        self.active_goal = goal

    def record_trade(self, trade: TradeRecord):
        self.trade_history.append(trade)
        if trade.status == "CLOSED":
            self.cumulative_realized_profit_inr += trade.realized_gain_inr
            self.cumulative_stcg_tax_inr += trade.stcg_tax_liability_inr

    def get_progress_summary(self) -> Dict[str, Any]:
        if not self.active_goal:
            return {"status": "NO_ACTIVE_GOAL"}
            
        net_achieved = self.cumulative_realized_profit_inr - self.cumulative_stcg_tax_inr
        target_net = self.active_goal.principal * (self.active_goal.net_target_roi / 100.0)
        progress_pct = (net_achieved / target_net) * 100.0 if target_net > 0 else 0.0
        
        return {
            "principal": self.active_goal.principal,
            "target_net_profit_inr": target_net,
            "net_profit_achieved_inr": round(net_achieved, 2),
            "gross_profit_realized_inr": round(self.cumulative_realized_profit_inr, 2),
            "stcg_tax_incurred_inr": round(self.cumulative_stcg_tax_inr, 2),
            "progress_percentage": round(min(100.0, max(0.0, progress_pct)), 2),
            "goal_reached": net_achieved >= target_net
        }
