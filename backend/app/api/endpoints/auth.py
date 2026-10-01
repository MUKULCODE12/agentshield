from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Organization, AuditLog
from app.schemas.schemas import UserLogin, UserRegister, Token, UserOut
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(subject=user.id)

    audit = AuditLog(
        org_id=user.org_id,
        actor=user.email,
        action="USER_LOGIN",
        resource_type="User",
        resource_id=str(user.id),
        details={"email": user.email}
    )
    db.add(audit)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": user.org_id
        }
    }

@router.post("/register", response_model=Token)
def register(reg_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == reg_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User email already registered")

    # Create Org
    org_slug = reg_data.organization_name.lower().replace(" ", "-")
    org = Organization(name=reg_data.organization_name, slug=org_slug, plan="Enterprise")
    db.add(org)
    db.commit()
    db.refresh(org)

    # Create User
    user = User(
        org_id=org.id,
        email=reg_data.email,
        hashed_password=get_password_hash(reg_data.password),
        full_name=reg_data.full_name,
        role="Admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": user.org_id
        }
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
