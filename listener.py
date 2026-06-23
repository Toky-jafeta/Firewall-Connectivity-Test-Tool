# -*- coding: utf-8 -*-
"""
Module Listener : écoute sur tous les ports TCP et UDP spécifiés,
répond automatiquement aux requêtes.
Utilise le multithreading.
"""

import socket
import threading
import logging
from config import TCP_PORTS, UDP_PORTS, RESPONSE_MESSAGE

class Listener:
    def __init__(self):
        self.tcp_sockets = []
        self.udp_sockets = []
        self.threads = []
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def start(self):
        """
        Démarre tous les threads d'écoute TCP et UDP.
        """
        logging.info("Démarrage du listener sur tous les ports TCP et UDP...")
        for port in TCP_PORTS:
            t = threading.Thread(target=self.tcp_listen, args=(port,), daemon=True)
            t.start()
            self.threads.append(t)
        for port in UDP_PORTS:
            t = threading.Thread(target=self.udp_listen, args=(port,), daemon=True)
            t.start()
            self.threads.append(t)
        logging.info("Listener démarré. Appuyez sur Ctrl+C pour arrêter.")
        for t in self.threads:
            t.join()

    def tcp_listen(self, port):
        """
        Thread d'écoute TCP pour un port donné.
        """
        server_socket = None
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('', port))
            server_socket.listen(5)
            with self.lock:
                self.tcp_sockets.append(server_socket)
            logging.info(f"TCP en écoute sur le port {port}")
            while not self.stop_event.is_set():
                try:
                    server_socket.settimeout(1.0)
                    client_socket, addr = server_socket.accept()
                    logging.info(f"Connexion TCP reçue de {addr} sur le port {port}")
                    handler = threading.Thread(
                        target=self.handle_tcp,
                        args=(client_socket, addr, port),
                        daemon=True
                    )
                    handler.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if not self.stop_event.is_set():
                        logging.error(f"Erreur lors de l'accept TCP sur le port {port}: {e}")
                    break
        except Exception as e:
            logging.error(f"Impossible de démarrer l'écoute TCP sur le port {port}: {e}")
        finally:
            if server_socket:
                server_socket.close()
                with self.lock:
                    if server_socket in self.tcp_sockets:
                        self.tcp_sockets.remove(server_socket)

    def handle_tcp(self, client_socket, addr, port):
        """
        Gère une connexion TCP entrante : reçoit les données et répond.
        """
        try:
            data = client_socket.recv(1024)
            if data:
                logging.info(f"Données TCP reçues de {addr}: {data}")
                client_socket.sendall(RESPONSE_MESSAGE)
            client_socket.close()
        except Exception as e:
            logging.error(f"Erreur lors du traitement TCP de {addr}: {e}")

    def udp_listen(self, port):
        """
        Thread d'écoute UDP pour un port donné.
        """
        server_socket = None
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('', port))
            with self.lock:
                self.udp_sockets.append(server_socket)
            logging.info(f"UDP en écoute sur le port {port}")
            while not self.stop_event.is_set():
                try:
                    server_socket.settimeout(1.0)
                    data, addr = server_socket.recvfrom(1024)
                    logging.info(f"Données UDP reçues de {addr} sur le port {port}: {data}")
                    server_socket.sendto(RESPONSE_MESSAGE, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if not self.stop_event.is_set():
                        logging.error(f"Erreur lors de la réception UDP sur le port {port}: {e}")
                    break
        except Exception as e:
            logging.error(f"Impossible de démarrer l'écoute UDP sur le port {port}: {e}")
        finally:
            if server_socket:
                server_socket.close()
                with self.lock:
                    if server_socket in self.udp_sockets:
                        self.udp_sockets.remove(server_socket)

    def stop(self):
        """
        Arrête le listener en fermant toutes les sockets et en joignant les threads.
        """
        logging.info("Arrêt du listener...")
        self.stop_event.set()
        for sock in self.tcp_sockets + self.udp_sockets:
            try:
                sock.close()
            except:
                pass
        for t in self.threads:
            t.join(timeout=2.0)
        logging.info("Listener arrêté.")