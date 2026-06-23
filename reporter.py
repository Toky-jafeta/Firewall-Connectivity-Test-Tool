# -*- coding: utf-8 -*-
"""
Module Reporter : génère des rapports CSV et HTML à partir des résultats de test.
"""

import csv
import datetime
import os
from config import TCP_PORTS, UDP_PORTS

class Reporter:
    def __init__(self, results, source_ip, target_ip, output_dir="reports"):
        self.results = results
        self.source_ip = source_ip
        self.target_ip = target_ip
        self.timestamp = datetime.datetime.now()
        self.output_dir = output_dir
        # Créer le répertoire de sortie s'il n'existe pas
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_csv(self, filename=None):
        """
        Génère un fichier CSV.
        """
        if not filename:
            filename = f"firewall_test_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Protocol', 'Port', 'Status'])
            for protocol, port, status in self.results:
                writer.writerow([protocol, port, status])
        return filepath

    def generate_html(self, filename=None):
        """
        Génère un rapport HTML moderne.
        """
        if not filename:
            filename = f"firewall_test_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)

        # Statistiques
        total = len(self.results)
        passed = sum(1 for _, _, s in self.results if s == 'PASS')
        failed = sum(1 for _, _, s in self.results if s == 'FAIL')
        timeout = sum(1 for _, _, s in self.results if s == 'TIMEOUT')
        error = sum(1 for _, _, s in self.results if s == 'ERROR')

        # Flux bloqués (FAIL, TIMEOUT, ERROR)
        blocked = [(p, port) for p, port, s in self.results if s in ('FAIL', 'TIMEOUT', 'ERROR')]

        # Construction du HTML
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de test de connectivité firewall</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f4f6f8;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .info {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
        }}
        .info-item {{
            margin-right: 30px;
        }}
        .info-item strong {{
            font-weight: 600;
        }}
        .summary {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: space-around;
            background: #e9ecef;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .summary-item {{
            text-align: center;
            min-width: 80px;
        }}
        .summary-item .number {{
            font-size: 2.2em;
            font-weight: bold;
        }}
        .summary-item .label {{
            font-size: 0.9em;
            color: #555;
        }}
        .summary-item.passed .number {{ color: #27ae60; }}
        .summary-item.failed .number {{ color: #e74c3c; }}
        .summary-item.timeout .number {{ color: #f39c12; }}
        .summary-item.error .number {{ color: #8e44ad; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #34495e;
            color: white;
        }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .status-PASS {{ color: #27ae60; font-weight: bold; }}
        .status-FAIL {{ color: #e74c3c; font-weight: bold; }}
        .status-TIMEOUT {{ color: #f39c12; font-weight: bold; }}
        .status-ERROR {{ color: #8e44ad; font-weight: bold; }}

        .blocked-list {{
            list-style-type: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .blocked-list li {{
            background: #f8d7da;
            padding: 5px 12px;
            border-radius: 20px;
            font-family: monospace;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>Rapport de test de connectivité firewall</h1>
    <div class="info">
        <div class="info-item"><strong>Date du test :</strong> {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</div>
        <div class="info-item"><strong>IP source :</strong> {self.source_ip}</div>
        <div class="info-item"><strong>IP destination :</strong> {self.target_ip}</div>
    </div>

    <div class="summary">
        <div class="summary-item">
            <div class="number">{total}</div>
            <div class="label">Total</div>
        </div>
        <div class="summary-item passed">
            <div class="number">{passed}</div>
            <div class="label">Passés</div>
        </div>
        <div class="summary-item failed">
            <div class="number">{failed}</div>
            <div class="label">Échecs</div>
        </div>
        <div class="summary-item timeout">
            <div class="number">{timeout}</div>
            <div class="label">Timeouts</div>
        </div>
        <div class="summary-item error">
            <div class="number">{error}</div>
            <div class="label">Erreurs</div>
        </div>
    </div>

    <h2>Détail des résultats</h2>
    <table>
        <thead>
            <tr><th>Protocole</th><th>Port</th><th>Statut</th></tr>
        </thead>
        <tbody>
"""
        for protocol, port, status in self.results:
            status_class = f"status-{status}"
            html += f"<tr><td>{protocol}</td><td>{port}</td><td class='{status_class}'>{status}</td></tr>\n"

        html += """
        </tbody>
    </table>

    <h2>Flux bloqués</h2>
"""
        if blocked:
            html += "<ul class='blocked-list'>\n"
            for protocol, port in blocked:
                html += f"<li>{protocol}/{port}</li>\n"
            html += "</ul>\n"
        else:
            html += "<p>Aucun flux bloqué détecté.</p>\n"

        html += f"""
    <div class="footer">
        Rapport généré par Firewall Connectivity Test Tool le {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}
    </div>
</div>
</body>
</html>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath