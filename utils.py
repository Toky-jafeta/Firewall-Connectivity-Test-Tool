# -*- coding: utf-8 -*-
"""
Fonctions utilitaires : détection IP locale, ping ICMP.
"""

import socket
import subprocess
import platform
import logging

def get_local_ip():
    """
    Retourne l'adresse IP locale de l'interface par défaut.
    """
    try:
        # Se connecter à un serveur DNS connu (pas de données envoyées)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback
        return socket.gethostbyname(socket.gethostname())

def ping(host, timeout=3):
    """
    Envoie une requête ICMP Echo Request vers l'hôte.
    Retourne True si une réponse est reçue dans le timeout, False sinon.
    """
    system = platform.system().lower()
    if system == 'windows':
        # ping -n 1 -w timeout_ms host
        timeout_ms = int(timeout * 1000)
        cmd = ['ping', '-n', '1', '-w', str(timeout_ms), host]
    else:
        # Linux / Mac : ping -c 1 -W timeout_sec host
        cmd = ['ping', '-c', '1', '-W', str(timeout), host]
    try:
        # On vérifie seulement le code de retour (0 = succès)
        ret = subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ret == 0
    except Exception as e:
        logging.debug(f"Ping error: {e}")
        return False