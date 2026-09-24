import uuid
from dataclasses import dataclass
from typing import Optional
from fastapi import Header, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

OVERALL_ACCESS_ROLES = frozenset({
    "NPVCC_OFFICER",
    "DSMB_ADMIN",
    "REGULATORY_AUDITOR",
    "SUPER_ADMIN",
})


@dataclass
class TenantContext:
    site_id: Optional[uuid.UUID]
    role: str
    user_id: str

    @property
    def has_global_access(self) -> bool:
        return self.role in OVERALL_ACCESS_ROLES


async def set_tenant_context(
    site_id: Optional[uuid.UUID],
    role: str,
    db: AsyncSession,
) -> None:
    sid = str(site_id) if site_id else ""
    await db.execute(
        text("SELECT set_config('app.current_user_site_id', :sid, true)"),
        {"sid": sid},
    )
    await db.execute(
        text("SELECT set_config('app.current_user_role', :role, true)"),
        {"role": role},
    )


async def get_tenant_context(
    x_site_id: Optional[str] = Header(None, alias="X-Site-Id"),
    x_user_role: str = Header("CLINICIAN", alias="X-User-Role"),
    x_user_id: str = Header("investigator", alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    parsed_site_id: Optional[uuid.UUID] = None
    if x_site_id and x_site_id.strip():
        try:
            parsed_site_id = uuid.UUID(x_site_id.strip())
        except ValueError:
            parsed_site_id = None

    await set_tenant_context(parsed_site_id, x_user_role, db)
    return TenantContext(
        site_id=parsed_site_id,
        role=x_user_role,
        user_id=x_user_id,
    )


def check_site_access(tenant: TenantContext, resource_site_id: Optional[uuid.UUID]) -> bool:
    if tenant.has_global_access:
        return True
    if resource_site_id is None:
        return True
    return tenant.site_id == resource_site_id


def apply_tenant_filter(query, tenant: TenantContext, site_column):
    if tenant.has_global_access:
        return query
    if tenant.site_id is not None:
        return query.where(site_column == tenant.site_id)
    return query

