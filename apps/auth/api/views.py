"""
Tenant auth — Bolt ``APIView`` (``django_bolt_guide.md``: ``AllowAny`` / ``JWTAuthentication``,
``BadRequest`` / ``Unauthorized``)।

``AUTH_USER_MODEL`` = ``apps.auth.models.User``। Access JWT এ ``typ: access``; refresh এ ``typ: refresh``।
OTP: ``POST …/login`` তারপর ``POST …/login/verify-otp``।
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
from django_bolt.exceptions import BadRequest, HTTPException, Unauthorized
from django_bolt.views import APIView

from .serializers import (
    CurrentUserResponse,
    ForgotPasswordBody,
    LoginBody,
    LoginTokenResponse,
    MessageResponse,
    ProfilePatchBody,
    RefreshTokenBody,
    RegisterBody,
    ResetPasswordBody,
    VerifyLoginOtpBody,
)

logger = logging.getLogger(__name__)
User = get_user_model()

AUTH_API_PREFIX = "/api/auth"
_MIN_PASSWORD_LEN = 8


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


class AuthRegister(_Public):
    async def post(self, data: RegisterBody) -> MessageResponse:
        email, pw = data.email.strip().lower(), data.password
        if not email or not pw:
            raise BadRequest(detail="email and password are required")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise BadRequest(detail="invalid email")
        if len(pw) < _MIN_PASSWORD_LEN:
            raise BadRequest(detail=f"password must be at least {_MIN_PASSWORD_LEN} characters")
        if await User.objects.filter(email=email).aexists():
            raise BadRequest(detail="email already registered")
        await sync_to_async(User.objects.create_user)(email=email, password=pw)
        return MessageResponse(detail="registered")


class AuthLogin(_Public):
    async def post(self, data: LoginBody) -> LoginTokenResponse:
        email, pw = data.email.strip().lower(), data.password
        if not email or not pw:
            raise BadRequest(detail="email and password are required")
        user = await sync_to_async(authenticate)(None, email=email, password=pw)
        if user is None:
            raise Unauthorized(detail="invalid email or password")

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
                raise HTTPException(status_code=503, detail="Could not send OTP email") from None
            return LoginTokenResponse(
                otp_required=True,
                detail="OTP sent to your email. Use POST /api/auth/login/verify-otp.",
                otp_expires_in=int(getattr(settings, "AUTH_OTP_VALID_SECONDS", 600)),
            )

        ref_sec = int(getattr(settings, "AUTH_REFRESH_TOKEN_SECONDS", 60 * 60 * 24 * 7))
        acc_sec = int(getattr(settings, "AUTH_ACCESS_TOKEN_SECONDS", 3600))
        return LoginTokenResponse(
            access=_access_token(user),
            refresh=_refresh_token(user),
            token_type="Bearer",
            expires_in=acc_sec,
            refresh_expires_in=ref_sec,
        )


class AuthVerifyLoginOtp(_Public):
    async def post(self, data: VerifyLoginOtpBody) -> LoginTokenResponse:
        email = data.email.strip().lower()
        otp = (data.otp or "").strip()
        if not email or not otp:
            raise BadRequest(detail="email and otp are required")
        user = await User.objects.filter(email=email).afirst()
        if not user or not user.login_otp_hash or not user.login_otp_expires_at:
            raise Unauthorized(detail="invalid or expired OTP")
        if timezone.now() > user.login_otp_expires_at:
            user.login_otp_hash, user.login_otp_expires_at = "", None
            await user.asave(update_fields=["login_otp_hash", "login_otp_expires_at"])
            raise Unauthorized(detail="invalid or expired OTP")
        if not check_password(otp, user.login_otp_hash):
            raise Unauthorized(detail="invalid or expired OTP")
        user.login_otp_hash, user.login_otp_expires_at = "", None
        await user.asave(update_fields=["login_otp_hash", "login_otp_expires_at"])
        ref_sec = int(getattr(settings, "AUTH_REFRESH_TOKEN_SECONDS", 60 * 60 * 24 * 7))
        acc_sec = int(getattr(settings, "AUTH_ACCESS_TOKEN_SECONDS", 3600))
        return LoginTokenResponse(
            access=_access_token(user),
            refresh=_refresh_token(user),
            token_type="Bearer",
            expires_in=acc_sec,
            refresh_expires_in=ref_sec,
        )


class AuthTokenRefresh(_Public):
    async def post(self, data: RefreshTokenBody) -> LoginTokenResponse:
        if not (data.refresh or "").strip():
            raise BadRequest(detail="refresh is required")
        claims = _decode_refresh(data.refresh)
        if claims.get("typ") != "refresh":
            raise Unauthorized(detail="invalid token type")
        try:
            pk = int(claims["sub"])
        except (TypeError, ValueError):
            raise Unauthorized(detail="invalid token") from None
        try:
            user = await User.objects.aget(pk=pk)
        except User.DoesNotExist:
            raise Unauthorized(detail="user not found") from None
        acc_sec = int(getattr(settings, "AUTH_ACCESS_TOKEN_SECONDS", 3600))
        ref_sec = int(getattr(settings, "AUTH_REFRESH_TOKEN_SECONDS", 60 * 60 * 24 * 7))
        return LoginTokenResponse(
            access=_access_token(user),
            refresh=data.refresh.strip(),
            token_type="Bearer",
            expires_in=acc_sec,
            refresh_expires_in=ref_sec,
        )


class AuthForgotPassword(_Public):
    async def post(self, data: ForgotPasswordBody) -> MessageResponse:
        ok = MessageResponse(detail="If that email exists, reset instructions were sent.")
        raw = (data.email or "").strip()
        if not raw:
            return ok
        email = raw.lower()
        if "@" not in email:
            raise BadRequest(detail="invalid email")
        u = await User.objects.filter(email=email).afirst()
        if not u:
            return ok
        tok = secrets.token_urlsafe(32)
        u.reset_token, u.reset_sent_at = tok, timezone.now()
        await u.asave(update_fields=["reset_token", "reset_sent_at"])
        logger.info("tenant_auth.password_reset token=%s email=%s", tok, email)
        return ok


class AuthResetPassword(_Public):
    async def post(self, data: ResetPasswordBody) -> MessageResponse:
        if not data.token or not data.new_password:
            raise BadRequest(detail="token and new_password are required")
        if len(data.new_password) < _MIN_PASSWORD_LEN:
            raise BadRequest(detail=f"new_password must be at least {_MIN_PASSWORD_LEN} characters")
        u = await User.objects.filter(reset_token=data.token).afirst()
        ttl = timedelta(hours=int(getattr(settings, "AUTH_PASSWORD_RESET_HOURS", 24)))
        if not u or not u.reset_sent_at or timezone.now() - u.reset_sent_at > ttl:
            raise BadRequest(detail="invalid or expired token")
        await sync_to_async(u.set_password)(data.new_password)
        u.reset_token, u.reset_sent_at = "", None
        await u.asave(update_fields=["password", "reset_token", "reset_sent_at"])
        return MessageResponse(detail="password updated")


class AuthMe(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> CurrentUserResponse:
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
        return CurrentUserResponse(id=int(pk), email=str(email), otp_enabled=otp)


class AuthProfile(APIView):
    """Toggle ``otp_enabled`` for the logged-in user (Bearer access token)."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def patch(self, data: ProfilePatchBody) -> CurrentUserResponse:
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
        return CurrentUserResponse(id=user.pk, email=user.email, otp_enabled=user.otp_enabled)


def attach_auth_routes(api: BoltAPI) -> None:
    """Register auth routes under ``AUTH_API_PREFIX`` (``/api/auth``)."""
    tag = ["auth"]
    p = AUTH_API_PREFIX
    api.view(p + "/register", methods=["POST"], status_code=201, tags=tag)(AuthRegister)
    api.view(p + "/login", methods=["POST"], tags=tag)(AuthLogin)
    api.view(p + "/login/verify-otp", methods=["POST"], tags=tag)(AuthVerifyLoginOtp)
    api.view(p + "/token/refresh", methods=["POST"], tags=tag)(AuthTokenRefresh)
    api.view(p + "/forgot-password", methods=["POST"], tags=tag)(AuthForgotPassword)
    api.view(p + "/reset-password", methods=["POST"], tags=tag)(AuthResetPassword)
    api.view(p + "/me", methods=["GET"], tags=tag)(AuthMe)
    api.view(p + "/profile", methods=["PATCH"], tags=tag)(AuthProfile)
