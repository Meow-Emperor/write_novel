from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.dependencies import get_current_admin, get_current_user
from ..models.prompt import Prompt
from ..models.user import User
from ..schemas.prompt import PromptCreate, PromptResponse, PromptUpdate

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/", response_model=List[PromptResponse])
def list_prompts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取提示词列表。"""
    prompts = db.query(Prompt).offset(skip).limit(limit).all()
    return prompts


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取指定提示词。"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提示词不存在",
        )
    return prompt


@router.get("/name/{name}", response_model=PromptResponse)
def get_prompt_by_name(
    name: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """根据名称获取提示词。"""
    prompt = db.query(Prompt).filter(Prompt.name == name).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提示词不存在",
        )
    return prompt


@router.post("/", response_model=PromptResponse)
def create_prompt(
    prompt_data: PromptCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """创建提示词（管理员）。"""
    existing = db.query(Prompt).filter(Prompt.name == prompt_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="提示词名称已存在",
        )

    new_prompt = Prompt(**prompt_data.model_dump())
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)

    return new_prompt


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """更新提示词（管理员）。"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提示词不存在",
        )

    update_data = prompt_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prompt, key, value)

    db.commit()
    db.refresh(prompt)

    return prompt


@router.delete("/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """删除提示词（管理员）。"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提示词不存在",
        )

    db.delete(prompt)
    db.commit()

    return {"message": "提示词已删除"}
