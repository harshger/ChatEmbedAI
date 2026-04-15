from pydantic import BaseModel
from typing import List, Optional


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    company_name: Optional[str] = None
    website_url: Optional[str] = ''
    marketing_consent: bool = False
    scan_consent: bool = False
    terms_accepted: bool = True


class UserLogin(BaseModel):
    email: str
    password: str


class ChatbotCreate(BaseModel):
    business_name: str
    faq_content: str
    primary_language: str = 'de'
    auto_detect_language: bool = True
    widget_color: str = '#6366f1'
    show_gdpr_notice: bool = True
    widget_position: str = 'bottom-right'
    widget_greeting: str = ''
    hide_branding: bool = False
    custom_logo_url: str = ''
    widget_border_radius: str = 'rounded'


class ChatbotUpdate(BaseModel):
    business_name: Optional[str] = None
    faq_content: Optional[str] = None
    primary_language: Optional[str] = None
    auto_detect_language: Optional[bool] = None
    widget_color: Optional[str] = None
    show_gdpr_notice: Optional[bool] = None
    is_active: Optional[bool] = None
    widget_position: Optional[str] = None
    widget_greeting: Optional[str] = None
    hide_branding: Optional[bool] = None
    custom_logo_url: Optional[str] = None
    widget_border_radius: Optional[str] = None


class ChatMessage(BaseModel):
    chatbot_id: str
    message: str
    session_id: str
    history: Optional[List[dict]] = []
    widget_consent: bool = True


class ConsentLog(BaseModel):
    consent_type: str
    granted: bool
    session_id: Optional[str] = None


class CheckoutRequest(BaseModel):
    plan: str
    origin_url: str


class DeleteAccountRequest(BaseModel):
    confirmation: str


class TeamInvite(BaseModel):
    email: str
    role: str = 'member'


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: str


class DomainVerifyRequest(BaseModel):
    method: str
