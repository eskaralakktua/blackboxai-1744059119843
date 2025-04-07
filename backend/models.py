from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
import re

class WalletAddress(BaseModel):
    address: str
    blockchain: Optional[str] = "ethereum"

    @validator('address')
    def validate_wallet_address(cls, v):
        # Validación básica de dirección Ethereum/BSC/Polygon (0x seguido de 40 caracteres hexadecimales)
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Dirección de wallet inválida')
        return v.lower()

    @validator('blockchain')
    def validate_blockchain(cls, v):
        valid_chains = ["ethereum", "bsc", "polygon"]
        if v.lower() not in valid_chains:
            raise ValueError(f'Blockchain no soportada. Debe ser una de: {", ".join(valid_chains)}')
        return v.lower()

class Transaction(BaseModel):
    hash: str
    from_address: str
    to_address: str
    value: float
    timestamp: datetime
    token_address: Optional[str]
    token_symbol: Optional[str]
    token_decimals: Optional[int]
    usd_value: Optional[float]

class TokenInfo(BaseModel):
    address: str
    symbol: str
    name: str
    decimals: int
    total_value_usd: float
    transaction_count: int

class WalletStats(BaseModel):
    address: str
    blockchain: str
    total_sent_usd: float
    total_received_usd: float
    transaction_count: int
    unique_tokens: List[TokenInfo]
    first_transaction_date: datetime
    last_transaction_date: datetime
    most_frequent_contracts: List[str]
    interaction_hours: Dict[int, int]  # Hora del día -> número de transacciones

class WalletRelation(BaseModel):
    wallet_a: str
    wallet_b: str
    transaction_count: int
    total_value_usd: float
    similarity_score: float
    relationship_type: str  # "frequent_transfer", "similar_pattern", "same_entity", etc.

class GraphNode(BaseModel):
    id: str  # wallet address
    label: str  # shortened address or ENS if available
    size: int  # based on transaction volume
    color: str  # based on blockchain or category
    properties: Dict  # additional node properties

class GraphEdge(BaseModel):
    source: str  # wallet address
    target: str  # wallet address
    weight: float  # based on transaction volume
    properties: Dict  # additional edge properties

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class AIAnalysis(BaseModel):
    wallet_address: str
    behavior_pattern: str
    entity_type: str  # "individual", "business", "exchange", "mixer", etc.
    risk_score: float
    observations: List[str]
    related_entities: List[str]

class AnalysisReport(BaseModel):
    timestamp: datetime
    wallets_analyzed: List[WalletStats]
    relationships: List[WalletRelation]
    graph_data: GraphData
    ai_insights: List[AIAnalysis]
    summary: str

class ErrorResponse(BaseModel):
    message: str
    detail: Optional[str] = None