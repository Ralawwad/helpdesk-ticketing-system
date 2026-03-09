from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

TICKETS_FILE = 'tickets.json'

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=2)

def categorize_ticket(description):
    description = description.lower()
    if any(word in description for word in ['network', 'internet', 'wifi', 'connection', 'vpn']):
        return 'Network'
    elif any(word in description for word in ['hardware', 'monitor', 'keyboard', 'mouse', 'printer', 'computer']):
        return 'Hardware'
    elif any(word in description for word in ['software', 'install', 'crash', 'error', 'update', 'app']):
        return 'Software'
    elif any(word in description for word in ['password', 'login', 'account', 'locked', 'access']):
        return 'Account Access'
    else:
        return 'General'

def assign_priority(description):
    description = description.lower()
    if any(word in description for word in ['urgent', 'critical', 'down', 'cant work', "can't work", 'emergency']):
        return 'High'
    elif any(word in description for word in ['slow', 'intermittent', 'sometimes', 'occasional']):
        return 'Low'
    else:
        return 'Medium'

def suggest_solution(category):
    solutions = {
        'Network': 'Check network cable connections, restart router, run ipconfig /flushdns, check VPN settings.',
        'Hardware': 'Check all physical connections, restart device, check Device Manager for errors.',
        'Software': 'Restart the application, check for updates, reinstall if necessary, check Event Viewer for errors.',
        'Account Access': 'Verify credentials, check if account is locked in Active Directory, reset password if needed.',
        'General': 'Document the issue, gather more information, and escalate if necessary.'
    }
    return solutions.get(category, 'Please investigate and document findings.')

def generate_auto_reply(ticket):
    replies = {
        'Network': f"Hi {ticket['name']}, thank you for contacting IT Support. We have received your network connectivity ticket. Our team will check your connection settings, run diagnostics, and restore your access as soon as possible. Expected resolution time: 1-2 hours.",
        'Hardware': f"Hi {ticket['name']}, thank you for contacting IT Support. We have received your hardware issue ticket. A technician will inspect your equipment and check all connections. Expected resolution time: 2-4 hours.",
        'Software': f"Hi {ticket['name']}, thank you for contacting IT Support. We have received your software issue ticket. Our team will review the application logs and push a fix or reinstall as needed. Expected resolution time: 1-3 hours.",
        'Account Access': f"Hi {ticket['name']}, thank you for contacting IT Support. We have received your account access ticket. Our team will verify your credentials and check Active Directory immediately. Expected resolution time: 30 minutes.",
        'General': f"Hi {ticket['name']}, thank you for contacting IT Support. We have received your ticket and will investigate shortly. Expected resolution time: 4 hours."
    }
    return replies.get(ticket['category'], replies['General'])

@app.route('/')
def index():
    tickets = load_tickets()
    category_counts = {'Network': 0, 'Hardware': 0, 'Software': 0, 'Account Access': 0, 'General': 0}
    for ticket in tickets:
        cat = ticket.get('category', 'General')
        if cat in category_counts:
            category_counts[cat] += 1
    most_common_category = max(category_counts, key=category_counts.get) if tickets else 'N/A'
    return render_template('index.html', tickets=tickets, category_counts=category_counts, most_common_category=most_common_category)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        tickets = load_tickets()
        description = request.form['description']
        category = categorize_ticket(description)
        priority = assign_priority(description)
        solution = suggest_solution(category)
        ticket = {
            'id': len(tickets) + 1,
            'name': request.form['name'],
            'email': request.form['email'],
            'description': description,
            'category': category,
            'priority': priority,
            'solution': solution,
            'status': 'Open',
            'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'resolved_at': None,
            'auto_reply': None
        }
        ticket['auto_reply'] = generate_auto_reply(ticket)
        tickets.append(ticket)
        save_tickets(tickets)
        return redirect(url_for('index'))
    return render_template('submit.html')

@app.route('/resolve/<int:ticket_id>')
def resolve(ticket_id):
    tickets = load_tickets()
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            ticket['status'] = 'Resolved'
            ticket['resolved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    save_tickets(tickets)
    return redirect(url_for('index'))

@app.route('/delete/<int:ticket_id>')
def delete(ticket_id):
    tickets = load_tickets()
    tickets = [t for t in tickets if t['id'] != ticket_id]
    save_tickets(tickets)
    return redirect(url_for('index'))

@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    tickets = load_tickets()
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if not ticket:
        return redirect(url_for('index'))
    return render_template('ticket.html', ticket=ticket)

if __name__ == '__main__':
    app.run(debug=True)