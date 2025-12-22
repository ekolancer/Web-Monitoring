from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from config import OUTPUT_DIR

app = Flask(__name__)
CORS(app)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current monitoring status"""
    try:
        # Read latest scan results
        results_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith('scan_') and f.endswith('.json')]
        if not results_files:
            return jsonify({'status': 'No data available'})

        latest_file = max(results_files)
        with open(os.path.join(OUTPUT_DIR, latest_file), 'r') as f:
            data = json.load(f)

        # Calculate summary
        total_sites = len(data)
        healthy = sum(1 for site in data if site.get('Status') == 'HEALTHY')
        issues = total_sites - healthy

        return jsonify({
            'total_sites': total_sites,
            'healthy': healthy,
            'issues': issues,
            'last_scan': latest_file.replace('scan_', '').replace('.json', ''),
            'data': data[:10]  # Return first 10 results
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/history')
def get_history():
    """Get historical data for charts"""
    try:
        results_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.startswith('scan_') and f.endswith('.json')])

        history = []
        for file in results_files[-30:]:  # Last 30 scans
            with open(os.path.join(OUTPUT_DIR, file), 'r') as f:
                data = json.load(f)
                timestamp = file.replace('scan_', '').replace('.json', '').replace('_', ' ')
                healthy = sum(1 for site in data if site.get('Status') == 'HEALTHY')
                total = len(data)
                history.append({
                    'timestamp': timestamp,
                    'healthy': healthy,
                    'total': total,
                    'uptime_percent': (healthy / total * 100) if total > 0 else 0
                })

        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/security')
def get_security():
    """Get security check results"""
    try:
        # This would integrate with security scan results
        # For now, return mock data
        return jsonify({
            'critical': 2,
            'high': 5,
            'medium': 12,
            'low': 25,
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)