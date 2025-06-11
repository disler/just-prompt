"""
Tests for the CEO and Board prompt functionality.
"""

import pytest
import os
from unittest.mock import patch, mock_open, MagicMock, call
import tempfile
from pathlib import Path

from just_prompt.molecules.ceo_and_board_prompt import (
    ceo_and_board_prompt,
    DEFAULT_CEO_MODEL,
    DEFAULT_CEO_DECISION_PROMPT
)


@pytest.fixture
def mock_environment(monkeypatch):
    """Setup environment for tests."""
    monkeypatch.setenv("DEFAULT_MODELS", "a:claude-3,o:gpt-4o")
    monkeypatch.setenv("CORRECTION_MODEL", "a:claude-3")
    return monkeypatch


class TestCEOAndBoardPrompt:
    """Tests for ceo_and_board_prompt function."""

    @patch("just_prompt.molecules.ceo_and_board_prompt.prompt_from_file_to_file")
    @patch("just_prompt.molecules.ceo_and_board_prompt.prompt")
    @patch("builtins.open", new_callable=mock_open, read_data="Test prompt question")
    def test_ceo_and_board_prompt_success(self, mock_file, mock_prompt, mock_prompt_from_file_to_file, mock_environment, tmpdir):
        """Test successful CEO and board prompt execution."""
        # Set up mocks
        mock_prompt_from_file_to_file.return_value = [
            str(Path(tmpdir) / "test_a_claude-3.md"),
            str(Path(tmpdir) / "test_o_gpt-4o.md")
        ]
        mock_prompt.return_value = ["# CEO Decision\n\nThis is the CEO decision content."]
        
        # Create test files that would normally be created by prompt_from_file_to_file
        board_file1 = Path(tmpdir) / "test_a_claude-3.md"
        board_file1.write_text("Claude's response to the test prompt")
        
        board_file2 = Path(tmpdir) / "test_o_gpt-4o.md"
        board_file2.write_text("GPT-4o's response to the test prompt")
        
        # Test our function
        input_file = "test_prompt.txt"
        result = ceo_and_board_prompt(
            abs_from_file=input_file,
            abs_output_dir=str(tmpdir),
            models_prefixed_by_provider=["a:claude-3", "o:gpt-4o"]
        )
        
        # Assertions
        mock_prompt_from_file_to_file.assert_called_once_with(
            abs_file_path=input_file,
            models_prefixed_by_provider=["a:claude-3", "o:gpt-4o"],
            abs_output_dir=str(tmpdir)
        )
        
        # Check that the CEO model was called with the right prompt
        mock_prompt.assert_called_once()
        prompt_arg = mock_prompt.call_args[0][0]
        assert "<original-question>Test prompt question</original-question>" in prompt_arg
        assert "<model-name>a:claude-3</model-name>" in prompt_arg
        assert "<model-name>o:gpt-4o</model-name>" in prompt_arg
        
        # Check that the CEO decision file was created correctly
        expected_output_file = str(Path(tmpdir) / "ceo_decision.md")
        assert result == expected_output_file
        
        # Check that both the prompt XML and decision files were created
        # The actual call may be with Path object or string, so we check the call arguments
        assert mock_file.call_count >= 2  # Should be called at least twice - once for prompt XML and once for decision
        
        # Check that one call was for the CEO prompt XML file
        expected_prompt_file = str(Path(tmpdir) / "ceo_prompt.xml")
        prompt_file_call_found = False
        
        for call_args in mock_file.call_args_list:
            args, kwargs = call_args
            if str(args[0]) == expected_prompt_file and args[1] == "w" and kwargs.get("encoding") == "utf-8":
                prompt_file_call_found = True
                break
        assert prompt_file_call_found, "No call to create CEO prompt XML file found"
        
        # Check that one call was for the CEO decision file
        decision_file_call_found = False
        for call_args in mock_file.call_args_list:
            args, kwargs = call_args
            if str(args[0]) == expected_output_file and args[1] == "w" and kwargs.get("encoding") == "utf-8":
                decision_file_call_found = True
                break
        assert decision_file_call_found, "No call to create CEO decision file found"

    @patch("just_prompt.molecules.ceo_and_board_prompt.prompt_from_file_to_file")
    @patch("just_prompt.molecules.ceo_and_board_prompt.prompt")
    @patch("builtins.open", new_callable=mock_open, read_data="Test prompt question")
    def test_ceo_and_board_prompt_with_defaults(self, mock_file, mock_prompt, mock_prompt_from_file_to_file, mock_environment, tmpdir):
        """Test CEO and board prompt with default parameters."""
        # Set up mocks
        mock_prompt_from_file_to_file.return_value = [
            str(Path(tmpdir) / "test_a_claude-3.md"),
            str(Path(tmpdir) / "test_o_gpt-4o.md")
        ]
        mock_prompt.return_value = ["# CEO Decision\n\nThis is the CEO decision content."]
        
        # Create test files
        board_file1 = Path(tmpdir) / "test_a_claude-3.md"
        board_file1.write_text("Claude's response to the test prompt")
        
        board_file2 = Path(tmpdir) / "test_o_gpt-4o.md"
        board_file2.write_text("GPT-4o's response to the test prompt")
        
        # Test with defaults
        input_file = "test_prompt.txt"
        result = ceo_and_board_prompt(
            abs_from_file=input_file,
            abs_output_dir=str(tmpdir)
        )
        
        # Assertions
        mock_prompt_from_file_to_file.assert_called_once_with(
            abs_file_path=input_file,
            models_prefixed_by_provider=None,
            abs_output_dir=str(tmpdir)
        )
        
        # Check that the default CEO model was used
        mock_prompt.assert_called_once()
        assert mock_prompt.call_args[0][1] == [DEFAULT_CEO_MODEL]
        
        # Check that the CEO decision file was created correctly
        expected_output_file = str(Path(tmpdir) / "ceo_decision.md")
        assert result == expected_output_file
        
        # Verify that both prompt XML and decision files were created
        assert mock_file.call_count >= 2  # Once for prompt XML and once for decision

    @patch("just_prompt.molecules.ceo_and_board_prompt.prompt_from_file_to_file")
    @patch("just_prompt.molecules.ceo_and_board_prompt.prompt")
    def test_ceo_and_board_prompt_file_not_found(self, mock_prompt, mock_prompt_from_file_to_file, mock_environment):
        """Test error handling when input file is not found."""
        non_existent_file = "non_existent_file.txt"
        
        # Mock file not found error
        mock_open_instance = mock_open()
        mock_open_instance.side_effect = FileNotFoundError(f"File not found: {non_existent_file}")
        
        with patch("builtins.open", mock_open_instance):
            with pytest.raises(ValueError, match=f"Error reading file"):
                ceo_and_board_prompt(abs_from_file=non_existent_file)