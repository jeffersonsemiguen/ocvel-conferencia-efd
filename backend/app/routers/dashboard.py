from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.company import Company
from app.models.efd_file import EfdFile
from app.models.fiscal_period import FiscalPeriod
from app.models.validation import ValidationRun

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    companies = (
        db.query(Company)
        .filter(Company.is_active == True)
        .order_by(Company.name)
        .all()
    )

    company_data = []
    total_critical = 0
    total_alert = 0
    total_periods = 0

    for company in companies:
        periods = (
            db.query(FiscalPeriod)
            .filter(FiscalPeriod.company_id == company.id)
            .order_by(FiscalPeriod.year.desc(), FiscalPeriod.month.desc())
            .all()
        )

        period_data = []
        for period in periods:
            efd_file = (
                db.query(EfdFile)
                .filter(EfdFile.fiscal_period_id == period.id)
                .order_by(EfdFile.created_at.desc())
                .first()
            )

            latest_run = None
            if efd_file:
                latest_run = (
                    db.query(ValidationRun)
                    .filter(ValidationRun.fiscal_period_id == period.id)
                    .order_by(ValidationRun.started_at.desc())
                    .first()
                )

            run_summary = None
            if latest_run and latest_run.status == "completed":
                run_summary = {
                    "id": str(latest_run.id),
                    "total_findings": latest_run.total_findings,
                    "critical_count": latest_run.critical_count,
                    "alert_count": latest_run.alert_count,
                    "monetary_count": latest_run.monetary_count,
                    "observation_count": latest_run.observation_count,
                    "started_at": latest_run.started_at.isoformat() if latest_run.started_at else None,
                }
                total_critical += latest_run.critical_count
                total_alert += latest_run.alert_count

            period_data.append({
                "id": str(period.id),
                "year": period.year,
                "month": period.month,
                "status": period.status,
                "has_efd": efd_file is not None,
                "efd_parse_status": efd_file.parse_status if efd_file else None,
                "latest_run": run_summary,
            })

        total_periods += len(periods)
        company_data.append({
            "id": str(company.id),
            "name": company.name,
            "trade_name": company.trade_name,
            "cnpj": company.cnpj,
            "state": company.state,
            "periods": period_data,
            "period_count": len(periods),
            "critical_count": sum(
                (p["latest_run"]["critical_count"] if p["latest_run"] else 0)
                for p in period_data
            ),
            "alert_count": sum(
                (p["latest_run"]["alert_count"] if p["latest_run"] else 0)
                for p in period_data
            ),
        })

    return {
        "summary": {
            "total_companies": len(companies),
            "total_periods": total_periods,
            "total_critical": total_critical,
            "total_alert": total_alert,
        },
        "companies": company_data,
    }
