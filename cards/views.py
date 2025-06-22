from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Create your views here.

def index(request):
    """EMTeeGee home page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EMTeeGee - AI Magic Card Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { background: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .api-links { background: #f8f9fa; padding: 20px; border-radius: 5px; }
            .api-links a { display: block; margin: 10px 0; color: #3498db; text-decoration: none; }
            .api-links a:hover { text-decoration: underline; }
            .feature { margin: 15px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🃏 EMTeeGee - AI Magic Card Analysis</h1>
            
            <div class="status">
                <h3>🚀 System Status: ONLINE</h3>
                <p>Distributed AI analysis system for Magic: The Gathering cards</p>
                <ul>
                    <li>✅ MongoDB Atlas - Remote database connected</li>
                    <li>✅ Ollama AI - GPU acceleration enabled</li>
                    <li>✅ Swarm Workers - Desktop processing active</li>
                    <li>✅ Cloudflare Tunnel - External access enabled</li>
                </ul>
            </div>
            
            <div class="feature">
                <h4>🧠 AI Analysis Features</h4>
                <p>Advanced AI-powered analysis of Magic cards including gameplay tips, synergies, and strategic insights using distributed processing.</p>
            </div>
            
            <div class="feature">
                <h4>🐝 Swarm Processing</h4>
                <p>Multi-machine distributed analysis with desktop GPU workers and laptop CPU workers for maximum throughput.</p>
            </div>
            
            <div class="api-links">
                <h3>🔗 API Endpoints</h3>
                <a href="/cards/api/swarm/status">📊 Swarm Status</a>
                <a href="/cards/api/swarm/workers">👥 Worker Health</a>
                <a href="/admin/">🔧 Admin Panel</a>
            </div>
            
            <div style="text-align: center; margin-top: 30px; color: #7f8c8d;">
                <p>EMTeeGee v2.0 - Distributed AI Analysis System</p>
                <p>Ready for multi-machine Magic card analysis</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
