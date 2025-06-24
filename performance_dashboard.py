#!/usr/bin/env python3
"""
Web-based Performance Dashboard for Enhanced Swarm
Simple HTTP server that serves real-time performance metrics
"""

import os
import django
import json
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from performance_monitor import PerformanceMonitor

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard_html()
        elif parsed_path.path == '/api/metrics':
            self.serve_metrics_json()
        elif parsed_path.path == '/api/workers':
            self.serve_worker_details()
        else:
            self.send_error(404)
    
    def serve_dashboard_html(self):
        """Serve the main dashboard HTML"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Swarm Performance Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-title { font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #3498db; }
        .metric-label { font-size: 14px; color: #7f8c8d; }
        .worker-list { margin-top: 15px; }
        .worker-item { padding: 10px; background: #ecf0f1; margin: 5px 0; border-radius: 4px; }
        .status-active { border-left: 4px solid #27ae60; }
        .status-idle { border-left: 4px solid #f39c12; }
        .status-offline { border-left: 4px solid #e74c3c; }
        .refresh-info { text-align: center; margin-top: 20px; color: #7f8c8d; }
        .progress-bar { width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #3498db; transition: width 0.3s ease; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced Swarm Performance Dashboard</h1>
            <p>Real-time monitoring of AI card analysis system</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">📊 System Overview</div>
                <div id="system-overview">Loading...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">👥 Worker Status</div>
                <div id="worker-status">Loading...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">⚡ Throughput</div>
                <div id="throughput-metrics">Loading...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">📈 Analysis Progress</div>
                <div id="progress-metrics">Loading...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🔧 Worker Details</div>
                <div id="worker-details">Loading...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">📋 Task Completion</div>
                <div id="task-completion">Loading...</div>
            </div>
        </div>
        
        <div class="refresh-info">
            <p>🔄 Auto-refreshing every 10 seconds | Last updated: <span id="last-update">Never</span></p>
        </div>
    </div>

    <script>
        let monitor = null;
        
        function updateDashboard() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    updateSystemOverview(data.system_status);
                    updateWorkerStatus(data.worker_performance);
                    updateThroughput(data.throughput);
                    updateProgress(data.analysis_progress);
                    updateWorkerDetails(data.worker_performance);
                    updateTaskCompletion(data.task_completion);
                    
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching metrics:', error);
                });
        }
        
        function updateSystemOverview(status) {
            const html = `
                <div class="metric-value">${status.workers.active}/${status.workers.total}</div>
                <div class="metric-label">Active Workers</div>
                <hr>
                <div class="metric-value">${status.cards.analyzed.toLocaleString()}/${status.cards.total.toLocaleString()}</div>
                <div class="metric-label">Cards Analyzed (${status.cards.completion_rate})</div>
                <hr>
                <div class="metric-value">${status.tasks.pending}</div>
                <div class="metric-label">Pending Tasks</div>
            `;
            document.getElementById('system-overview').innerHTML = html;
        }
        
        function updateWorkerStatus(workerPerf) {
            const html = `
                <div class="metric-value">${workerPerf.active_workers}</div>
                <div class="metric-label">Active Workers</div>
                <hr>
                <div class="metric-value">${workerPerf.total_tasks_last_hour}</div>
                <div class="metric-label">Tasks Completed (Last Hour)</div>
                <hr>
                <div class="metric-value">${workerPerf.average_system_task_time}s</div>
                <div class="metric-label">Average Task Time</div>
            `;
            document.getElementById('worker-status').innerHTML = html;
        }
        
        function updateThroughput(throughput) {
            const lastHour = throughput.last_hour;
            const html = `
                <div class="metric-value">${lastHour.cards_per_hour}</div>
                <div class="metric-label">Cards/Hour</div>
                <hr>
                <div class="metric-value">${lastHour.components_per_hour}</div>
                <div class="metric-label">Components/Hour</div>
                <hr>
                <div class="metric-value">${lastHour.cards_completed}</div>
                <div class="metric-label">Cards Completed (Last Hour)</div>
            `;
            document.getElementById('throughput-metrics').innerHTML = html;
        }
        
        function updateProgress(progress) {
            const total = progress.total_progress;
            const percentage = total.completion_percentage;
            const html = `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
                <div style="margin-top: 10px;">
                    <div class="metric-value">${percentage}%</div>
                    <div class="metric-label">Overall Completion</div>
                </div>
                <hr>
                <div class="metric-value">${total.fully_analyzed.toLocaleString()}</div>
                <div class="metric-label">Fully Analyzed Cards</div>
            `;
            document.getElementById('progress-metrics').innerHTML = html;
        }
        
        function updateWorkerDetails(workerPerf) {
            let html = '<div class="worker-list">';
            
            for (const [workerId, stats] of Object.entries(workerPerf.worker_details)) {
                const statusClass = `status-${stats.status}`;
                html += `
                    <div class="worker-item ${statusClass}">
                        <strong>${workerId}</strong><br>
                        Status: ${stats.status} | Tasks/Hour: ${stats.tasks_per_hour_rate} | Avg Time: ${stats.average_task_time_seconds}s
                    </div>
                `;
            }
            
            html += '</div>';
            document.getElementById('worker-details').innerHTML = html;
        }
        
        function updateTaskCompletion(taskCompletion) {
            const periods = taskCompletion.period_metrics;
            let html = '';
            
            for (const [period, metrics] of Object.entries(periods)) {
                if (period === 'last_hour' || period === 'last_24_hours') {
                    html += `
                        <div class="metric-value">${metrics.completed_tasks}</div>
                        <div class="metric-label">${period.replace('_', ' ').toUpperCase()}</div>
                        <div style="font-size: 12px; color: #7f8c8d;">Rate: ${metrics.completion_rate_percentage}%</div>
                        <hr>
                    `;
                }
            }
            
            document.getElementById('task-completion').innerHTML = html;
        }
        
        // Start monitoring
        updateDashboard();
        setInterval(updateDashboard, 10000); // Update every 10 seconds
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_metrics_json(self):
        """Serve metrics as JSON"""
        try:
            metrics = monitor.collect_real_time_metrics()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(metrics, default=str, indent=2)
            self.wfile.write(response.encode())
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_worker_details(self):
        """Serve detailed worker information"""
        try:
            metrics = monitor.collect_real_time_metrics()
            worker_details = metrics['worker_performance']['worker_details']
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(worker_details, default=str, indent=2)
            self.wfile.write(response.encode())
        except Exception as e:
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass

# Global monitor instance
monitor = PerformanceMonitor()

def start_dashboard_server(port=8888):
    """Start the web dashboard server"""
    server = HTTPServer(('localhost', port), DashboardHandler)
    print(f"🌐 Performance Dashboard starting on http://localhost:{port}")
    print(f"📊 Access the dashboard at: http://localhost:{port}")
    print(f"🔌 API endpoint: http://localhost:{port}/api/metrics")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_dashboard_server()