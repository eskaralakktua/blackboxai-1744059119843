import pandas as pd
from typing import Dict, List, Tuple
import logging
from ..utils import validate_csv_file, group_wallets_by_blockchain
from ..models import WalletAddress
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class CSVService:
    def __init__(self):
        self.supported_chains = ["ethereum", "bsc", "polygon"]

    async def process_csv(self, file: UploadFile) -> Dict[str, List[str]]:
        """
        Procesa el archivo CSV subido y retorna las direcciones agrupadas por blockchain.
        
        Args:
            file: Archivo CSV subido
            
        Returns:
            Dict con blockchain como clave y lista de direcciones como valor
            
        Raises:
            HTTPException: Si hay errores en el formato o contenido del CSV
        """
        try:
            # Leer el contenido del archivo
            contents = await file.read()
            
            # Validar el CSV y obtener DataFrame
            is_valid, message, df = validate_csv_file(contents)
            
            if not is_valid:
                logger.error(f"Error en validación de CSV: {message}")
                raise HTTPException(status_code=400, detail=message)
            
            # Verificar límite de direcciones
            if len(df) > 100:  # Límite arbitrario, ajustar según necesidades
                raise HTTPException(
                    status_code=400,
                    detail="El archivo excede el límite máximo de 100 direcciones"
                )
            
            # Agrupar direcciones por blockchain
            grouped_addresses = group_wallets_by_blockchain(df)
            
            # Validar que haya al menos una dirección
            total_addresses = sum(len(addresses) for addresses in grouped_addresses.values())
            if total_addresses == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No se encontraron direcciones válidas en el archivo"
                )
            
            return grouped_addresses
            
        except pd.errors.EmptyDataError:
            raise HTTPException(status_code=400, detail="El archivo CSV está vacío")
            
        except pd.errors.ParserError:
            raise HTTPException(
                status_code=400,
                detail="Error al parsear el archivo CSV. Verifique el formato"
            )
            
        except Exception as e:
            logger.error(f"Error procesando CSV: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando el archivo: {str(e)}"
            )

    def validate_and_clean_address(self, address: str) -> str:
        """
        Valida y limpia una dirección de wallet.
        
        Args:
            address: Dirección de wallet a validar
            
        Returns:
            Dirección limpia y en minúsculas
            
        Raises:
            ValueError: Si la dirección no es válida
        """
        try:
            # Usar el modelo Pydantic para validar
            wallet = WalletAddress(address=address)
            return wallet.address
        except ValueError as e:
            raise ValueError(f"Dirección inválida ({address}): {str(e)}")

    def get_csv_summary(self, grouped_addresses: Dict[str, List[str]]) -> Dict:
        """
        Genera un resumen del contenido del CSV procesado.
        
        Args:
            grouped_addresses: Direcciones agrupadas por blockchain
            
        Returns:
            Dict con estadísticas del CSV
        """
        summary = {
            "total_addresses": 0,
            "addresses_by_chain": {},
            "validation_status": "success"
        }
        
        for chain, addresses in grouped_addresses.items():
            summary["addresses_by_chain"][chain] = len(addresses)
            summary["total_addresses"] += len(addresses)
            
        return summary

    async def export_results_to_csv(self, analysis_results: Dict) -> bytes:
        """
        Exporta los resultados del análisis a un archivo CSV.
        
        Args:
            analysis_results: Resultados del análisis de wallets
            
        Returns:
            Contenido del CSV en bytes
        """
        try:
            # Crear DataFrame con los resultados
            results_data = []
            for wallet_data in analysis_results.get("wallets_analyzed", []):
                row = {
                    "wallet_address": wallet_data["address"],
                    "blockchain": wallet_data["blockchain"],
                    "total_sent_usd": wallet_data["total_sent_usd"],
                    "total_received_usd": wallet_data["total_received_usd"],
                    "transaction_count": wallet_data["transaction_count"],
                    "first_transaction": wallet_data["first_transaction_date"],
                    "last_transaction": wallet_data["last_transaction_date"],
                    "unique_tokens_count": len(wallet_data["unique_tokens"]),
                    "most_frequent_contracts": ",".join(wallet_data["most_frequent_contracts"][:5])
                }
                results_data.append(row)
            
            df = pd.DataFrame(results_data)
            
            # Convertir DataFrame a CSV
            csv_content = df.to_csv(index=False)
            return csv_content.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error exportando resultados a CSV: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error generando el archivo CSV de resultados"
            )