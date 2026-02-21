"""
Tenant-scoped query service
SECURITY: Enforce tenant isolation at query level
"""
from typing import TypeVar, Type
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query
from fastapi import HTTPException, status
import uuid

from app.core.database import Base

T = TypeVar('T', bound=Base)


class TenantService:
    """
    Service to enforce tenant-scoped queries
    Prevents cross-tenant data leakage
    """
    
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
    
    def get_query(self, model: Type[T]) -> Query:
        """
        Get base query with tenant filter
        SECURITY: All queries automatically filtered by tenant_id
        """
        if not hasattr(model, 'tenant_id'):
            raise ValueError(f"Model {model.__name__} does not have tenant_id column")
        
        return select(model).filter(model.tenant_id == self.tenant_id)
    
    async def get_by_id(self, model: Type[T], id: uuid.UUID) -> T:
        """Get single record by ID within tenant"""
        result = await self.db.execute(
            select(model).filter(
                and_(
                    model.id == id,
                    model.tenant_id == self.tenant_id,
                )
            )
        )
        
        obj = result.scalar_one_or_none()
        
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.__name__} not found",
            )
        
        return obj
    
    async def verify_access(self, obj: Base) -> None:
        """
        Verify that object belongs to current tenant
        Raises 403 if cross-tenant access attempted
        """
        if not hasattr(obj, 'tenant_id'):
            return  # Object not tenant-scoped
        
        if obj.tenant_id != self.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Resource belongs to different tenant",
            )
