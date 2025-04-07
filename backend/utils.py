import pandas as pd
from typing import List, Dict, Tuple
import csv
import io
from web3 import Web3
from datetime import datetime
import logging
from models import WalletAddress
from config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_csv_file(file_content: bytes) -> Tuple[bool, str, pd.DataFrame]:
    """
    Valida el contenido del archivo CSV y retorna un DataFrame si es válido.
    """
    try:
        # Leer el CSV en un DataFrame
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Verificar columnas requeridas
        if 'wallet_address' not in df.columns:
            return False, "El archivo CSV debe contener una columna 'wallet_address'", None
        
        # Si existe la columna blockchain, verificar valores válidos
        if 'blockchain' in df.columns:
            valid_chains = ["ethereum", "bsc", "polygon"]
            invalid_chains = df['blockchain'].dropna().unique().tolist()
            invalid_chains = [chain for chain in invalid_chains if chain.lower() not in valid_chains]
            
            if invalid_chains:
                return False, f"Blockchains no soportadas encontradas: {', '.join(invalid_chains)}", None
        else:
            # Si no existe la columna blockchain, añadirla con valor por defecto
            df['blockchain'] = 'ethereum'
        
        # Validar formato de direcciones
        w3 = Web3()
        invalid_addresses = []
        for addr in df['wallet_address']:
            if not w3.is_address(addr):
                invalid_addresses.append(addr)
        
        if invalid_addresses:
            return False, f"Direcciones inválidas encontradas: {', '.join(invalid_addresses[:5])}...", None
        
        # Limpiar y normalizar datos
        df['wallet_address'] = df['wallet_address'].str.lower()
        df['blockchain'] = df['blockchain'].str.lower()
        
        return True, "CSV válido", df
        
    except Exception as e:
        logger.error(f"Error validando CSV: {str(e)}")
        return False, f"Error procesando el archivo CSV: {str(e)}", None

def group_wallets_by_blockchain(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Agrupa las direcciones de wallet por blockchain.
    """
    grouped = {}
    for blockchain in df['blockchain'].unique():
        addresses = df[df['blockchain'] == blockchain]['wallet_address'].tolist()
        grouped[blockchain] = addresses
    return grouped

def format_wallet_address(address: str, max_length: int = 12) -> str:
    """
    Formatea una dirección de wallet para mostrar (trunca en el medio).
    """
    if len(address) <= max_length:
        return address
    return f"{address[:6]}...{address[-4:]}"

def calculate_usd_value(amount: float, token_price: float, decimals: int = 18) -> float:
    """
    Calcula el valor en USD de una cantidad de tokens.
    """
    try:
        return (amount / (10 ** decimals)) * token_price
    except Exception as e:
        logger.error(f"Error calculando valor USD: {str(e)}")
        return 0.0

def extract_common_patterns(transactions: List[Dict]) -> Dict:
    """
    Extrae patrones comunes de las transacciones.
    """
    patterns = {
        'common_hours': {},
        'frequent_contracts': {},
        'transaction_types': {},
    }
    
    for tx in transactions:
        # Analizar hora del día
        hour = datetime.fromtimestamp(tx['timestamp']).hour
        patterns['common_hours'][hour] = patterns['common_hours'].get(hour, 0) + 1
        
        # Analizar contratos frecuentes
        if tx.get('to_address'):
            patterns['frequent_contracts'][tx['to_address']] = \
                patterns['frequent_contracts'].get(tx['to_address'], 0) + 1
        
        # Analizar tipos de transacción
        tx_type = tx.get('type', 'transfer')
        patterns['transaction_types'][tx_type] = \
            patterns['transaction_types'].get(tx_type, 0) + 1
    
    return patterns

def calculate_similarity_score(wallet_a: Dict, wallet_b: Dict) -> float:
    """
    Calcula un score de similitud entre dos wallets basado en sus patrones.
    """
    score = 0.0
    weights = {
        'time_pattern': 0.3,
        'contract_overlap': 0.3,
        'value_pattern': 0.2,
        'token_overlap': 0.2
    }
    
    # Comparar patrones de tiempo
    time_similarity = compare_time_patterns(
        wallet_a.get('interaction_hours', {}),
        wallet_b.get('interaction_hours', {})
    )
    score += time_similarity * weights['time_pattern']
    
    # Comparar contratos comunes
    contract_similarity = compare_contract_overlap(
        wallet_a.get('most_frequent_contracts', []),
        wallet_b.get('most_frequent_contracts', [])
    )
    score += contract_similarity * weights['contract_overlap']
    
    # Comparar patrones de valor
    value_similarity = compare_value_patterns(
        wallet_a.get('total_sent_usd', 0),
        wallet_b.get('total_sent_usd', 0)
    )
    score += value_similarity * weights['value_pattern']
    
    # Comparar tokens comunes
    token_similarity = compare_token_overlap(
        wallet_a.get('unique_tokens', []),
        wallet_b.get('unique_tokens', [])
    )
    score += token_similarity * weights['token_overlap']
    
    return min(1.0, max(0.0, score))

def compare_time_patterns(hours_a: Dict[int, int], hours_b: Dict[int, int]) -> float:
    """
    Compara patrones de tiempo entre dos wallets.
    """
    if not hours_a or not hours_b:
        return 0.0
    
    total_hours = 24
    similarity = 0
    
    for hour in range(total_hours):
        count_a = hours_a.get(hour, 0)
        count_b = hours_b.get(hour, 0)
        
        if count_a > 0 and count_b > 0:
            # Calcular similitud relativa para esta hora
            ratio = min(count_a, count_b) / max(count_a, count_b)
            similarity += ratio
    
    return similarity / total_hours

def compare_contract_overlap(contracts_a: List[str], contracts_b: List[str]) -> float:
    """
    Compara el solapamiento de contratos entre dos wallets.
    """
    if not contracts_a or not contracts_b:
        return 0.0
    
    set_a = set(contracts_a)
    set_b = set(contracts_b)
    
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    
    return intersection / union if union > 0 else 0.0

def compare_value_patterns(value_a: float, value_b: float) -> float:
    """
    Compara patrones de valor entre dos wallets.
    """
    if value_a == 0 or value_b == 0:
        return 0.0
    
    ratio = min(value_a, value_b) / max(value_a, value_b)
    return ratio

def compare_token_overlap(tokens_a: List[Dict], tokens_b: List[Dict]) -> float:
    """
    Compara el solapamiento de tokens entre dos wallets.
    """
    if not tokens_a or not tokens_b:
        return 0.0
    
    tokens_set_a = {token['address'] for token in tokens_a}
    tokens_set_b = {token['address'] for token in tokens_b}
    
    intersection = len(tokens_set_a.intersection(tokens_set_b))
    union = len(tokens_set_a.union(tokens_set_b))
    
    return intersection / union if union > 0 else 0.0