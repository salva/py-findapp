import os
import pytest
import logging
from findapp import findapp

if os.name == "nt":
    import winreg

# Set up logging for debugging
# logging.basicConfig(level=logging.DEBUG)

# Mocking classes to simulate OS behavior
class MockWinregKey:
    def __init__(self, values):
        self.values = values

    def __enter__(self):
        logging.debug("Entering MockWinregKey context with values: %s", self.values)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug("Exiting MockWinregKey context.")

    def QueryValueEx(self, name):
        logging.debug("Querying value '%s' in MockWinregKey.", name)
        if name in self.values:
            result = self.values[name], 0
            logging.debug("Found value: %s", result)
            return result
        logging.debug("Value '%s' not found, raising FileNotFoundError.", name)
        raise FileNotFoundError

class MockWinreg:
    def __init__(self):
        self.registry = {}

    def OpenKey(self, root, path):
        logging.debug("Opening key with root: %s, path: %s", root, path)
        if (root, path) in self.registry:
            logging.debug("Key found in MockWinreg registry.")
            return MockWinregKey(self.registry[(root, path)])
        logging.debug("Key not found, raising FileNotFoundError.")
        raise FileNotFoundError

    def QueryValueEx(self, key, name):
        logging.debug("Querying value '%s' with key: %s", name, key)
        return key.QueryValueEx(name)

    def add_key(self, root, path, values):
        logging.debug("Adding key to MockWinreg: root=%s, path=%s, values=%s", root, path, values)
        self.registry[(root, path)] = values

class MockFilesystem:
    def __init__(self):
        self.files = {}

    def add_file(self, path):
        logging.debug("Adding file to MockFilesystem: %s", path)
        self.files[path] = True

    def which(self, binary_name):
        logging.debug("Searching for binary '%s' in MockFilesystem.", binary_name)
        for file in self.files:
            for extension in ("", ".exe"):
                if file == binary_name+extension:
                    logging.debug("Binary found: %s", file)
                    return file
        logging.debug("Binary '%s' not found.", binary_name)
        return None

@pytest.fixture
def patch_mock_calls(mocker):
    mock_winreg = MockWinreg()
    mock_filesystem = MockFilesystem()

    # Mock registry keys with distinct paths
    mock_winreg.add_key(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\TestVendor\\TestApp", {"": "C:\\Registry Vendor Program Files\\TestApp"})
    mock_winreg.add_key(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\TestApp", {"": "C:\\Registry Program Files\\TestApp"})

    # Mock filesystem files with distinct paths for registry tests
    mock_filesystem.add_file("C:\\Registry Vendor Program Files\\TestApp\\App.exe")
    mock_filesystem.add_file("C:\\Registry Program Files\\TestApp\\App.exe")

    # Mock filesystem files with distinct paths for environment variable searches
    mock_filesystem.add_file("C:\\Filesystem Program Files\\TestApp\\App.exe")
    mock_filesystem.add_file("C:\\Filesystem Vendor Program Files\\TestApp\\App.exe")
    mock_filesystem.add_file("C:\\Users\\User\\AppData\\Local\\TestApp\\App.exe")
    mock_filesystem.add_file("C:\\Users\\User\\AppData\\Roaming\\TestApp\\App.exe")
    mock_filesystem.add_file("C:\\Users\\User\\AppData\\Roaming\\App\\App.exe")
    mock_filesystem.add_file("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\TestApp\\App.exe")

    # Mock environment variables
    os.environ.update({
        "PROGRAMFILES": "C:\\Filesystem Program Files",
        "PROGRAMFILES(X86)": "C:\\Filesystem Program Files (x86)",
        "LOCALAPPDATA": "C:\\Users\\User\\AppData\\Local",
        "APPDATA": "C:\\Users\\User\\AppData\\Roaming",
        "PROGRAMDATA": "C:\\ProgramData",
    })

    mocker.patch("winreg.OpenKey", side_effect=mock_winreg.OpenKey)
    mocker.patch("winreg.QueryValueEx", side_effect=mock_winreg.QueryValueEx)
    mocker.patch("shutil.which", side_effect=mock_filesystem.which)

    return mocker

@pytest.mark.skipif(os.name != "nt", reason="Tests are only applicable on Windows.")
def test_findapp_function(patch_mock_calls):
    # Test the function
    path = findapp("App", vendor_name="TestVendor", app_name="TestApp", cached=False)

    assert path == "C:\\Registry Vendor Program Files\\TestApp\\App.exe"

@pytest.mark.skipif(os.name != "nt", reason="Tests are only applicable on Windows.")
def test_findapp_no_vendor(patch_mock_calls):
    # Test the function
    path = findapp("App", app_name="TestApp", cached=False)

    assert path == "C:\\Registry Program Files\\TestApp\\App.exe"

@pytest.mark.skipif(os.name != "nt", reason="Tests are only applicable on Windows.")
def test_findapp_in_filesystem_only(patch_mock_calls):
    # Test the function
    path = findapp("App", app_name="TestApp", search_in_registry=False, cached=False)

    assert path == "C:\\Filesystem Program Files\\TestApp\\App.exe"

@pytest.mark.skipif(os.name != "nt", reason="Tests are only applicable on Windows.")
def test_findapp_less_args(patch_mock_calls):
    # Test the function
    path = findapp("App", cached=False)

    assert path == "C:\\Users\\User\\AppData\\Roaming\\App\\App.exe"
    
@pytest.mark.skipif(os.name != "nt", reason="Tests are only applicable on Windows.")
def test_findapp_in_registry_only(patch_mock_calls):
    # Test the function
    path = findapp("App", vendor_name="TestVendor", app_name="TestApp", search_in_path=False, cached=False)

    assert path == "C:\\Registry Vendor Program Files\\TestApp\\App.exe"
