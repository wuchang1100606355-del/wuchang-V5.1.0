import sys
try:
    import importlib_metadata
    import importlib.metadata
    if not hasattr(importlib.metadata, \ packages_distributions\):
        importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
except ImportError:
    pass
