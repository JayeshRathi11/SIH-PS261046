import uuid
from typing import Any, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.idempotency import check_idempotency, store_idempotency_record
from app.models.clinical import AdverseEvent, TrialPatient
from app.schemas.clinical import AdverseEventCreate, AdverseEventOut
from app.services.ct16_generator import generate_form_ct16_pdf
from app.services.safety import create_adverse_event
from app.services.semantic_search import find_similar_safety_cases

router = APIRouter(prefix="/api/v1/safety", tags=["Safety & Pharmacovigilance"])


@router.post(
    "/adverse-event",
    response_model=AdverseEventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log an adverse event (SAE auto-trigger enabled)",
)
@router.post(
    "/adverse-events",
    response_model=AdverseEventOut,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def log_adverse_event(
    payload: AdverseEventCreate,
    idempotency_key: Optional[str] = Depends(check_idempotency),
    db: AsyncSession = Depends(get_db),
) -> AdverseEventOut:
    try:
        ae = await create_adverse_event(
            db,
            patient_id=payload.patient_id,
            severity=payload.severity,
            clinical_notes=payload.clinical_notes,
            ayurvedic_intervention=payload.ayurvedic_intervention,
            concomitant_drugs=payload.concomitant_drugs,
            reported_by=payload.reported_by,
        )
        out = AdverseEventOut.model_validate(ae)
        if idempotency_key:
            store_idempotency_record(idempotency_key, out.model_dump())
        return out
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log adverse event: {exc}",
        ) from exc


@router.get(
    "/cases/similar",
    summary="Semantic case-similarity search over prior adverse events and safety signals",
)
async def search_similar_cases(
    query: str = Query(..., min_length=2, description="Clinical presentation or symptom query"),
    trial_id: Optional[uuid.UUID] = Query(None, description="Optional study protocol filter"),
    top_k: int = Query(5, ge=1, le=50, description="Max cases to return"),
    threshold: float = Query(0.25, ge=0.0, le=1.0, description="Minimum cosine similarity cutoff"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    return await find_similar_safety_cases(
        query_text=query,
        trial_id=trial_id,
        db=db,
        top_k=top_k,
        threshold=threshold,
    )


@router.get(
    "/reports/ct16/{ae_id}",
    summary="Download CDSCO Form CT-16 Report (PDF)",
)
async def get_form_ct16_report(
    ae_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(AdverseEvent)
        .options(joinedload(AdverseEvent.patient).joinedload(TrialPatient.trial))
        .where(AdverseEvent.id == ae_id)
    )
    result = await db.execute(stmt)
    ae = result.unique().scalar_one_or_none()
    if ae is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adverse event not found",
        )
    if not ae.is_serious:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form CT-16 is only generated for Serious Adverse Events (SAE)",
        )

    patient = ae.patient
    trial = patient.trial if patient else None
    pdf_bytes = generate_form_ct16_pdf(
        ae_record=ae,
        patient_record=patient,
        trial_record=trial,
        interactions=ae.herb_drug_conflicts,
        meddra_terms=ae.coded_meddra_terms,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Form_CT16_{ae_id}.pdf"},
    )


@router.post(
    "/transcribe-audio",
    summary="Multilingual Voice-to-Text Clinical Audio Transcription & MedDRA Coding",
)
async def transcribe_audio_endpoint(
    audio_file: UploadFile = File(..., description="Raw consultation audio (.wav, .mp3, .m4a, .ogg)"),
):
    audio_bytes = await audio_file.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty.",
        )
    filename = audio_file.filename or "consultation.wav"
    mime_type = audio_file.content_type or "audio/wav"

    from app.services.voice_transcriber import transcribe_clinical_audio
    return transcribe_clinical_audio(audio_bytes=audio_bytes, filename=filename, mime_type=mime_type)

