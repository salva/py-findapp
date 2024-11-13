import shutil
import os.path
import pathlib

_cache = {}

class BaseAppFinder:

    @classmethod
    def find_app(cls, binary_name, cached=True, **kwargs):
        if cached:
            path = _cache.get(binary_name)
            if path is None:
                path = cls._find_app_with_by_os(binary_name=binary_name, **kwargs)
                _cache[binary_name] = path
            return path

        return cls._find_app_with_by_os(binary_name=binary_name, **kwargs)

    @classmethod
    def _find_app_with_by_os(cls, by_os=None, **kwargs):
        if by_os:
            extra_kwargs = by_os.get(cls.selector)
            if extra_kwargs:
                kwargs = {**kwargs, **extra_kwargs}
        return cls._find_app_no_cache(**kwargs)

    @classmethod
    def _find_app_no_cache(cls, binary_name, search_in_path=True, more_search_paths=None, **kwargs):
        binary_name_path = pathlib.Path(binary_name)
        kwargs.setdefault("app_name", binary_name_path.stem)
        kwargs.setdefault("vendor_name", None)

        if str(binary_name_path.name) != binary_name:
            # When a path is given, we assume it is coming from a
            # configuration file or similar and don't search anywhere
            # else.
            path = cls._find_app_which(binary_name, **kwargs)
            if path is None:
                raise FileNotFoundError(f"Could not find an executable at {binary_name}")
            return path

        if search_in_path:
            path = cls._find_app_which(binary_name, **kwargs)
            if path is not None:
                return path

        if more_search_paths:
            path = cls._find_app_in_paths(binary_name, more_search_paths, **kwargs)
            if path is not None:
                return path

        path = cls._find_app_in_common_places(binary_name, **kwargs)
        if path is not None:
            return path

        raise FileNotFoundError(f"Could not find {binary_name}")

    @classmethod
    def _find_app_which(cls, binary_name, **kwargs):
        # We use shutil.which because it is cross-platform and it
        # automatically adds extensions to file names while handling
        # absolute paths correctly.
        return shutil.which(binary_name)

    @classmethod
    def _find_app_in_paths(cls, binary_name, search_paths, **kwargs):
        if search_paths:
            for search_path in search_paths:
                if search_path is not None:
                    path = cls._find_app_which(str((pathlib.Path(search_path)/binary_name).resolve()))
                    if path is not None:
                        return path
        return None

    @classmethod
    def _find_app_in_common_places(cls, binary_name, **kwargs):
        return None
