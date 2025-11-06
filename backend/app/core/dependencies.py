from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..core.security import decode_access_token, hash_password
from ..models.user import User

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """获取当前登录用户。"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id: Optional[int] = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )

    # 注意：当传入的 sub 不是整数（例如管理员 UUID）时，将抛出 ValueError
    try:
        user_lookup_id = int(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )

    user = db.query(User).filter(User.id == user_lookup_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return user


async def get_current_user_or_demo(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db),
) -> User:
    """返回当前登录用户；若在开发环境下无凭证，则回退到 DEMO 用户。

    - 生产/非 DEBUG 模式：行为与 get_current_user 等价（无凭证即 401）。
    - 开发/DEBUG 模式：若无凭证，则确保存在一个 demo 用户并返回之。
    """
    # 1) 有凭证则按严格校验执行
    if credentials is not None:
        return await get_current_user(credentials, db)  # type: ignore[arg-type]

    # 2) 无凭证：仅在 DEBUG 下允许回退到 demo 用户
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证的请求",
        )

    # 确保存在 demo 用户（仅用于开发环境的无登录使用场景）
    demo_username = "demo"
    demo = db.query(User).filter(User.username == demo_username).first()
    if demo is None:
        demo = User(
            username=demo_username,
            email=None,
            hashed_password=hash_password("demo"),
            is_admin=False,
            is_active=True,
        )
        db.add(demo)
        db.commit()
        db.refresh(demo)

    return demo


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前管理员用户。"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
