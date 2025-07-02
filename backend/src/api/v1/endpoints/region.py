from fastapi import APIRouter, Depends, HTTPException, status

from domain.entities.region import Region
from domain.exceptions import (
    CountryDoesNotExistsError,
    RegionConflictError,
    RegionDatabaseError,
    RegionDoesNotExistsError,
)
from schemas.region_schema import RegionCreate, RegionUpdate
from services.region_service import (
    RegionService,
    region_service_dependency,
)

router = APIRouter(prefix="/region", tags=["region"])
