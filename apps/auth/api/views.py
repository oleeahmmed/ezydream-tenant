"""
Tenant auth — Bolt ``APIView`` (access + refresh JWT, optional email OTP, profile OTP flag).

``AUTH_USER_MODEL`` = ``tenant_auth.User``. Access tokens carry ``typ: access`` (for ``/me``);
refresh carries ``typ: refresh``. OTP login: ``POST /login`` then ``POST /login/verify-otp``.
"""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.utils import timezone
from django_bolt import BoltAPI
from django_bolt.auth import AllowAny, IsAuthenticated, JWTAuthentication, Token
from django_bolt.exceptions import HTTPException, Unauthorized
from django_bolt.serializers import Serializer, field
from django_bolt.views import APIView

logger = logging.getLogger(__name__)
User = get_user_model()

_P = "/api/auth"
_MIN = 8


def _u(s: str) -> str:
    return f"{_P}{s}"


# --- serializers ---


class RegisterIn(Serializer):
    email: str
    password: str


class LoginIn(Serializer):
    email: str
    password: str


class VerifyLoginOtpIn(Serializer):
    email: str
    otp: str


class RefreshIn(Serializer):
    refresh: str


class ForgotPasswordIn(Serializer):
    email: str | None = field(default=None)


class ResetPasswordIn(Serializer):
    token: str
    new_password: str


class MessageOut(Serializer):
    detail: str


class LoginResponse(Serializer):
    """Password-only login: tokens. OTP flow: ``otp_required`` + ``detail`` + ``otp_expires_in``."""

    otp_required: bool = field(default=False)
    detail: str = field(default="")
    access: str = field(default="")
    refresh: str = field(default="")
    token_type: str = field(default="Bearer")
    expires_in: int = field(default=0)
    refresh_expires_in: int = field(default=0)
    otp_expires_in: int = field(default=0)


class MeOut(Serializer):
    id: int
    email: str
    otp_enabled: bool


class ProfilePatchIn(Serializer):
    otp_enabled: bool


# --- helpers ---


def _access_token(user: User) -> str:
    sec = int(getattr(settings, "AUTH_ACCESS_TOKEN_SECONDS", 3600))
    exp = datetime.now(UTC) + timedelta(seconds=sec)
    return Token(
        sub=str(user.pk),
        exp=exp,
        extras={"email": user.email, "typ": "access"},
    ).encode(secret=settings.SECRET_KEY, algorithm="HS256")


def _refresh_token(user: User) -> str:
    sec = int(getattr(settings, "AUTH_REFRESH_TOKEN_SECONDS", 60 * 60 * 24 * 7))
    exp = datetime.now(UTC) + timedelta(seconds=sec)
    return Token(
        sub=str(user.pk),
        exp=exp,
        extras={"email": user.email, "typ": "refresh"},
    ).encode(secret=settings.SECRET_KEY, algorithm="HS256")


def _otp_digits() -> str:
    n = max(4, min(10, int(getattr(settings, "AUTH_OTP_LENGTH", 6))))
    return f"{secrets.randbelow(10**n):0{n}d}"


def _send_login_otp_email(to_email: str, code: str) -> None:
    subject = getattr(settings, "AUTH_LOGIN_OTP_SUBJECT", "Your login verification code")
    body = (
        f"Your one-time login code is: {code}\n\n"
        f"It expires in {getattr(settings, 'AUTH_OTP_VALID_SECONDS', 600)} seconds.\n"
        "If you did not try to log in, ignore this email."
    )
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
        [to_email],
        fail_silently=False,
    )


def _bad(st: int, msg: str) -> None:
    if st == 401:
        raise Unauthorized(detail=msg)
    raise HTTPException(status_code=st, detail=msg)


def _decode_refresh(raw: str) -> dict:
    try:
        return jwt.decode(
            raw.strip(),
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as e:
        raise Unauthorized(detail="Invalid or expired refresh token") from e


class _Public(APIView):
    auth: list = []
    guards = [AllowAny()]


class AuthRegisterView(_Public):
    async def post(self, data: RegisterIn) -> MessageOut:
        email, pw = data.email.strip().lower(), data.password
        if not email or not pw:
            _bad(400, "email and password are required")
        if "@" not in email or "." not in email.split("@")[-1]:
            _bad(400, "invalid email")
        if len(pw) < _MIN:
            _bad(400, f"password must be at least {_MIN} characters")
        if await User.objects.filter(email=email).aexists():
            _bad(400, "email already registered")
        await sync_to_async(User.objects.create_user)(email=email, password=pw)
        return MessageOut(detail="registered")


class AuthLoginView(_Public):
    async def post(self, data: LoginIn) -> LoginResponse:
        email, pw = data.email.strip().lower(), data.password
        if not email or not pw:
            _bad(400, "email and password are required")
        user = await sync_to_async(authenticate)(None, email=email, password=pw)
        if user is None:
            _bad(401, "invalid email or password")

        if user.otp_enabled:
            code = _otp_digits()
            user.login_otp_hash = make_password(code)
            user.login_otp_expires_at = timezone.now() + timedelta(
                seconds=int(getattr(settings, "AUTH_OTP_VALID_SECONDS", 600))
            )
            await user.asave(update_fields=["login_otp_hash", "login_otp_expires_at"])
            try:
                await sync_to_async(_send_login_otp_email)(user.email, code)
            except Exception:
                logger.exception("tenant_auth.login_otp email failed email=%s", email)
                _bad(500, "Could not send OTP email")
            return LoginResponse(
                otp_required=True,
                detail="OTP sent to your email. Use POST /api/auth/login/verify-otp.",
                otp_expires_in=int(getattr(settings, "AUTH_OTP_VALID_SECONDS", 600)),
            )

        ref_sec = int(getattr(settings, "AUTH_REFRESH_TOKEN_SECONDS", 60 * 60 * 24 * 7))
        acc_sec = int(getattr(settings, "AUTH_ACCESS_TOKEN_SECONDS", 3600))
        return LoginResponse(
            access=_access_token(user),
            refresh=_refresh_token(user),
            token_type="Bearer",
            expires_in=acc_sec,
            refresh_expires_in=ref_sec,
        )


class AuthVerifyLoginOtpView(_Public):
    async def post(self, data: VerifyLoginOtpIn) -> LoginResponse:
        email = data.email.strip().lower()
        otp = (data.otp or "").strip()
        if not email or not otp:
            _bad(400, "email and otp are required")
        user = await User.objects.filter(email=email).afirst()
        if not user or not user.login_otp_hash or not user.login_otp_expires_at:
            _bad(401, "invalid or expired OTP")
        if timezone.now() > user.login_otp_expires_at:
            user.login_otp_hash, user.login_otp_expires_at = "", None
            await user.asave(update_fields=["login_otp_hash", "login_otp_expires_at"])
            _bad(401, "invalid or expired OTP")
        if not check_password(otp, user.login_otp_hash):
            _bad(401, "invalid or expired OTP")
        user.login_otp_hash, user.login_otp_expires_at = "", None
        await user.asave(update_fields=["login_otp_hash", "login_otp_expires_at"])
        ref_sec = int(getattr(settings, "AUTH_REFRESH_TOKEN_SECONDS", 60 * 60 * 24 * 7))
        acc_sec = int(getattr(settings, "AUTH_ACCESS_TOKEN_SECONDS", 3600))
        return LoginResponse(
            access=_access_token(user),
            refresh=_refresh_token(user),
            token_type="Bearer",
            expires_in=acc_sec,
            refresh_expires_in=ref_sec,
        )


class AuthTokenRefreshView(_Public):
    async def post(self, data: RefreshIn) -> LoginResponse:
        if not (data.refresh or "").strip():
            _bad(400, "refresh is required")
        claims = _decode_refresh(data.refresh)
        if claims.get("typ") != "refresh":
            _bad(401, "invalid token type")
        try:
            pk = int(claims["sub"])
        except (TypeError, ValueError):
            _bad(401, "invalid token")
        try:
            user = await User.objects.aget(pk=pk)
        except User.DoesNotExist:
            _bad(401, "user not found")
        acc_sec = int(getattr(settings, "AUTH_ACCESS_TOKEN_SECONDS", 3600))
        ref_sec = int(getattr(settings, "AUTH_REFRESH_TOKEN_SECONDS", 60 * 60 * 24 * 7))
        return LoginResponse(
            access=_access_token(user),
            refresh=data.refresh.strip(),
            token_type="Bearer",
            expires_in=acc_sec,
            refresh_expires_in=ref_sec,
        )


class AuthForgotView(_Public):
    async def post(self, data: ForgotPasswordIn) -> MessageOut:
        ok = MessageOut(detail="If that email exists, reset instructions were sent.")
        raw = (data.email or "").strip()
        if not raw:
            return ok
        email = raw.lower()
        if "@" not in email:
            _bad(400, "invalid email")
        u = await User.objects.filter(email=email).afirst()
        if not u:
            return ok
        tok = secrets.token_urlsafe(32)
        u.reset_token, u.reset_sent_at = tok, timezone.now()
        await u.asave(update_fields=["reset_token", "reset_sent_at"])
        logger.info("tenant_auth.password_reset token=%s email=%s", tok, email)
        return ok


class AuthResetView(_Public):
    async def post(self, data: ResetPasswordIn) -> MessageOut:
        if not data.token or not data.new_password:
            _bad(400, "token and new_password are required")
        if len(data.new_password) < _MIN:
            _bad(400, f"new_password must be at least {_MIN} characters")
        u = await User.objects.filter(reset_token=data.token).afirst()
        ttl = timedelta(hours=int(getattr(settings, "AUTH_PASSWORD_RESET_HOURS", 24)))
        if not u or not u.reset_sent_at or timezone.now() - u.reset_sent_at > ttl:
            _bad(400, "invalid or expired token")
        await sync_to_async(u.set_password)(data.new_password)
        u.reset_token, u.reset_sent_at = "", None
        await u.asave(update_fields=["password", "reset_token", "reset_sent_at"])
        return MessageOut(detail="password updated")


class AuthMeView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> MeOut:
        ctx = (self.request.get("auth") if hasattr(self.request, "get") else None) or {}
        claims = ctx.get("auth_claims") or {}
        if claims.get("typ") not in (None, "access"):
            raise Unauthorized(detail="Use access token, not refresh")
        u = self.request.user
        pk = getattr(u, "pk", None)
        if pk is None:
            raise Unauthorized(detail="Authentication required")
        email = getattr(u, "email", None) or ""
        otp = bool(getattr(u, "otp_enabled", False))
        return MeOut(id=int(pk), email=str(email), otp_enabled=otp)


class AuthProfileView(APIView):
    """Toggle ``otp_enabled`` for the logged-in user (Bearer access token)."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def patch(self, data: ProfilePatchIn) -> MeOut:
        ctx = (self.request.get("auth") if hasattr(self.request, "get") else None) or {}
        claims = ctx.get("auth_claims") or {}
        if claims.get("typ") not in (None, "access"):
            raise Unauthorized(detail="Use access token, not refresh")
        u = self.request.user
        pk = getattr(u, "pk", None)
        if pk is None:
            raise Unauthorized(detail="Authentication required")
        user = await User.objects.aget(pk=pk)
        user.otp_enabled = bool(data.otp_enabled)
        await user.asave(update_fields=["otp_enabled"])
        return MeOut(id=user.pk, email=user.email, otp_enabled=user.otp_enabled)


def attach_auth_routes(api: BoltAPI) -> None:
    api.view(_u("/register"), methods=["POST"], status_code=201, tags=["auth"])(
        AuthRegisterView
    )
    api.view(_u("/login"), methods=["POST"], tags=["auth"])(AuthLoginView)
    api.view(_u("/login/verify-otp"), methods=["POST"], tags=["auth"])(
        AuthVerifyLoginOtpView
    )
    api.view(_u("/token/refresh"), methods=["POST"], tags=["auth"])(AuthTokenRefreshView)
    api.view(_u("/forgot-password"), methods=["POST"], tags=["auth"])(AuthForgotView)
    api.view(_u("/reset-password"), methods=["POST"], tags=["auth"])(AuthResetView)
    api.view(_u("/me"), methods=["GET"], tags=["auth"])(AuthMeView)
    api.view(_u("/profile"), methods=["PATCH"], tags=["auth"])(AuthProfileView)
