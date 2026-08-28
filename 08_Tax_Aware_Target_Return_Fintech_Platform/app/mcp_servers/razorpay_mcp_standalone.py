"""
Standalone Razorpay Gateway JSON-RPC MCP Server.
"""
import sys, json
from razorpay_mcp import RazorpayMCPServer, RazorpayPaymentLinkRequest

server = RazorpayMCPServer()

def handle_rpc(line: str):
    try:
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        msg_id = req.get("id")
        
        if method == "create_payment_link":
            plink_req = RazorpayPaymentLinkRequest(**params)
            result = server.create_payment_link(plink_req).model_dump()
        elif method == "verify_payment":
            result = server.verify_payment(params.get("payment_link_id"))
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
