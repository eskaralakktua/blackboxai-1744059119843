# Wallet Analysis Backend

Backend para el análisis de wallets en diferentes blockchains. Esta aplicación procesa archivos CSV con direcciones de wallet, analiza sus transacciones y relaciones, y genera reportes detallados utilizando IA.

## Características

- 📥 Procesamiento de archivos CSV con direcciones de wallet
- 🔍 Análisis de transacciones usando Moralis/Web3
- 🧠 Análisis de patrones y relaciones con GPT-4
- 📊 Generación de grafos de transacciones
- 📄 Reportes en PDF y CSV
- 🔗 API RESTful con FastAPI

## Requisitos

- Python 3.8+
- FastAPI
- Moralis SDK
- OpenAI API
- Web3.py
- NetworkX
- Pandas
- ReportLab (para PDFs)

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd wallet-analysis-backend
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus claves de API y configuración
```

## Uso

1. Iniciar el servidor:
```bash
uvicorn main:app --reload --port 8000
```

2. La API estará disponible en `http://localhost:8000`

3. Documentación de la API disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### POST /api/v1/upload-csv
Sube un archivo CSV con direcciones de wallet para análisis.

### GET /api/v1/analysis/{analysis_id}/status
Obtiene el estado actual del análisis.

### GET /api/v1/analysis/{analysis_id}/report
Obtiene el reporte completo del análisis.

### GET /api/v1/analysis/{analysis_id}/graph
Obtiene el grafo de transacciones.

### GET /api/v1/analysis/{analysis_id}/download/{format}
Descarga el reporte en formato PDF o CSV.

## Estructura del Proyecto

```
backend/
├── main.py           # Punto de entrada de la aplicación
├── config.py         # Configuración global
├── models.py         # Modelos Pydantic
├── utils.py          # Utilidades generales
├── requirements.txt  # Dependencias
├── services/         # Servicios de la aplicación
│   ├── csv_service.py
│   ├── blockchain_service.py
│   ├── openai_service.py
│   └── graph_service.py
└── routers/          # Rutas de la API
    └── wallet.py
```

## Formato del CSV

El archivo CSV debe contener las siguientes columnas:
- `wallet_address` (requerido): Dirección de la wallet
- `blockchain` (opcional): Nombre de la blockchain (ethereum, bsc, polygon)

Ejemplo:
```csv
wallet_address,blockchain
0x742d35Cc6634C0532925a3b844Bc454e4438f44e,ethereum
0x123...abc,bsc
```

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.