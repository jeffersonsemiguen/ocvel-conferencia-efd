import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.services.auth.auth_service import (
    create_access_token, hash_password, verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str
    role: str


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "analyst"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class ChangePasswordBody(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username, User.is_active == True).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(str(user.id), {"role": user.role, "name": user.name})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
def change_password(
    body: ChangePasswordBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(400, "Senha atual incorreta")
    current_user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"message": "Senha alterada com sucesso"}


# ── Admin: gerenciar usuários ─────────────────────────────────────────────────

@router.get("/users", response_model=list[UserResponse])
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.name).all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email já cadastrado")
    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == admin.id:
        raise HTTPException(400, "Não é possível desativar o próprio usuário")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    user.is_active = False
    db.commit()
    return {"message": "Usuário desativado"}


@router.post("/seed-admin", status_code=status.HTTP_201_CREATED)
def seed_admin(db: Session = Depends(get_db)):
    """Cria o primeiro usuário admin. Só funciona se não houver nenhum usuário no banco."""
    if db.query(User).count() > 0:
        raise HTTPException(400, "Já existem usuários cadastrados. Use /auth/users para criar novos.")
    admin = User(
        email="admin@fiscalcheck.local",
        name="Administrador",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {
        "message": "Admin criado. Altere a senha imediatamente.",
        "email": admin.email,
        "password_temporario": "admin123",
    }
