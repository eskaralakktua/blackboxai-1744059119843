from typing import List, Dict, Set
import networkx as nx
import json
import logging
from ..models import Transaction, GraphNode, GraphEdge, GraphData
from ..utils import format_wallet_address, calculate_similarity_score

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_properties = {}
        self.edge_properties = {}

    def create_transaction_graph(
        self,
        transactions: List[Transaction],
        wallet_stats: Dict
    ) -> GraphData:
        """
        Crea un grafo dirigido de transacciones entre wallets.
        
        Args:
            transactions: Lista de transacciones
            wallet_stats: Estadísticas de las wallets analizadas
            
        Returns:
            GraphData con nodos y aristas del grafo
        """
        try:
            # Reiniciar el grafo
            self.graph.clear()
            self.node_properties.clear()
            self.edge_properties.clear()
            
            # Procesar transacciones para crear el grafo
            self._process_transactions(transactions, wallet_stats)
            
            # Calcular métricas adicionales
            self._calculate_node_metrics()
            self._calculate_edge_weights()
            
            # Convertir el grafo a formato GraphData
            return self._convert_to_graph_data()
            
        except Exception as e:
            logger.error(f"Error creando grafo de transacciones: {str(e)}")
            return GraphData(nodes=[], edges=[])

    def _process_transactions(
        self,
        transactions: List[Transaction],
        wallet_stats: Dict
    ):
        """Procesa las transacciones para crear nodos y aristas"""
        analyzed_addresses = set(wallet_stats.keys())
        
        for tx in transactions:
            from_addr = tx.from_address.lower()
            to_addr = tx.to_address.lower()
            
            # Añadir nodos si no existen
            if from_addr not in self.graph:
                self._add_node(from_addr, analyzed_addresses)
            if to_addr not in self.graph:
                self._add_node(to_addr, analyzed_addresses)
            
            # Añadir o actualizar arista
            if self.graph.has_edge(from_addr, to_addr):
                self.edge_properties[(from_addr, to_addr)]["transactions"].append({
                    "hash": tx.hash,
                    "value": tx.usd_value,
                    "timestamp": tx.timestamp.isoformat(),
                    "token": tx.token_symbol
                })
            else:
                self.graph.add_edge(from_addr, to_addr)
                self.edge_properties[(from_addr, to_addr)] = {
                    "transactions": [{
                        "hash": tx.hash,
                        "value": tx.usd_value,
                        "timestamp": tx.timestamp.isoformat(),
                        "token": tx.token_symbol
                    }],
                    "total_value": 0,
                    "transaction_count": 0
                }

    def _add_node(self, address: str, analyzed_addresses: Set[str]):
        """Añade un nodo al grafo con sus propiedades iniciales"""
        self.graph.add_node(address)
        self.node_properties[address] = {
            "address": address,
            "label": format_wallet_address(address),
            "is_analyzed": address in analyzed_addresses,
            "total_sent": 0,
            "total_received": 0,
            "transaction_count": 0,
            "degree_centrality": 0
        }

    def _calculate_node_metrics(self):
        """Calcula métricas adicionales para los nodos"""
        try:
            # Calcular grado de centralidad
            centrality = nx.degree_centrality(self.graph)
            
            for node in self.graph.nodes():
                # Actualizar centralidad
                self.node_properties[node]["degree_centrality"] = centrality[node]
                
                # Calcular totales de transacciones
                total_sent = sum(
                    sum(tx["value"] for tx in self.edge_properties[(node, succ)]["transactions"])
                    for succ in self.graph.successors(node)
                )
                
                total_received = sum(
                    sum(tx["value"] for tx in self.edge_properties[(pred, node)]["transactions"])
                    for pred in self.graph.predecessors(node)
                )
                
                self.node_properties[node].update({
                    "total_sent": total_sent,
                    "total_received": total_received,
                    "transaction_count": self.graph.in_degree(node) + self.graph.out_degree(node)
                })
                
        except Exception as e:
            logger.error(f"Error calculando métricas de nodos: {str(e)}")

    def _calculate_edge_weights(self):
        """Calcula pesos y métricas adicionales para las aristas"""
        try:
            for edge in self.graph.edges():
                from_addr, to_addr = edge
                transactions = self.edge_properties[edge]["transactions"]
                
                # Calcular totales
                total_value = sum(tx["value"] for tx in transactions)
                transaction_count = len(transactions)
                
                self.edge_properties[edge].update({
                    "total_value": total_value,
                    "transaction_count": transaction_count,
                    "weight": total_value * transaction_count  # Peso combinado
                })
                
        except Exception as e:
            logger.error(f"Error calculando pesos de aristas: {str(e)}")

    def _convert_to_graph_data(self) -> GraphData:
        """Convierte el grafo interno a formato GraphData"""
        try:
            nodes = []
            edges = []
            
            # Convertir nodos
            for node in self.graph.nodes():
                props = self.node_properties[node]
                nodes.append(GraphNode(
                    id=node,
                    label=props["label"],
                    size=int(props["transaction_count"] / 2) + 20,  # Tamaño base + actividad
                    color="#ff7675" if props["is_analyzed"] else "#74b9ff",  # Rojo para analizados, azul para externos
                    properties=props
                ))
            
            # Convertir aristas
            for edge in self.graph.edges():
                from_addr, to_addr = edge
                props = self.edge_properties[edge]
                edges.append(GraphEdge(
                    source=from_addr,
                    target=to_addr,
                    weight=props["weight"],
                    properties=props
                ))
            
            return GraphData(nodes=nodes, edges=edges)
            
        except Exception as e:
            logger.error(f"Error convirtiendo a GraphData: {str(e)}")
            return GraphData(nodes=[], edges=[])

    def detect_clusters(self) -> List[Dict]:
        """
        Detecta clusters de wallets que podrían estar relacionadas.
        
        Returns:
            Lista de clusters con sus propiedades
        """
        try:
            # Convertir a grafo no dirigido para análisis de comunidades
            undirected = self.graph.to_undirected()
            
            # Detectar comunidades usando el algoritmo de Louvain
            communities = nx.community.louvain_communities(undirected)
            
            # Analizar cada comunidad
            clusters = []
            for i, community in enumerate(communities):
                if len(community) > 1:  # Solo considerar grupos de 2 o más wallets
                    # Calcular propiedades del cluster
                    cluster_info = {
                        "id": i,
                        "wallets": list(community),
                        "size": len(community),
                        "total_volume": sum(
                            self.node_properties[node]["total_sent"] +
                            self.node_properties[node]["total_received"]
                            for node in community
                        ),
                        "internal_transactions": self._count_internal_transactions(community),
                        "similarity_score": self._calculate_cluster_similarity(community)
                    }
                    clusters.append(cluster_info)
            
            return sorted(clusters, key=lambda x: x["similarity_score"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error detectando clusters: {str(e)}")
            return []

    def _count_internal_transactions(self, community: Set[str]) -> int:
        """Cuenta el número de transacciones entre miembros de la comunidad"""
        count = 0
        for from_addr in community:
            for to_addr in community:
                if self.graph.has_edge(from_addr, to_addr):
                    count += len(self.edge_properties[(from_addr, to_addr)]["transactions"])
        return count

    def _calculate_cluster_similarity(self, community: Set[str]) -> float:
        """Calcula un score de similitud para los miembros del cluster"""
        if len(community) < 2:
            return 0.0
            
        try:
            # Calcular similitud promedio entre todos los pares
            similarities = []
            for addr1 in community:
                for addr2 in community:
                    if addr1 < addr2:  # Evitar duplicados
                        score = calculate_similarity_score(
                            self.node_properties[addr1],
                            self.node_properties[addr2]
                        )
                        similarities.append(score)
            
            return sum(similarities) / len(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando similitud de cluster: {str(e)}")
            return 0.0

    def export_graph_json(self) -> str:
        """
        Exporta el grafo en formato JSON compatible con D3.js/Cytoscape.js
        
        Returns:
            String JSON con el grafo
        """
        try:
            graph_data = self._convert_to_graph_data()
            return json.dumps({
                "nodes": [node.dict() for node in graph_data.nodes],
                "edges": [edge.dict() for edge in graph_data.edges]
            })
        except Exception as e:
            logger.error(f"Error exportando grafo a JSON: {str(e)}")
            return json.dumps({"nodes": [], "edges": []})