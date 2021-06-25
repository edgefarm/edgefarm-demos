from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    dist_name = "preload-db"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
