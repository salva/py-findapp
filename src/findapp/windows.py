import winreg
import pathlib
from findapp.base import BaseAppFinder

_default_registry_roots = [
    winreg.HKEY_LOCAL_MACHINE,
    winreg.HKEY_CURRENT_USER,
    winreg.HKEY_CLASSES_ROOT
]

class WindowsAppFinder(BaseAppFinder):

    selector = "windows"

    @classmethod
    def _get_paths_from_registry(cls,
                                app_name=None, vendor_name=None,
                                registry_roots=None, registry_paths=None,
                                **kwargs):
        search_paths = []

        if registry_roots is None:
            registry_roots = _default_registry_roots

        if registry_paths is None:
            registry_paths = [f"SOFTWARE\\{app_name}"]
            if vendor_name is not None:
                registry_paths.insert(0, f"SOFTWARE\\{vendor_name}\\{app_name}")

        for path in registry_paths:
            for root in registry_roots:
                try:
                    with winreg.OpenKey(root, path) as key:
                        install_path, _ = winreg.QueryValueEx(key, "")
                        search_paths.append(install_path)
                except FileNotFoundError:
                    continue
        return search_paths

    @classmethod
    def _get_common_paths(cls, app_name=None, vendor_name=None, **kwargs):
        search_paths = []
        for ev in ["PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA", "APPDATA"]:
            value = os.getenv(ev)
            if value is not None:
                search_paths.append(Path(value)/app_name)
        for ev in ["PROGRAMDATA", "APPDATA"]:
            value = os.getenv(ev)
            if value is not None:
                search_paths.append(Path(value) / "Microsoft/Windows/Start Menu/Programs"/app_name)
        return search_paths

    @classmethod
    def _find_app_in_common_places(cls, binary_name,
                                   search_in_registry=True,
                                   search_in_common_paths=True,
                                   **kwargs):
        if search_in_registry:
            search_paths = cls._get_paths_from_registry(**kwargs)
            path = cls._find_app_in_paths(binary_name, search_paths, **kwargs)
            if path is not None:
                return path

        if search_in_common_paths:
            search_paths = cls._get_common_paths(**kwargs)
            path = cls._find_app_in_paths(binary_name, search_paths, **kwargs)
            if path is not None:
                return path

        return None
