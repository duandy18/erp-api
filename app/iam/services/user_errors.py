from __future__ import annotations


class AuthorizationError(Exception):
    pass


class NotFoundError(Exception):
    pass


__all__ = ["AuthorizationError", "NotFoundError"]
