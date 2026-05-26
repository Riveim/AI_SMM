from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Business, Product, PromptTemplate
from app.schemas import (
    BusinessCreate, BusinessUpdate, BusinessResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    PromptTemplateCreate, PromptTemplateResponse,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/business", tags=["business"])


# ─── Helpers ────────────────────────────────────────────────────────────────

async def get_business_or_404(business_id: int, user: User, db: AsyncSession) -> Business:
    result = await db.execute(
        select(Business).where(Business.id == business_id, Business.user_id == user.id)
    )
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Бизнес не найден")
    return b


# ─── Business ────────────────────────────────────────────────────────────────

@router.post("", response_model=BusinessResponse, status_code=201)
async def create_business(
    data: BusinessCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    b = Business(**data.model_dump(), user_id=user.id)
    db.add(b)
    await db.flush()
    await db.refresh(b)
    return b


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Business).where(Business.user_id == user.id))
    return result.scalars().all()


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_business_or_404(business_id, user, db)


@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: int,
    data: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    b = await get_business_or_404(business_id, user, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(b, field, value)
    await db.flush()
    await db.refresh(b)
    return b


@router.delete("/{business_id}", status_code=204)
async def delete_business(
    business_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    b = await get_business_or_404(business_id, user, db)
    await db.delete(b)


# ─── Products ────────────────────────────────────────────────────────────────

@router.post("/{business_id}/products", response_model=ProductResponse, status_code=201)
async def add_product(
    business_id: int,
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await get_business_or_404(business_id, user, db)
    p = Product(**data.model_dump(), business_id=business_id)
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@router.get("/{business_id}/products", response_model=list[ProductResponse])
async def list_products(
    business_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await get_business_or_404(business_id, user, db)
    result = await db.execute(select(Product).where(Product.business_id == business_id))
    return result.scalars().all()


@router.patch("/{business_id}/products/{product_id}", response_model=ProductResponse)
async def update_product(
    business_id: int,
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await get_business_or_404(business_id, user, db)
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.business_id == business_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Товар не найден")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    await db.flush()
    await db.refresh(p)
    return p


@router.delete("/{business_id}/products/{product_id}", status_code=204)
async def delete_product(
    business_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await get_business_or_404(business_id, user, db)
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.business_id == business_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Товар не найден")
    await db.delete(p)


# ─── Prompt Templates ────────────────────────────────────────────────────────

@router.post("/{business_id}/prompts", response_model=PromptTemplateResponse, status_code=201)
async def add_prompt(
    business_id: int,
    data: PromptTemplateCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await get_business_or_404(business_id, user, db)
    pt = PromptTemplate(**data.model_dump(), business_id=business_id)
    db.add(pt)
    await db.flush()
    await db.refresh(pt)
    return pt


@router.get("/{business_id}/prompts", response_model=list[PromptTemplateResponse])
async def list_prompts(
    business_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await get_business_or_404(business_id, user, db)
    result = await db.execute(
        select(PromptTemplate).where(
            PromptTemplate.business_id == business_id,
            PromptTemplate.is_active == True,
        )
    )
    return result.scalars().all()
