"""
Standalone DhanHQ JSON-RPC MCP Server Runner.
"""
import sys, json
from dhan_mcp import DhanHQMCPServer, DhanOrderRequest

server = DhanHQMCPServer()

def handle_rpc(line: str):
    try:
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        msg_id = req.get("id")
        
        if method == "get_market_quote":
            result = server.get_market_quote(params.get("symbols", ["NIFTYBEES", "GOLDBEES"]))
        elif method == "get_holdings":
            result = server.get_positions_and_holdings()
        elif method == "place_order":
            order_req = DhanOrderRequest(**params)
            result = server.place_dhan_order(order_req)
        else:
            result = {"error": f"Method {method} not supported"}
            
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}) + "\n")
        sys.stdout.flush()
    except Exception as e:
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": str(e)}) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())
