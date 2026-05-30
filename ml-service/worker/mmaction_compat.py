# ml-service/worker/mmaction_compat.py
"""
Compatibility layer for MMAction2 imports.
Handles the broken package installation by wrapping imports.
"""

try:
    # Try proper import first
    from mmaction.apis import init_recognizer, inference_recognizer # type: ignore
except ImportError:
    # Fallback to workaround path
    from mmaction2.mmaction.apis import init_recognizer, inference_recognizer

__all__ = ['init_recognizer', 'inference_recognizer']