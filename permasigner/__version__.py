try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata
print(__package__)
__version__ = importlib_metadata.version(__package__)