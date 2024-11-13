# FindApp Python Package

## Overview

Finding an executable on POSIX-based operating systems, such as Linux and macOS, is generally straightforward because most applications are installed in standard locations and added to the global PATH. This means they can be easily found by simply searching the system PATH. On Windows, however, applications are often installed in their own directories, which are not typically added to the global PATH. As a result, locating an application from another program can be challenging.

This project provides a cross-platform Python package for finding application binaries. It uses OS-specific methods to locate application binaries efficiently, leveraging caching and various techniques to search for binaries, including checking common locations, system paths, and Windows registry entries. The utility is designed to adapt its search strategy based on the current operating system.

## Features

- Cross-platform support for Windows, Linux, and macOS.
- Caching mechanism to avoid redundant searches.
- Windows-specific enhancements: searches in registry and common installation paths.
- Supports custom search paths.

## Installation

To use the FindApp package, you can install it via pip:

```sh
pip install findapp
```

## Usage

### Basic Usage

The main function provided by the module is `findapp()`, which allows you to locate the path to an application binary.

```python
from findapp import findapp

# Find the path to Python executable
python_path = findapp("python3")
print(python_path)
```

### Windows-Specific Usage

On Windows, you can provide additional arguments to refine the search:

```python
# Find Notepad using Windows registry and common paths
notepad_path = findapp("notepad", search_in_registry=True, search_in_common_paths=True)
print(notepad_path)

# Search with vendor-specific registry paths
myapp_path = findapp("myapp", vendor_name="MyVendor", registry_paths=["SOFTWARE\MyVendor\MyApp"])
print(myapp_path)

# Search only in the current user's registry keys
app_path = findapp("app", registry_roots=[winreg.HKEY_CURRENT_USER])
print(app_path)
```

## Parameters

The `findapp()` function provides several parameters to customize the search:

- **binary\_name (str)**: The name of the application binary to find. It can also be a path (see [Using Paths as `binary_name`](#using-paths-as-binary_name) for more details).
- **cached (bool, optional)**: Whether to use a cached result if available. Default is `True`.
- **search\_in\_path (bool, optional)**: Whether to search in the system PATH. Default is `True`.
- **more\_search\_paths (list, optional)**: Additional directories to search for the binary.
- **search\_in\_registry (bool, optional, Windows-only)**: Whether to search in the Windows registry for installation paths. Default is `True`.
- **search\_in\_common\_paths (bool, optional, Windows-only)**: Whether to search in common Windows installation paths. Default is `True`.
- **vendor\_name (str, optional, Windows-only)**: The vendor name for more specific registry searches.
- **registry\_roots (list, optional, Windows-only)**: A list of registry root keys to search in. Default is common Windows registry roots.
- **registry\_paths (list, optional, Windows-only)**: Specific registry paths to search for the application. Default is `['SOFTWARE\{app_name}', 'SOFTWARE\{vendor_name}\{app_name}']` if `vendor_name` is provided.

### Error Handling

The `findapp()` function raises a `FileNotFoundError` if the specified application cannot be found.

```python
try:
    unknown_app_path = findapp("unknown_app")
except FileNotFoundError as e:
    print(e)  # Output: Could not find unknown_app
```

### Using Paths as `binary_name`

The `findapp()` function also allows the `binary_name` parameter to be specified as a relative or absolute path. This can be useful when allowing users to set a custom value in a configuration file.

If a path is given, `findapp` will only verify the existence of the given path without searching in other locations.

Example:

```python
# Use a custom path set in a configuration file, defaulting to "myapp" if not set
path = findapp(cfg.get("app_path", "myapp"))

# If a relative or absolute path is provided, `findapp` will just check that the given path is correct
# but will not look for the application elsewhere.
print(path)
```

## Search Order by Operating System

The `findapp` function employs a systematic search order to locate application binaries, with different strategies depending on the operating system being used. Below is the detailed search order for each supported operating system.

### POSIX-Based Systems (Linux and macOS)

1. **System PATH**: The function first searches the system PATH to locate the binary. This is the most common and efficient method to find executables, as most installed applications are added to the PATH.
2. **Additional Search Paths**: If the `more_search_paths` parameter is provided, the function will then search in these user-specified directories.

### Windows

1. **System PATH**: The initial search is performed in the system PATH, similar to POSIX systems, to check if the application binary is accessible globally.
2. **Additional Search Paths**: The function will also search in any user-specified directories provided via the `more_search_paths` parameter. This is an optional step that can help locate binaries installed in non-standard locations.
3. **Windows Registry**: If the `search_in_registry` parameter is set to `True`, the function will attempt to locate the application in the Windows Registry. It searches in the specified `registry_roots` and `registry_paths` to find installation information for the application. This step helps locate software that may not have added itself to the global PATH.
4. **Common Installation Paths**: If the `search_in_common_paths` parameter is enabled, the function will check common directories where applications are typically installed, such as `Program Files`, `Program Files (x86)`, and `AppData` directories.

This structured search order ensures that the `findapp` function is able to locate application binaries in a flexible and efficient manner, considering the unique characteristics of each operating system.

## Contributing

Contributions are welcome! If you encounter bugs or have suggestions for improvements, please create an issue or submit a pull request on GitHub.

GitHub Repository: [FindApp on GitHub](https://github.com/salva/py-findapp)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Copyright

Copyright (c) 2024 Salvador Fandiño ([sfandino@yahoo.com](mailto:sfandino@yahoo.com)).

This project is licensed under the MIT License.

