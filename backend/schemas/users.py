# ==========================================
# SNEAKERSTUFF AUTH REFACTOR
# Modified by Sneakerstuff Developer
# Purpose:
# Authentication now uses email instead of username.
# ==========================================

import re
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

class UserLogin(BaseModel):
    # Standard OAuth2 fields. Under form-urlencoded login, the email
    # will be mapped to the username property.
    username: str
    password: str

class UserSignup(BaseModel):
    # Signups require username, email, and password.
    username: str
    email: str
    password: str

    # Custom regex field validator to ensure a valid email format
    # without requiring external validator dependencies.
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", v):
            raise ValueError("Invalid email format (e.g. user@domain.com)")
        return v.strip().lower()

    # Password length validation enforced at schema validation level.
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

class UserResponse(BaseModel):
    id: int
    role: str
    username: str
    # Added email to UserResponse schema to support frontend profile displays.
    email: str

    # Pydantic v2 Config mapping
    model_config = ConfigDict(from_attributes=True)