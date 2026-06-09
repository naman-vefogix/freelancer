from contextvars import ContextVar

current_user: ContextVar = ContextVar('current_user', default=None)
current_request: ContextVar = ContextVar('current_request', default=None)