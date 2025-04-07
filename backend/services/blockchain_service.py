from typing import List, Dict, Optional
import logging
from web3 import Web3
from moralis import evm_api
import asyncio
from datetime import datetime, timedelta
from ..config import settings
from ..models import Transaction, TokenInfo
import aiohttp
import json

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.moralis_api_key = settings.MORALIS_API_KEY
        self.web3_connections = {}
        self.initialize_web3_connections()

    def initialize_web3_connections(self):
        """Inicializa conexiones Web3 para cada blockchain soportada"""
        for chain, config in settings.SUPPORTED_CHAINS.items():
            try:
                self.web3_connections[chain] = Web3(Web3.HTTPProvider(config['rpc_url']))
                logger.info(f"Conexión Web3 inicializada para {chain}")
            except Exception as e:
                logger.error(f"Error inicializando Web3 para {chain}: {str(e)}")

    async def get_wallet_transactions(
        self,
        address: str,
        blockchain: str,
        days: int = 30
    ) -> List[Transaction]:
        """
        Obtiene las transacciones de una wallet usando Moralis API.
        
        Args:
            address: Dirección de la wallet
            blockchain: Nombre de la blockchain
            days: Número de días hacia atrás para buscar
            
        Returns:
            Lista de transacciones
        """
        try:
            # Configurar parámetros para Moralis
            params = {
                "address": address,
                "chain": blockchain,
                "from_date": (datetime.now() - timedelta(days=days)).isoformat()
            }

            # Obtener transacciones normales
            normal_txs = await self._get_moralis_transactions(params)
            
            # Obtener transferencias de tokens ERC20
            erc20_txs = await self._get_moralis_token_transfers(params)
            
            # Combinar y procesar transacciones
            all_transactions = await self._process_transactions(
                normal_txs + erc20_txs,
                blockchain
            )
            
            return all_transactions
            
        except Exception as e:
            logger.error(f"Error obteniendo transacciones: {str(e)}")
            return []

    async def _get_moralis_transactions(self, params: Dict) -> List[Dict]:
        """Obtiene transacciones normales usando Moralis API"""
        try:
            result = await evm_api.transaction.get_wallet_transactions(
                api_key=self.moralis_api_key,
                params=params
            )
            return result.get("result", [])
        except Exception as e:
            logger.error(f"Error en Moralis API (transactions): {str(e)}")
            return []

    async def _get_moralis_token_transfers(self, params: Dict) -> List[Dict]:
        """Obtiene transferencias de tokens usando Moralis API"""
        try:
            result = await evm_api.token.get_wallet_token_transfers(
                api_key=self.moralis_api_key,
                params=params
            )
            return result.get("result", [])
        except Exception as e:
            logger.error(f"Error en Moralis API (token transfers): {str(e)}")
            return []

    async def _process_transactions(
        self,
        transactions: List[Dict],
        blockchain: str
    ) -> List[Transaction]:
        """Procesa y normaliza las transacciones"""
        processed_txs = []
        
        for tx in transactions:
            try:
                # Obtener precio histórico para el token
                token_price = await self._get_historical_token_price(
                    tx.get('token_address'),
                    blockchain,
                    tx.get('block_timestamp')
                )
                
                # Crear objeto Transaction
                processed_tx = Transaction(
                    hash=tx['hash'],
                    from_address=tx['from_address'],
                    to_address=tx['to_address'],
                    value=float(tx['value']),
                    timestamp=datetime.fromisoformat(tx['block_timestamp']),
                    token_address=tx.get('token_address'),
                    token_symbol=tx.get('token_symbol'),
                    token_decimals=int(tx.get('token_decimals', 18)),
                    usd_value=self._calculate_usd_value(
                        float(tx['value']),
                        token_price,
                        int(tx.get('token_decimals', 18))
                    )
                )
                
                processed_txs.append(processed_tx)
                
            except Exception as e:
                logger.error(f"Error procesando transacción {tx.get('hash')}: {str(e)}")
                continue
                
        return processed_txs

    async def _get_historical_token_price(
        self,
        token_address: Optional[str],
        blockchain: str,
        timestamp: str
    ) -> float:
        """Obtiene el precio histórico de un token"""
        try:
            if not token_address:
                # Para transacciones de moneda nativa (ETH, BNB, etc.)
                params = {
                    "chain": blockchain,
                    "timestamp": timestamp
                }
                result = await evm_api.token.get_native_price(
                    api_key=self.moralis_api_key,
                    params=params
                )
                return float(result.get("usdPrice", 0))
            else:
                # Para tokens ERC20
                params = {
                    "chain": blockchain,
                    "address": token_address,
                    "timestamp": timestamp
                }
                result = await evm_api.token.get_token_price(
                    api_key=self.moralis_api_key,
                    params=params
                )
                return float(result.get("usdPrice", 0))
                
        except Exception as e:
            logger.error(f"Error obteniendo precio histórico: {str(e)}")
            return 0

    def _calculate_usd_value(
        self,
        amount: float,
        price: float,
        decimals: int
    ) -> float:
        """Calcula el valor en USD de una cantidad de tokens"""
        try:
            return (amount / (10 ** decimals)) * price
        except Exception as e:
            logger.error(f"Error calculando valor USD: {str(e)}")
            return 0

    async def get_token_info(
        self,
        token_address: str,
        blockchain: str
    ) -> Optional[TokenInfo]:
        """Obtiene información detallada de un token"""
        try:
            params = {
                "chain": blockchain,
                "address": token_address
            }
            
            result = await evm_api.token.get_token_metadata(
                api_key=self.moralis_api_key,
                params=params
            )
            
            if result:
                return TokenInfo(
                    address=token_address,
                    symbol=result['symbol'],
                    name=result['name'],
                    decimals=int(result['decimals']),
                    total_value_usd=0,  # Se actualiza después
                    transaction_count=0  # Se actualiza después
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo info del token: {str(e)}")
            return None

    async def analyze_wallet_interactions(
        self,
        address: str,
        blockchain: str,
        days: int = 30
    ) -> Dict:
        """
        Analiza las interacciones de una wallet para detectar patrones.
        
        Args:
            address: Dirección de la wallet
            blockchain: Nombre de la blockchain
            days: Número de días hacia atrás para analizar
            
        Returns:
            Dict con estadísticas y patrones de interacción
        """
        try:
            # Obtener transacciones
            transactions = await self.get_wallet_transactions(address, blockchain, days)
            
            # Inicializar estadísticas
            stats = {
                "total_sent_usd": 0,
                "total_received_usd": 0,
                "transaction_count": len(transactions),
                "unique_tokens": set(),
                "contract_interactions": {},
                "hourly_activity": {i: 0 for i in range(24)},
                "first_tx_date": None,
                "last_tx_date": None
            }
            
            # Analizar transacciones
            for tx in transactions:
                # Actualizar montos
                if tx.from_address.lower() == address.lower():
                    stats["total_sent_usd"] += tx.usd_value
                else:
                    stats["total_received_usd"] += tx.usd_value
                
                # Registrar tokens únicos
                if tx.token_address:
                    stats["unique_tokens"].add(tx.token_address)
                
                # Registrar interacciones con contratos
                if tx.to_address:
                    stats["contract_interactions"][tx.to_address] = \
                        stats["contract_interactions"].get(tx.to_address, 0) + 1
                
                # Actualizar actividad por hora
                hour = tx.timestamp.hour
                stats["hourly_activity"][hour] += 1
                
                # Actualizar fechas
                if not stats["first_tx_date"] or tx.timestamp < stats["first_tx_date"]:
                    stats["first_tx_date"] = tx.timestamp
                if not stats["last_tx_date"] or tx.timestamp > stats["last_tx_date"]:
                    stats["last_tx_date"] = tx.timestamp
            
            # Procesar tokens únicos
            unique_tokens_info = []
            for token_addr in stats["unique_tokens"]:
                token_info = await self.get_token_info(token_addr, blockchain)
                if token_info:
                    unique_tokens_info.append(token_info)
            
            # Preparar resultado final
            return {
                "address": address,
                "blockchain": blockchain,
                "total_sent_usd": stats["total_sent_usd"],
                "total_received_usd": stats["total_received_usd"],
                "transaction_count": stats["transaction_count"],
                "unique_tokens": unique_tokens_info,
                "most_frequent_contracts": sorted(
                    stats["contract_interactions"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "hourly_activity": stats["hourly_activity"],
                "first_transaction_date": stats["first_tx_date"],
                "last_transaction_date": stats["last_tx_date"]
            }
            
        except Exception as e:
            logger.error(f"Error analizando interacciones: {str(e)}")
            return {}