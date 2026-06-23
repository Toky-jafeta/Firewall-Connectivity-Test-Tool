# -*- coding: utf-8 -*-
"""
Module Tester : envoie des requêtes vers la cible pour chaque port (TCP, UDP)
et effectue un ping ICMP.
Utilise le multithreading pour accélérer les tests.
"""

import socket
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import TCP_PORTS, UDP_PORTS, REQUEST_MESSAGE, RESPONSE_MESSAGE, DEFAULT_TIMEOUT
from utils import ping, get_local_ip

class Tester:
    def __init__(self, target_ip, timeout=DEFAULT_TIMEOUT):
        self.target_ip = target_ip
        self.timeout = timeout
        self.results = []
        self.lock = threading.Lock()

    def run_tests(self):
        """
        Lance tous les tests : ICMP, TCP, UDP.
        Retourne la liste des résultats.
        """
        self.test_icmp()
        self.test_tcp_ports()
        self.test_udp_ports()
        return self.results

    def test_icmp(self):
        """
        Test ICMP (ping).
        """
        status = "PASS" if ping(self.target_ip, self.timeout) else "FAIL"
        with self.lock:
            self.results.append(("ICMP", 0, status))
        logging.info(f"ICMP : {status}")

    def test_tcp_ports(self):
        """
        Teste tous les ports TCP en parallèle avec un ThreadPoolExecutor.
        """
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_port = {
                executor.submit(self.test_tcp_port, port): port
                for port in TCP_PORTS
            }
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    status = future.result()
                    with self.lock:
                        self.results.append(("TCP", port, status))
                    logging.info(f"TCP/{port} : {status}")
                except Exception as e:
                    logging.error(f"Erreur lors du test TCP/{port} : {e}")
                    with self.lock:
                        self.results.append(("TCP", port, "ERROR"))

    def test_tcp_port(self, port):
        """
        Teste un port TCP spécifique.
        Retourne 'PASS', 'FAIL' ou 'TIMEOUT'.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            start = time.time()
            sock.connect((self.target_ip, port))
            sock.sendall(REQUEST_MESSAGE)
            data = sock.recv(1024)
            if data == RESPONSE_MESSAGE:
                status = "PASS"
            else:
                status = "FAIL"
            sock.close()
            return status
        except socket.timeout:
            return "TIMEOUT"
        except ConnectionRefusedError:
            return "FAIL"
        except Exception as e:
            logging.debug(f"TCP/{port} exception: {e}")
            return "FAIL"

    def test_udp_ports(self):
        """
        Teste tous les ports UDP en parallèle.
        """
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_port = {
                executor.submit(self.test_udp_port, port): port
                for port in UDP_PORTS
            }
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    status = future.result()
                    with self.lock:
                        self.results.append(("UDP", port, status))
                    logging.info(f"UDP/{port} : {status}")
                except Exception as e:
                    logging.error(f"Erreur lors du test UDP/{port} : {e}")
                    with self.lock:
                        self.results.append(("UDP", port, "ERROR"))

    def test_udp_port(self, port):
        """
        Teste un port UDP spécifique.
        Retourne 'PASS', 'FAIL' ou 'TIMEOUT'.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            sock.sendto(REQUEST_MESSAGE, (self.target_ip, port))
            data, addr = sock.recvfrom(1024)
            if data == RESPONSE_MESSAGE:
                status = "PASS"
            else:
                status = "FAIL"
            sock.close()
            return status
        except socket.timeout:
            return "TIMEOUT"
        except (ConnectionRefusedError, OSError) as e:
            return "FAIL"
        except Exception as e:
            logging.debug(f"UDP/{port} exception: {e}")
            return "FAIL"