from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import apuracao_reference, companies, correction, efd_files, fiscal_periods, pdf_apuracao, pr_adjustment, validation

app = FastAPI(
    title="FiscalCheck EFD ICMS/IPI",
    description="API para conferência e ajuste assistido da EFD ICMS/IPI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router)
app.include_router(fiscal_periods.router)
app.include_router(efd_files.router)
app.include_router(pdf_apuracao.router)
app.include_router(apuracao_reference.router)
app.include_router(validation.router)
app.include_router(correction.router)
app.include_router(pr_adjustment.router)


@app.get("/health")
def health():
    return {"status": "ok"}
