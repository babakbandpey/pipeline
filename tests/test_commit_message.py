# test_commit_message.py

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from unittest.mock import call

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Assuming the commit_message.py is in the same directory and the functions are imported
from scripts.commit_message import (
    split_diff_by_file,
    create_commit_message,
    run_pytest,
    create_commit_message_file,
    main
)

# ----------------------------
# Test split_diff_by_file
# ----------------------------

def test_split_diff_by_file_empty_diff():
    """
    Test split_diff_by_file function with an empty diff file.
    """
    with patch('scripts.commit_message.FileUtils.read_file', return_value=''):
        result = split_diff_by_file('/path/to/diff.txt')
        assert result == []

def test_split_diff_by_file_single_file():
    """
    Test split_diff_by_file function with a single file diff.
    """
    diff_content = """diff --git a/file1.py b/file1.py
index e69de29..0d1d7fc 100644
--- a/file1.py
+++ b/file1.py
@@ -0,0 +1,2 @@
+print("Hello World")
+print("Test")"""
    with patch('scripts.commit_message.FileUtils.read_file', return_value=diff_content):
        result = split_diff_by_file('/path/to/diff.txt')
        assert len(result) == 1
        assert 'diff --git a/file1.py b/file1.py' in result[0]

def test_split_diff_by_file_multiple_files():
    """
    Test split_diff_by_file function with multiple file diffs.
    """
    diff_content = """diff --git a/file1.py b/file1.py
index e69de29..0d1d7fc 100644
--- a/file1.py
+++ b/file1.py
@@ -0,0 +1,2 @@
+print("Hello World")
+print("Test")
diff --git a/file2.py b/file2.py
index e69de29..0d1d7fc 100644
--- a/file2.py
+++ b/file2.py
@@ -0,0 +1,2 @@
+print("Another File")
+print("Testing")"""
    with patch('scripts.commit_message.FileUtils.read_file', return_value=diff_content):
        result = split_diff_by_file('/path/to/diff.txt')
        assert len(result) == 2
        assert 'diff --git a/file1.py b/file1.py' in result[0]
        assert 'diff --git a/file2.py b/file2.py' in result[1]

# ----------------------------
# Test create_commit_message
# ----------------------------

def test_create_commit_message_success():
    """
    Test create_commit_message function with a valid JSON response
    """
    mock_chatbot = MagicMock()
    mock_response = """
    {
        "title": "Add new feature",
        "description": ["Implemented the new feature X.", "Refactored the Y module."],
        "type": "feature"
    }
    """
    mock_chatbot.invoke.return_value = mock_response

    with patch('scripts.commit_message.ChatbotUtils.parse_json', return_value={
        "title": "Add new feature",
        "description": ["Implemented the new feature X.", "Refactored the Y module."],
        "type": "feature"
    }):
        commit_message = create_commit_message(mock_chatbot)
        expected_message = (
            "Add new feature\n\nDescription:\n"
            "1. Implemented the new feature X.\n"
            "2. Refactored the Y module.\n\nType: feature"
        )
        assert commit_message == expected_message
        mock_chatbot.invoke.assert_called_once()

def test_create_commit_message_invalid_json():
    """
    Test create_commit_message function with an invalid JSON response
    """
    mock_chatbot = MagicMock()
    mock_chatbot.invoke.return_value = "Invalid JSON"

    with patch('scripts.commit_message.ChatbotUtils.parse_json', return_value=None), \
         patch('scripts.commit_message.logger') as mock_logger:
        commit_message = create_commit_message(mock_chatbot)
        assert commit_message is None
        mock_logger.warning.assert_called_with("Invalid JSON format. Trying again... Press CTRL+C to abort.")

def test_create_commit_message_exception():
    """
    Test create_commit_message function with an exception raised by the chatbot
    """
    mock_chatbot = MagicMock()
    mock_chatbot.invoke.side_effect = ValueError("Chatbot error")

    with patch('scripts.commit_message.logger') as mock_logger:
        commit_message = create_commit_message(mock_chatbot)
        assert commit_message is False
        mock_logger.error.assert_called_with("Error generating commit message: %s", "Chatbot error")

# ----------------------------
# Test run_pytest
# ----------------------------

def test_run_pytest_success():
    """
    Test run_pytest function with a successful test run.
    """
    with patch('scripts.commit_message.subprocess.run') as mock_run, \
         patch('scripts.commit_message.logger') as mock_logger:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "All tests passed."
        mock_run.return_value.stderr = ""

        result = run_pytest()
        assert result is True
        mock_run.assert_called_once_with(['pytest'], capture_output=True, text=True)
        mock_logger.info.assert_called_with("All tests passed successfully.")

def test_run_pytest_failure():
    """
    Test run_pytest function with a failed test run.
    """
    with patch('scripts.commit_message.subprocess.run') as mock_run, \
         patch('scripts.commit_message.logger') as mock_logger:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "Some tests failed."
        mock_run.return_value.stderr = "Error details."

        result = run_pytest()
        assert result is False
        mock_run.assert_called_once_with(['pytest'], capture_output=True, text=True)
        mock_logger.error.assert_any_call("Pytest failed with the following output:\n%s", "Some tests failed.")
        mock_logger.error.assert_any_call("Pytest stderr:\n%s", "Error details.")

def test_run_pytest_file_not_found():
    """
    Test run_pytest function when pytest is not installed.
    """
    with patch('scripts.commit_message.subprocess.run', side_effect=FileNotFoundError()), \
         patch('scripts.commit_message.logger') as mock_logger:
        result = run_pytest()
        assert result is False
        mock_logger.error.assert_called_with("Pytest is not installed or not found in the PATH.")

def test_run_pytest_unexpected_exception():
    """
    Test run_pytest function with an unexpected exception.
    """
    with patch('scripts.commit_message.subprocess.run', side_effect=Exception("Unexpected error")), \
         patch('scripts.commit_message.logger') as mock_logger:
        result = run_pytest()
        assert result is False
        mock_logger.error.assert_called_with("An unexpected error occurred while running pytest: %s", "Unexpected error")

# ----------------------------
# Test create_commit_message_file
# ----------------------------

def test_create_commit_message_file_success():
    """
    Test create_commit_message_file function with a successful write.
    """
    mock_file_utils = patch('scripts.commit_message.FileUtils.write_to_file').start()
    mock_logger = patch('scripts.commit_message.logger').start()

    create_commit_message_file("Test commit message", "/path/to/commit_message.txt")

    mock_file_utils.assert_called_once_with("/path/to/commit_message.txt", "Test commit message")
    mock_logger.info.assert_called_with("Commit message written to %s successfully.", "/path/to/commit_message.txt")

    patch.stopall()


# ----------------------------
# Test main function
# ----------------------------

@pytest.fixture
def mock_pipeline_utils():
    """
    Mock PipelineUtils module.
    """
    with patch('scripts.commit_message.PipelineUtils') as mock_pu:
        yield mock_pu

@pytest.fixture
def mock_file_utils():
    """
    Mock FileUtils module.
    """
    with patch('scripts.commit_message.FileUtils') as mock_fu:
        yield mock_fu

@pytest.fixture
def mock_chatbot():
    """
    Mock Chatbot instance.
    """
    with patch('scripts.commit_message.ChatbotUtils') as mock_cu, \
         patch('scripts.commit_message.PipelineUtils.create_chatbot') as mock_create_cb:
        mock_chatbot = MagicMock()
        mock_create_cb.return_value = mock_chatbot
        yield mock_chatbot

from textwrap import dedent

def test_main_success(
    mock_pipeline_utils,
    mock_file_utils,
    mock_chatbot
):
    """
    Test main function with successful execution.
    """
    with patch('scripts.commit_message.run_pytest', return_value=True), \
         patch('scripts.commit_message.split_diff_by_file', return_value=["diff1", "diff2"]), \
         patch('scripts.commit_message.logger') as mock_logger, \
         patch('scripts.commit_message.FileUtils.delete_file') as mock_delete_file:

        # Mock get_args
        mock_pipeline_utils.get_args.return_value = MagicMock()

        # Mock write_to_file for diff sections
        mock_file_utils.write_to_file.side_effect = lambda path, content: None

        # Mock chatbot.invoke to return "Commit message" twice
        mock_chatbot.invoke.side_effect = ["Commit message", "Commit message"]

        # Execute main
        main()

        # Assertions
        mock_pipeline_utils.get_args.assert_called_once()
        assert mock_chatbot.invoke.call_count == 2

        # Update expected_prompt to match the actual prompt used in the code
        expected_prompt = (
                "Write a detailed commit message based on the provided content. "
                "Format the commit message as JSON with the keys: "
                "'title', 'description' (list of sentences), and 'type' (e.g., feature, bugfix)."
            )

        expected_calls = [call(expected_prompt), call(expected_prompt)]
        mock_chatbot.invoke.assert_has_calls(expected_calls, any_order=False)

        mock_logger.info.assert_any_call("Commit message generated successfully.")


def test_main_pytest_failure():
    """
    Test main function when pytest fails
    """
    with patch('scripts.commit_message.run_pytest', return_value=False), \
         patch('scripts.commit_message.logger') as mock_logger, \
         patch('scripts.commit_message.PipelineUtils.get_args') as mock_get_args:

        # Mock the args returned by PipelineUtils.get_args()
        mock_args = Mock()
        mock_args.model = 'gpt-3.5-turbo'
        mock_args.type = 'txt'
        mock_args.system_prompt_template = ''
        mock_args.path = ''
        mock_args.collection_name = ''
        mock_get_args.return_value = mock_args

        with patch('scripts.commit_message.sys.exit') as mock_exit:
            # Simulate sys.exit(1) raising SystemExit
            mock_exit.side_effect = SystemExit(1)

            # Run main() and expect SystemExit
            try:
                main()
            except SystemExit:
                pass  # Expected exception due to sys.exit(1)

            mock_logger.error.assert_called_with("Tests failed. Aborting commit message generation.")
            mock_exit.assert_called_with(1)

