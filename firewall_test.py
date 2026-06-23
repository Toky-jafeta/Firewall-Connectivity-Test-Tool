#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée principal du test de connectivité firewall.
Gère les arguments en ligne de commande et orchestre les modules.
"""

import argparse
import logging
import sys
import os
from listener import Listener
from tester import Tester
from reporter import Reporter
from utils import get_local_ip

def setup_logging():
    """
    Configure le logging : fichier + console.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "firewall_test.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    parser = argparse.ArgumentParser(
        description="Outil de test de connectivité firewall (TCP, UDP, ICMP)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--listen",
        action="store_true",
        help="Mode Listener : écoute sur tous les ports définis"
    )
    group.add_argument(
        "--target",
        help="Mode Test : adresse IP de la destination à tester"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Timeout en secondes (défaut : 3.0)"
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Répertoire de sortie des rapports (défaut : reports)"
    )
    args = parser.parse_args()

    setup_logging()
    logging.info("Démarrage de l'outil de test firewall")

    if args.listen:
        logging.info("Mode Listener activé")
        listener = Listener()
        try:
            listener.start()
        except KeyboardInterrupt:
            logging.info("Listener interrompu par l'utilisateur")
            listener.stop()
        except Exception as e:
            logging.error(f"Erreur du listener : {e}")
    else:
        target = args.target
        if not target:
            logging.error("L'adresse IP cible est requise en mode test")
            sys.exit(1)
        logging.info(f"Mode Test activé, cible : {target}")
        source_ip = get_local_ip()
        logging.info(f"IP source détectée : {source_ip}")

        tester = Tester(target, timeout=args.timeout)
        results = tester.run_tests()
        logging.info("Tests terminés.")

        reporter = Reporter(results, source_ip, target, output_dir=args.output_dir)
        csv_file = reporter.generate_csv()
        html_file = reporter.generate_html()
        logging.info(f"Rapport CSV généré : {csv_file}")
        logging.info(f"Rapport HTML généré : {html_file}")

        print("\n" + "=" * 50)
        print("FIREWALL CONNECTIVITY TEST")
        print("=" * 50 + "\n")
        for protocol, port, status in results:
            print(f"{protocol}/{port:<5} {status}")

        total = len(results)
        passed = sum(1 for _, _, s in results if s == 'PASS')
        failed = sum(1 for _, _, s in results if s == 'FAIL')
        timeout = sum(1 for _, _, s in results if s == 'TIMEOUT')
        error = sum(1 for _, _, s in results if s == 'ERROR')
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"\nTOTAL TESTS : {total}")
        print(f"PASSED      : {passed}")
        print(f"FAILED      : {failed}")
        print(f"TIMEOUT     : {timeout}")
        print(f"ERROR       : {error}")

        print("\nBLOCKED FLOWS")
        for protocol, port, status in results:
            if status in ('FAIL', 'TIMEOUT', 'ERROR'):
                print(f"{protocol}/{port}")
        print(f"\nRapports sauvegardés dans : {csv_file}, {html_file}")

if __name__ == "__main__":
    main()