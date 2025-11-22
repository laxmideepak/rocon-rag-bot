# api/index.py
"""Minimal ROCON Docs API - No external dependencies"""

from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Health check - returns JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "message": "ROCON Docs Assistant API",
            "version": "1.0.0",
            "endpoints": {
                "GET /": "Health check",
                "POST /": "Ask a question (coming soon)"
            }
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_POST(self):
        """Simple echo endpoint"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            question = data.get('question', 'No question provided')
            
            response = {
                "answer": f"✅ API is working! You asked: '{question}'\n\nFull RAG system integration coming soon.",
                "sources": [],
                "metadata": {
                    "status": "test_mode",
                    "received_question": question
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, indent=2).encode())
        
    except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error = {
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error processing request"
            }
            self.wfile.write(json.dumps(error).encode())
    
    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
