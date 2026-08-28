"""
Standalone Zerodha Kite Connect JSON-RPC MCP Server.
"""
import sys, json
from zerodha_mcp import ZerodhaKiteMCPServer, OrderPlacementRequest

server = ZerodhaKiteMCPServer()

def handle_rpc(line: str):
    try:
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        msg_id = req.get("id")
        
        if method == "get_quote":
            result = server.get_quote(params.get("symbols", ["NIFTYBEES", "GOLDBEES"]))
        elif method == "place_order":
            order_req = OrderPlacementRequest(**params)
            result = server.place_order(order_req)
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
