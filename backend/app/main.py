from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import (
    apuracao_reference, auth, cfop_cst, companies, correction, dashboard,
    efd_files, fiscal_matrix, fiscal_periods, nfe, pdf_apuracao, pr_adjustment, validation,
    period_analytics, relatorio, validation_config,
)
from app import models  # Import all models so they're registered with Base

app = FastAPI(
    title="FiscalCheck EFD ICMS/IPI",
    description="API para conferência e ajuste assistido da EFD ICMS/IPI",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Autenticação (rotas públicas: /auth/login, /auth/seed-admin)
app.include_router(auth.router)

# Rotas protegidas por JWT
app.include_router(companies.router)
app.include_router(fiscal_periods.router)
app.include_router(efd_files.router)
app.include_router(pdf_apuracao.router)
app.include_router(apuracao_reference.router)
app.include_router(validation.router)
app.include_router(correction.router)
app.include_router(pr_adjustment.router)
app.include_router(cfop_cst.router)
app.include_router(fiscal_matrix.router)
app.include_router(dashboard.router)
app.include_router(period_analytics.router)
app.include_router(nfe.router)
app.include_router(relatorio.router)
app.include_router(validation_config.router)


@app.get("/health")
def health():
    return {"status": "ok"}
