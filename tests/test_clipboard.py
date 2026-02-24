import pytest
from unittest.mock import Mock, patch, MagicMock
from dv_tui.actions import Clipboard


def test_clipboard_detect_tool_found():
    clipboard = Clipboard()
    assert clipboard._available_tool is not None or clipboard.get_tool_name() == "none"


def test_clipboard_get_tool_name():
    clipboard = Clipboard()
    tool_name = clipboard.get_tool_name()
    assert tool_name in ["xclip", "wl-copy", "pbcopy", "none"]


def test_clipboard_copy_with_xclip():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="/usr/bin/xclip")
        
        clipboard = Clipboard()
        
        with patch.object(clipboard, 'copy') as mock_copy:
            mock_copy.return_value = True
            result = clipboard.copy("test text")
            
            assert result is True


def test_clipboard_copy_with_wl_copy():
    clipboard = Clipboard()
    clipboard._available_tool = "wl-copy"
    
    with patch('subprocess.run') as mock_run:
        result = clipboard.copy("test text")
        
        assert result is True
        mock_run.assert_called_once_with(
            ["wl-copy"],
            input=b"test text",
            check=True
        )


def test_clipboard_copy_with_xclip_selection():
    clipboard = Clipboard()
    clipboard._available_tool = "xclip"
    
    with patch('subprocess.run') as mock_run:
        result = clipboard.copy("test text")
        
        assert result is True
        mock_run.assert_called_once_with(
            ["xclip", "-selection", "clipboard"],
            input=b"test text",
            check=True
        )


def test_clipboard_copy_with_pbcopy():
    clipboard = Clipboard()
    clipboard._available_tool = "pbcopy"
    
    with patch('subprocess.run') as mock_run:
        result = clipboard.copy("test text")
        
        assert result is True
        mock_run.assert_called_once_with(
            ["pbcopy"],
            input=b"test text",
            check=True
        )


def test_clipboard_copy_no_tool():
    clipboard = Clipboard()
    clipboard._available_tool = None
    
    result = clipboard.copy("test text")
    
    assert result is False


def test_clipboard_copy_unicode():
    clipboard = Clipboard()
    clipboard._available_tool = "xclip"
    
    with patch('subprocess.run') as mock_run:
        result = clipboard.copy("Hello 世界")
        
        assert result is True
        mock_run.assert_called_once()


def test_clipboard_copy_empty_string():
    clipboard = Clipboard()
    clipboard._available_tool = "xclip"
    
    with patch('subprocess.run') as mock_run:
        result = clipboard.copy("")
        
        assert result is True


def test_clipboard_copy_error_handling():
    clipboard = Clipboard()
    clipboard._available_tool = "xclip"
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("copy failed")
        
        result = clipboard.copy("test text")
        
        assert result is False


def test_clipboard_copy_multiline():
    clipboard = Clipboard()
    clipboard._available_tool = "xclip"
    
    with patch('subprocess.run') as mock_run:
        text = "line1\nline2\nline3"
        result = clipboard.copy(text)
        
        assert result is True
        mock_run.assert_called_once()


def test_clipboard_get_tool_name_none():
    clipboard = Clipboard()
    clipboard._available_tool = None
    
    result = clipboard.get_tool_name()
    
    assert result == "none"


def test_clipboard_get_tool_name_xclip():
    clipboard = Clipboard()
    clipboard._available_tool = "xclip"
    
    result = clipboard.get_tool_name()
    
    assert result == "xclip"
