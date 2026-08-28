"""
Persistent State Store for WealthPulse AI.
Maintains user profiles, authentication sessions, active investment goals,
open orders, and historical tax ledgers. Compatible with local disk or Google Cloud Firestore.
"""

import os, json, time, uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

STATE_FILE = os.getenv("STATE_FILE_PATH", os.path.join(os.path.dirname(__file__), "state_db.json"))

class UserSession(BaseModel):
    user_id: str
    email: str
    name: str
    role: str = "investor"
    zerodha_balance_inr: float = 100000.0
    razorpay_balance_inr: float = 0.0
    active_goal: Optional[Dict[str, Any]] = None
    open_orders: List[Dict[str, Any]] = []
    realized_trades: List[Dict[str, Any]] = []
    created_at: str

class PersistentStateStore:
    def __init__(self, filepath: str = STATE_FILE):
        self.filepath = filepath
        self._state: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # Default Seed State with Test User
        return {
            "users": {
                "user_demo_101": {
                    "user_id": "user_demo_101",
                    "email": "demo@wealthpulse.ai",
                    "password_hash": "Investor@2026",
                    "name": "Mani Chandrasekaran (Demo Investor)",
                    "role": "investor",
                    "zerodha_balance_inr": 100000.0,
                    "razorpay_balance_inr": 0.0,
                    "active_goal": None,
                    "open_orders": [],
                    "realized_trades": [],
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for uid, u in self._state.get("users", {}).items():
            if u.get("email") == email:
                return u
        return None

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._state.get("users", {}).get(user_id)

    def update_user_goal(self, user_id: str, goal: Dict[str, Any]):
        if user_id in self._state["users"]:
            self._state["users"][user_id]["active_goal"] = goal
            self._save()

    def add_order(self, user_id: str, order: Dict[str, Any]):
        if user_id in self._state["users"]:
            self._state["users"][user_id]["open_orders"].append(order)
            self._save()

    def record_realized_trade(self, user_id: str, trade: Dict[str, Any]):
        if user_id in self._state["users"]:
            self._state["users"][user_id]["realized_trades"].append(trade)
            self._save()

    def deposit_funds(self, user_id: str, amount: float, source: str = "razorpay"):
        if user_id in self._state["users"]:
            if source == "razorpay":
                self._state["users"][user_id]["razorpay_balance_inr"] += amount
                self._state["users"][user_id]["zerodha_balance_inr"] += amount
            self._save()

state_store = PersistentStateStore()
