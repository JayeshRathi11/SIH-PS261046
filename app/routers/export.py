import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.cdisc_exporter import generate_cdisc_sdtm_package
from app.services.fhir_exporter import generate_patient_fhir_bundle

router = APIRouter(prefix="/api/v1/export", tags=["Global Interoperability Exporters"])


@router.get(
    "/cdisc-sdtm/{trial_id}",
    summary="Export CDISC SDTM Study Package (ZIP)",
)
async def export_cdisc_sdtm(
    trial_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    zip_bytes = await generate_cdisc_sdtm_package(trial_id, db)
    if zip_bytes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical trial not found or contains no patient data.",
        )
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="CDISC_SDTM_{trial_id}.zip"'},
    )


@router.get(
    "/fhir-bundle/{patient_id}",
    summary="Export ABDM-Compliant HL7 FHIR R4 Patient Bundle (JSON)",
)
async def export_fhir_bundle(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    bundle = await generate_patient_fhir_bundle(patient_id, db)
    if bundle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )
    return bundle


@router.get(
    "/dead-letter/{trial_id}",
    summary="List quarantined dead-letter export records for a trial",
)
async def list_dead_letter_records(
    trial_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    from app.services.export_queue import get_quarantined_records_for_trial
    records = await get_quarantined_records_for_trial(trial_id, db)
    return [
        {
            "id": str(r.id),
            "export_type": r.export_type,
            "trial_id": str(r.trial_id),
            "record_identifier": r.record_identifier,
            "payload_snapshot": r.payload_snapshot,
            "error_trace": r.error_trace,
            "retry_count": r.retry_count,
            "status": r.status,
            "quarantined_at": r.quarantined_at.isoformat() if r.quarantined_at else None,
        }
        for r in records
    ]

