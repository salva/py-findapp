"""This module provides a cross-platform utility for finding application binaries.

The search leverages caching and various techniques to find the binary
efficiently, including checking common locations and searching in
system paths. On Windows, additional search techniques include looking
up the registry and common installation paths.

Functions:
- findapp(binary_name, **kwargs): Finds the specified application by its binary name.

Usage Example:

    # Searches with vendor-specific registry paths.
    path = findapp("myapp", vendor_name="MyVendor")

    # Searches only in the current user's registry keys.
    path = findapp("app", registry_roots=[winreg.HKEY_CURRENT_USER])

    # Finds DBeaver using a custom configuration for windows
    path = findapp("dbeaver", by_os={'windows': {'binary_name': 'dbeaver-cli'}})

"""

__version__ = "0.0.1"

import os
if os.name == "nt":
    from findapp.windows import WindowsAppFinder as AppFinder
else:
    # TODO: Check for MacOS!
    from findapp.posix import PosixAppFinder as AppFinder

def findapp(binary_name, **kwargs):
    """
    Find the specified application by its binary name.

    This function uses OS-specific methods to locate the requested application binary, adapting the search strategy
    depending on the current operating system. On Windows, it additionally searches in the registry and common
    installation paths. The search can be cached for efficiency and can also be customized using additional parameters.

    Parameters:
    binary_name (str): The name of the application binary to find.
    cached (bool, optional): Whether to use a cached result if available. Default is True.
    search_in_path (bool, optional): Whether to search in the system PATH. Default is True.
    more_search_paths (list, optional): Additional directories to search for the binary.
    search_in_registry (bool, optional, Windows-only): Whether to search in the Windows registry for installation
                                                       paths. Default is True.
    search_in_common_paths (bool, optional, Windows-only): Whether to search in common Windows installation paths.
                                                           Default is True.
    vendor_name (str, optional, Windows-only): The vendor name for more specific registry searches.
    registry_roots (list, optional, Windows-only): A list of registry root keys to search in. Default is common Windows
                                                   registry roots.
    registry_paths (list, optional, Windows-only): Specific registry paths to search for the application. Default is
                                                   ['SOFTWARE\\{app_name}', 'SOFTWARE\\{vendor_name}\\{app_name}']
                                                   if vendor_name is provided.

    Returns:
    str: The path to the application binary if found, or raises FileNotFoundError if not found.

    Raises:
    FileNotFoundError: If the specified application cannot be found.
    """
    return AppFinder.find_app(binary_name, **kwargs)
