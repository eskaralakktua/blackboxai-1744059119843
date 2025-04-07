import openai
import logging
from typing import List, Dict
import json
from ..config import settings
from ..models import AIAnalysis, WalletStats

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = settings.GPT_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

    async def analyze_wallet_patterns(
        self,
        wallet_stats: WalletStats,
        known_patterns: Dict = None
    ) -> AIAnalysis:
        """
        Analiza los patrones de una wallet usando GPT-4.
        
        Args:
            wallet_stats: Estadísticas de la wallet a analizar
            known_patterns: Patrones conocidos para comparar (opcional)
            
        Returns:
            Análisis de la wallet con observaciones e hipótesis
        """
        try:
            # Preparar el prompt con la información de la wallet
            prompt = self._create_analysis_prompt(wallet_stats, known_patterns)
            
            # Realizar la llamada a GPT-4
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Procesar y estructurar la respuesta
            analysis = self._process_gpt_response(
                response.choices[0].message.content,
                wallet_stats.address
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis GPT: {str(e)}")
            return AIAnalysis(
                wallet_address=wallet_stats.address,
                behavior_pattern="Error en análisis",
                entity_type="unknown",
                risk_score=0.0,
                observations=["Error en el análisis de GPT"],
                related_entities=[]
            )

    async def analyze_wallet_relationships(
        self,
        wallets_data: List[WalletStats],
        transaction_graph: Dict
    ) -> List[Dict]:
        """
        Analiza las relaciones entre múltiples wallets.
        
        Args:
            wallets_data: Lista de estadísticas de wallets
            transaction_graph: Grafo de transacciones entre wallets
            
        Returns:
            Lista de relaciones detectadas con explicaciones
        """
        try:
            # Preparar el prompt con la información de todas las wallets
            prompt = self._create_relationship_prompt(wallets_data, transaction_graph)
            
            # Realizar la llamada a GPT-4
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_relationship_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Procesar y estructurar la respuesta
            relationships = self._process_relationship_response(
                response.choices[0].message.content
            )
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error en análisis de relaciones: {str(e)}")
            return []

    def _get_system_prompt(self) -> str:
        """Retorna el prompt del sistema para análisis individual de wallets"""
        return """Eres un experto analista de blockchain especializado en detectar patrones 
        de comportamiento en wallets. Tu tarea es analizar la actividad de una wallet y:
        1. Identificar patrones de comportamiento
        2. Clasificar el tipo de entidad (individual, exchange, smart contract, etc.)
        3. Asignar un score de riesgo (0-1)
        4. Proporcionar observaciones relevantes
        5. Identificar posibles entidades relacionadas
        
        Responde en formato JSON con los campos: behavior_pattern, entity_type, risk_score, 
        observations (array), related_entities (array)."""

    def _get_relationship_system_prompt(self) -> str:
        """Retorna el prompt del sistema para análisis de relaciones"""
        return """Eres un experto analista de blockchain especializado en detectar relaciones 
        entre wallets. Tu tarea es analizar múltiples wallets y sus interacciones para:
        1. Identificar grupos de wallets que podrían pertenecer a la misma entidad
        2. Detectar patrones de comportamiento similares
        3. Identificar relaciones sospechosas o inusuales
        4. Proporcionar explicaciones detalladas de las relaciones encontradas
        
        Responde en formato JSON con un array de relaciones, cada una con los campos:
        wallets_involved (array), relationship_type, confidence_score, explanation."""

    def _create_analysis_prompt(
        self,
        wallet_stats: WalletStats,
        known_patterns: Dict = None
    ) -> str:
        """Crea el prompt para análisis individual de wallet"""
        prompt = f"""Analiza la siguiente wallet:
        
        Dirección: {wallet_stats.address}
        Blockchain: {wallet_stats.blockchain}
        Total enviado (USD): ${wallet_stats.total_sent_usd:,.2f}
        Total recibido (USD): ${wallet_stats.total_received_usd:,.2f}
        Número de transacciones: {wallet_stats.transaction_count}
        
        Tokens únicos: {len(wallet_stats.unique_tokens)}
        Contratos más frecuentes: {', '.join(wallet_stats.most_frequent_contracts[:5])}
        
        Primera transacción: {wallet_stats.first_transaction_date}
        Última transacción: {wallet_stats.last_transaction_date}
        
        Distribución horaria de actividad:
        {json.dumps(wallet_stats.interaction_hours)}
        """
        
        if known_patterns:
            prompt += f"\n\nPatrones conocidos para comparar:\n{json.dumps(known_patterns)}"
        
        return prompt

    def _create_relationship_prompt(
        self,
        wallets_data: List[WalletStats],
        transaction_graph: Dict
    ) -> str:
        """Crea el prompt para análisis de relaciones entre wallets"""
        prompt = "Analiza las siguientes wallets y sus relaciones:\n\n"
        
        # Añadir información de cada wallet
        for wallet in wallets_data:
            prompt += f"""
            Wallet: {wallet.address}
            - Total movido (USD): ${wallet.total_sent_usd + wallet.total_received_usd:,.2f}
            - Transacciones: {wallet.transaction_count}
            - Tokens principales: {', '.join([t.symbol for t in wallet.unique_tokens[:3]])}
            """
        
        # Añadir información del grafo de transacciones
        prompt += "\nRelaciones detectadas en transacciones:\n"
        prompt += json.dumps(transaction_graph, indent=2)
        
        return prompt

    def _process_gpt_response(self, response: str, wallet_address: str) -> AIAnalysis:
        """Procesa la respuesta de GPT y la convierte en un objeto AIAnalysis"""
        try:
            # Intentar parsear la respuesta como JSON
            analysis_dict = json.loads(response)
            
            return AIAnalysis(
                wallet_address=wallet_address,
                behavior_pattern=analysis_dict.get("behavior_pattern", "Unknown"),
                entity_type=analysis_dict.get("entity_type", "unknown"),
                risk_score=float(analysis_dict.get("risk_score", 0.0)),
                observations=analysis_dict.get("observations", []),
                related_entities=analysis_dict.get("related_entities", [])
            )
            
        except json.JSONDecodeError:
            logger.error("Error decodificando respuesta JSON de GPT")
            return AIAnalysis(
                wallet_address=wallet_address,
                behavior_pattern="Error en formato",
                entity_type="unknown",
                risk_score=0.0,
                observations=["Error procesando respuesta de GPT"],
                related_entities=[]
            )
        except Exception as e:
            logger.error(f"Error procesando respuesta de GPT: {str(e)}")
            return AIAnalysis(
                wallet_address=wallet_address,
                behavior_pattern="Error en procesamiento",
                entity_type="unknown",
                risk_score=0.0,
                observations=["Error interno procesando análisis"],
                related_entities=[]
            )

    def _process_relationship_response(self, response: str) -> List[Dict]:
        """Procesa la respuesta de GPT sobre relaciones entre wallets"""
        try:
            # Intentar parsear la respuesta como JSON
            relationships = json.loads(response)
            
            # Validar y limpiar cada relación
            cleaned_relationships = []
            for rel in relationships:
                if isinstance(rel, dict) and all(
                    k in rel for k in [
                        "wallets_involved",
                        "relationship_type",
                        "confidence_score",
                        "explanation"
                    ]
                ):
                    cleaned_relationships.append({
                        "wallets_involved": rel["wallets_involved"],
                        "relationship_type": rel["relationship_type"],
                        "confidence_score": float(rel["confidence_score"]),
                        "explanation": rel["explanation"]
                    })
            
            return cleaned_relationships
            
        except json.JSONDecodeError:
            logger.error("Error decodificando respuesta JSON de GPT (relaciones)")
            return []
        except Exception as e:
            logger.error(f"Error procesando respuesta de relaciones: {str(e)}")
            return []