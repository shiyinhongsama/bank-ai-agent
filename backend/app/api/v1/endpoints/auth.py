"""
认证API端点
"""

import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# 临时存储用户（在实际项目中应使用数据库）
fake_users_db = {}

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

class UserRegister(BaseModel):
    """用户注册模型"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    id_number: Optional[str] = None

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    is_verified: bool
    created_at: datetime

class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    # 这里应该是JWT令牌生成逻辑
    # 简化实现
    import base64
    import json
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 将过期时间序列化为ISO字符串，避免json.dumps报错
    to_encode.update({"exp": expire.isoformat()})
    encoded_jwt = base64.b64encode(json.dumps(to_encode).encode()).decode()
    return encoded_jwt

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        if user_data.username in fake_users_db:
            raise HTTPException(
                status_code=400,
                detail="用户名已存在"
            )
        
        # 创建用户
        user_id = len(fake_users_db) + 1
        user = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "id_number": user_data.id_number,
            "hashed_password": user_data.password,  # 实际项目中应该加密
            "is_verified": False,
            "created_at": datetime.now()
        }
        
        fake_users_db[user_data.username] = user
        
        logger.info(f"✅ 用户注册成功: {user_data.username}")
        
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            phone=user["phone"],
            is_verified=user["is_verified"],
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 用户注册失败: {e}")
        raise HTTPException(status_code=500, detail="注册失败")

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    try:
        # 优先检查内存用户
        user = fake_users_db.get(user_data.username)

        # 若内存中不存在，则查询数据库中的演示用户
        if not user:
            db_user = db.query(User).filter(User.username == user_data.username).first()
            if not db_user or db_user.hashed_password != user_data.password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            # 统一返回结构
            user = {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "full_name": db_user.full_name,
                "phone": db_user.phone,
                "hashed_password": db_user.hashed_password,
                "is_verified": db_user.is_verified,
                "created_at": db_user.created_at,
            }
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]},
            expires_delta=access_token_expires
        )
        
        logger.info(f"✅ 用户登录成功: {user_data.username}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user["full_name"],
                phone=user["phone"],
                is_verified=user["is_verified"],
                created_at=user["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 用户登录失败: {e}")
        raise HTTPException(status_code=500, detail="登录失败")

@router.post("/logout")
async def logout():
    """用户登出"""
    # 在实际项目中应该将令牌加入黑名单
    return {"message": "登出成功"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    try:
        # 验证令牌（在实际项目中应该验证JWT）
        # 简化实现
        import base64
        import json
        
        try:
            payload = base64.b64decode(credentials.credentials).decode()
            token_data = json.loads(payload)
            username = token_data.get("sub")
        except:
            raise HTTPException(status_code=401, detail="无效的令牌")
        
        # 获取用户信息（先查内存，再查数据库）
        user = fake_users_db.get(username)
        if not user:
            db_user = db.query(User).filter(User.username == username).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="用户不存在")
            user = {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "full_name": db_user.full_name,
                "phone": db_user.phone,
                "is_verified": db_user.is_verified,
                "created_at": db_user.created_at,
            }
        
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            phone=user["phone"],
            is_verified=user["is_verified"],
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")