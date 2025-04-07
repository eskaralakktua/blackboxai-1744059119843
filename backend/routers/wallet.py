from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict
import logging
from ..services.csv_service import CSVService
from ..services.blockchain_service import BlockchainService
from ..services.openai_service import OpenAIService
from ..services.graph_service import GraphService
from ..models import AnalysisReport, WalletStats, AIAnalysis
import tempfile
import os
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Instanciar servicios
csv_service = CSVService()
blockchain_service = BlockchainService()
openai_service = OpenAIService()
graph_service = GraphService()

# Variable global para almacenar resultados de análisis en memoria
analysis_results = {}

@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Endpoint para subir archivo CSV con direcciones de wallet.
    Inicia el análisis en segundo plano.
    """
    try:
        # Validar que sea un archivo CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser un CSV"
            )
        
        # Procesar el CSV
        grouped_addresses = await csv_service.process_csv(file)
        
        # Generar ID único para este análisis
        analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Iniciar análisis en segundo plano
        background_tasks.add_task(
            analyze_wallets,
            grouped_addresses,
            analysis_id
        )
        
        return {
            "message": "Archivo CSV procesado correctamente",
            "analysis_id": analysis_id,
            "wallets_count": sum(len(addrs) for addrs in grouped_addresses.values())
        }
        
    except Exception as e:
        logger.error(f"Error en upload_csv: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el archivo: {str(e)}"
        )

@router.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """
    Obtiene el estado actual del análisis.
    """
    try:
        if analysis_id not in analysis_results:
            return {"status": "not_found"}
            
        result = analysis_results[analysis_id]
        return {
            "status": result.get("status", "processing"),
            "progress": result.get("progress", 0),
            "message": result.get("message", ""),
            "error": result.get("error", None)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo estado del análisis"
        )

@router.get("/analysis/{analysis_id}/report")
async def get_analysis_report(analysis_id: str):
    """
    Obtiene el reporte completo del análisis.
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(
                status_code=404,
                detail="Análisis no encontrado"
            )
            
        result = analysis_results[analysis_id]
        
        if result.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="El análisis aún no ha terminado"
            )
            
        return result.get("report", {})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo reporte: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo reporte del análisis"
        )

@router.get("/analysis/{analysis_id}/graph")
async def get_analysis_graph(analysis_id: str):
    """
    Obtiene el grafo de transacciones del análisis.
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(
                status_code=404,
                detail="Análisis no encontrado"
            )
            
        result = analysis_results[analysis_id]
        
        if result.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="El análisis aún no ha terminado"
            )
            
        return result.get("graph_data", {"nodes": [], "edges": []})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo grafo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo grafo del análisis"
        )

@router.get("/analysis/{analysis_id}/download/{format}")
async def download_report(analysis_id: str, format: str):
    """
    Descarga el reporte en formato PDF o CSV.
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(
                status_code=404,
                detail="Análisis no encontrado"
            )
            
        result = analysis_results[analysis_id]
        
        if result.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="El análisis aún no ha terminado"
            )
            
        if format.lower() not in ["pdf", "csv"]:
            raise HTTPException(
                status_code=400,
                detail="Formato no soportado"
            )
            
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{format.lower()}"
        ) as tmp_file:
            if format.lower() == "csv":
                # Exportar a CSV
                csv_content = await csv_service.export_results_to_csv(result["report"])
                tmp_file.write(csv_content)
            else:
                # Generar PDF (implementar en una función separada)
                generate_pdf_report(result["report"], tmp_file.name)
            
            return FileResponse(
                tmp_file.name,
                filename=f"wallet_analysis_{analysis_id}.{format.lower()}",
                media_type=f"application/{format.lower()}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error descargando reporte: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error generando archivo de reporte"
        )

async def analyze_wallets(
    grouped_addresses: Dict[str, List[str]],
    analysis_id: str
):
    """
    Función de análisis en segundo plano.
    """
    try:
        # Inicializar resultado
        analysis_results[analysis_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Iniciando análisis"
        }
        
        # Analizar cada wallet
        all_wallet_stats = []
        total_wallets = sum(len(addrs) for addrs in grouped_addresses.values())
        wallets_processed = 0
        
        for blockchain, addresses in grouped_addresses.items():
            for address in addresses:
                try:
                    # Actualizar progreso
                    wallets_processed += 1
                    progress = int((wallets_processed / total_wallets) * 100)
                    analysis_results[analysis_id].update({
                        "progress": progress,
                        "message": f"Analizando wallet {address}"
                    })
                    
                    # Obtener datos de la blockchain
                    wallet_data = await blockchain_service.analyze_wallet_interactions(
                        address,
                        blockchain
                    )
                    
                    if wallet_data:
                        all_wallet_stats.append(WalletStats(**wallet_data))
                        
                except Exception as e:
                    logger.error(f"Error analizando wallet {address}: {str(e)}")
                    continue
        
        # Crear grafo de transacciones
        analysis_results[analysis_id].update({
            "message": "Generando grafo de transacciones"
        })
        
        graph_data = graph_service.create_transaction_graph(
            [tx for stats in all_wallet_stats for tx in stats.transactions],
            {stats.address: stats.dict() for stats in all_wallet_stats}
        )
        
        # Analizar con GPT
        analysis_results[analysis_id].update({
            "message": "Realizando análisis con IA"
        })
        
        ai_insights = []
        for stats in all_wallet_stats:
            analysis = await openai_service.analyze_wallet_patterns(stats)
            ai_insights.append(analysis)
        
        # Analizar relaciones
        relationships = await openai_service.analyze_wallet_relationships(
            all_wallet_stats,
            graph_data.dict()
        )
        
        # Crear reporte final
        report = AnalysisReport(
            timestamp=datetime.now(),
            wallets_analyzed=all_wallet_stats,
            relationships=relationships,
            graph_data=graph_data,
            ai_insights=ai_insights,
            summary=generate_summary(all_wallet_stats, relationships, ai_insights)
        )
        
        # Guardar resultados
        analysis_results[analysis_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Análisis completado",
            "report": report.dict(),
            "graph_data": graph_data.dict()
        })
        
    except Exception as e:
        logger.error(f"Error en análisis: {str(e)}")
        analysis_results[analysis_id].update({
            "status": "error",
            "error": str(e)
        })

def generate_summary(
    wallet_stats: List[WalletStats],
    relationships: List[Dict],
    ai_insights: List[AIAnalysis]
) -> str:
    """
    Genera un resumen del análisis.
    """
    total_volume = sum(
        stats.total_sent_usd + stats.total_received_usd
        for stats in wallet_stats
    )
    
    high_risk_wallets = [
        insight.wallet_address
        for insight in ai_insights
        if insight.risk_score > 0.7
    ]
    
    strong_relationships = [
        rel for rel in relationships
        if rel["confidence_score"] > 0.8
    ]
    
    summary = f"""
    Análisis completado para {len(wallet_stats)} wallets.
    Volumen total analizado: ${total_volume:,.2f} USD
    Wallets de alto riesgo identificadas: {len(high_risk_wallets)}
    Relaciones fuertes detectadas: {len(strong_relationships)}
    """
    
    return summary

def generate_pdf_report(report_data: Dict, output_path: str):
    """
    Genera un reporte PDF.
    Esta función debe ser implementada según los requisitos específicos.
    """
    # TODO: Implementar generación de PDF
    pass