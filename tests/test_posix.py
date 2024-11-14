import os
import pytest
import logging
from findapp import findapp

# Set up logging for debugging
# logging.basicConfig(level=logging.DEBUG)

# Mocking classes to simulate OS behavior
class MockFilesystem:
    def __init__(self):
        self.files = {}

    def add_file(self, path):
        logging.debug("Adding file to MockFilesystem: %s", path)
        self.files[path] = True

    def is_file(self, path):
        logging.debug("Checking if file exists in MockFilesystem: %s", path)
        return path in self.files

    def which(self, command_name):
        logging.debug("Searching for command '%s' in MockFilesystem.", command_name)
        # If the command does not contain slashes, return a hardcoded path
        if "/" not in command_name:
            # Assume PATH=/usr/bin
            command_name = f"/usr/bin/{command_name}"
        # Otherwise, check the internal registry
        if command_name in self.files:
            logging.debug(f"Command found: {command_name}")
            return command_name
        logging.debug(f"Command '{command_name}' not found.")
        return None

@pytest.fixture
def patch_mock_calls(mocker):
    mock_filesystem = MockFilesystem()

    # Mock filesystem files with distinct paths for environment variable searches
    mock_filesystem.add_file("/usr/local/bin/TestApp")
    mock_filesystem.add_file("/usr/bin/app")
    mock_filesystem.add_file("/home/user/.local/bin/TestApp")
    mock_filesystem.add_file("/opt/TestVendor/TestApp/bin/TestApp")
    mock_filesystem.add_file("/home/user/.config/TestApp/TestApp")

    mocker.patch("os.path.isfile", side_effect=mock_filesystem.is_file)
    mocker.patch("shutil.which", side_effect=mock_filesystem.which)

    return mock_filesystem

@pytest.mark.skipif(os.name != "posix", reason="Tests are only applicable on POSIX systems.")
def test_findapp_function(patch_mock_calls):
    path = findapp("app", cached=False)
    assert path == "/usr/bin/app"

@pytest.mark.skipif(os.name != "posix", reason="Tests are only applicable on POSIX systems.")
def test_findapp_useless_args(patch_mock_calls):
    path = findapp("app", vendor_name="TestVendor", app_name="TestApp", cached=False)
    assert path == "/usr/bin/app"

@pytest.mark.skipif(os.name != "posix", reason="Tests are only applicable on POSIX systems.")
def test_findapp_with_path(patch_mock_calls):
    path = findapp("/home/user/.local/bin/TestApp", cached=False)
    assert path == "/home/user/.local/bin/TestApp"


@pytest.mark.skipif(os.name != "posix", reason="Tests are only applicable on POSIX systems.")
def test_findapp_not_found(patch_mock_calls):
    with pytest.raises(FileNotFoundError):
        findapp("NonExistentApp", cached=False)

@pytest.mark.skipif(os.name != "posix", reason="Tests are only applicable on POSIX systems.")
def test_findapp_with_path_not_found(patch_mock_calls):
    with pytest.raises(FileNotFoundError):
        findapp("/home/user/nonexistent/path/TestApp", cached=False)
