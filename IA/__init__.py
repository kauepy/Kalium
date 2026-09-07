try:
    from .assistant import responder
except ImportError:
    from assistant import responder

__all__ = ["responder"]