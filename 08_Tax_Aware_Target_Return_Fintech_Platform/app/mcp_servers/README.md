# Model Context Protocol (MCP) Server Setup Guide

This directory provides standalone Model Context Protocol (MCP) servers for **Zerodha Kite Connect** and **Razorpay**.

## 1. Local Configuration (Claude Desktop / Cursor / Antigravity)
Add the contents of `mcp_config.json` to your local MCP configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Antigravity / Jetski**: `<appDataDir>/mcp/`

## 2. Available MCP Tools

### A. Zerodha Kite Connect MCP (`zerodha-kite`)
- `mcp_zerodha_get_holdings`: Fetches live stock and ETF portfolio.
- `mcp_zerodha_get_quote`: Returns real-time LTP and market depth for NSE symbols.
- `mcp_zerodha_place_gtt_order`: Dispatches buy orders with automated profit target & trailing stop-loss.
- `mcp_zerodha_get_margins`: Returns available equity & commodity trading margins.

### B. Razorpay Gateway MCP (`razorpay-gateway`)
- `mcp_razorpay_create_payment_link`: Generates instant dynamic UPI / NetBanking payment URLs.
- `mcp_razorpay_verify_payment`: Validates webhook deposit confirmations.
- `mcp_razorpay_create_upi_mandate`: Configures recurring SIP autopay mandates.

## 3. Production Deployment on Google Cloud Run
Each MCP server can be packaged as a standalone Server-Sent Events (SSE) microservice on Cloud Run:
```bash
gcloud run deploy zerodha-mcp-server \
  --image gcr.io/$PROJECT_ID/zerodha-mcp:latest \
  --region us-central1 \
  --allow-unauthenticated
```
