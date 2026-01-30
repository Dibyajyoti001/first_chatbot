# src/server_state.py
# Holds runtime globals (set by backend startup). Import this from handlers/routes.

GRAPH = None
_CHECKPOINT_CTX = None
_STORE_CTX = None
