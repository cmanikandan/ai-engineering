"""
Tax-Aware Quantitative Hurdle Rate Calculator for Indian Equity Markets.
Compliant with Section 111A of the Income Tax Act (STCG @ 20% + 4% Health & Education Cess = 20.8%).
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

class TaxHurdleBreakdown(BaseModel):
    principal_amount: float = Field(description="Initial invested capital in INR")
    net_target_roi_pct: float = Field(description="User's desired in-hand net profit percentage")
    net_target_profit_inr: float = Field(description="User's desired in-hand net profit in INR")
    stcg_tax_rate_pct: float = Field(default=20.8, description="Indian Short-Term Capital Gains tax rate (20% + 4% cess)")
    stt_rate_pct: float = Field(default=0.1, description="Securities Transaction Tax on delivery trades")
    estimated_brokerage_inr: float = Field(default=40.0, description="Estimated Zerodha flat brokerage + GST (Buy + Sell)")
    gross_target_profit_inr: float = Field(description="Gross pre-tax profit required to deliver net target")
    gross_target_roi_pct: float = Field(description="Gross pre-tax percentage gain required")
    projected_stcg_tax_inr: float = Field(description="Projected tax liability payable to ITD under Section 111A")
    projected_friction_inr: float = Field(description="Total friction fees (STT + Zerodha brokerage + GST)")

def calculate_tax_hurdle(
    principal_amount: float,
    net_target_roi_pct: float,
    stcg_tax_rate: float = 0.208,
    stt_rate: float = 0.001,
    turnover_friction_pct: float = 0.0015
) -> TaxHurdleBreakdown:
    """
    Calculates the exact pre-tax hurdle return required to guarantee the user's requested
    net in-hand return after deducting Indian STCG (20.8%), STT, and Zerodha brokerage.
    """
    net_target_profit = principal_amount * (net_target_roi_pct / 100.0)
    
    # Total friction: STT (0.1% buy + 0.1% sell on delivery = 0.2% total round-trip) + Zerodha flat fees
    variable_friction = principal_amount * (stt_rate * 2 + turnover_friction_pct)
    flat_brokerage = 40.0  # ₹20 buy + ₹20 sell
    total_friction = variable_friction + flat_brokerage
    
    # Gross hurdle calculation
    gross_target_profit = (net_target_profit + total_friction) / (1.0 - stcg_tax_rate)
    gross_target_roi_pct = (gross_target_profit / principal_amount) * 100.0
    projected_stcg_tax = gross_target_profit * stcg_tax_rate
    
    return TaxHurdleBreakdown(
        principal_amount=round(principal_amount, 2),
        net_target_roi_pct=round(net_target_roi_pct, 2),
        net_target_profit_inr=round(net_target_profit, 2),
        stcg_tax_rate_pct=round(stcg_tax_rate * 100.0, 2),
        stt_rate_pct=round(stt_rate * 100.0, 2),
        estimated_brokerage_inr=round(flat_brokerage, 2),
        gross_target_profit_inr=round(gross_target_profit, 2),
        gross_target_roi_pct=round(gross_target_roi_pct, 2),
        projected_stcg_tax_inr=round(projected_stcg_tax, 2),
        projected_friction_inr=round(total_friction, 2)
    )
