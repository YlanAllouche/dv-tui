import pytest
import json
import tempfile
import os
from pathlib import Path

from dv_tui.data_loaders import (
    DataLoader,
    JsonDataLoader,
    CsvDataLoader,
    StdinDataLoader,
    load_file,
    create_loader,
    detect_source,
    union_keys,
    fill_missing_keys,
)


class TestUnionKeys:
    """Test union_keys function."""
    
    def test_empty_list(self):
        assert union_keys([]) == []
    
    def test_single_item(self):
        data = [{"a": 1, "b": 2}]
        assert union_keys(data) == ["a", "b"]
    
    def test_multiple_items_same_keys(self):
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        assert union_keys(data) == ["a", "b"]
    
    def test_multiple_items_different_keys(self):
        data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        result = union_keys(data)
        assert sorted(result) == ["a", "b", "c", "d"]
    
    def test_union_mixed_keys(self):
        data = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
        assert sorted(union_keys(data)) == ["a", "b", "c"]


class TestFillMissingKeys:
    """Test fill_missing_keys function."""
    
    def test_empty_list(self):
        assert fill_missing_keys([]) == []
    
    def test_complete_data(self):
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = fill_missing_keys(data)
        assert len(result) == 2
        assert all(set(item.keys()) == {"a", "b"} for item in result)
    
    def test_missing_keys_filled(self):
        data = [{"a": 1}, {"b": 2}]
        result = fill_missing_keys(data)
        assert result == [{"a": 1, "b": ""}, {"a": "", "b": 2}]
    
    def test_preserves_existing_values(self):
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = fill_missing_keys(data)
        assert result == data


class TestJsonDataLoader:
    """Test JsonDataLoader."""
    
    def test_load_valid_json_file(self, tmp_path):
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        loader = JsonDataLoader(str(file_path))
        result = loader.load()
        assert result == data
    
    def test_load_json_file_with_missing_keys(self, tmp_path):
        data = [{"a": 1}, {"a": 2, "b": 3}]
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        loader = JsonDataLoader(str(file_path))
        result = loader.load()
        assert len(result) == 2
        assert result == [{"a": 1, "b": ""}, {"a": 2, "b": 3}]
    
    def test_load_inline_json(self):
        json_str = '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'
        loader = JsonDataLoader(json_str)
        result = loader.load()
        assert result == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    
    def test_load_inline_json_missing_keys(self):
        json_str = '[{"a": 1}, {"a": 2, "b": 3}]'
        loader = JsonDataLoader(json_str)
        result = loader.load()
        assert result == [{"a": 1, "b": ""}, {"a": 2, "b": 3}]
    
    def test_load_inline_json_object(self):
        json_str = '{"a": 1, "b": 2}'
        loader = JsonDataLoader(json_str)
        with pytest.raises(Exception, match="JSON must be a list of objects"):
            loader.load()
    
    def test_load_invalid_json_file(self, tmp_path):
        file_path = tmp_path / "invalid.json"
        with open(file_path, 'w') as f:
            f.write('{"invalid": json}')
        
        loader = JsonDataLoader(str(file_path))
        with pytest.raises(Exception, match="Invalid JSON"):
            loader.load()
    
    def test_load_inline_invalid_json(self):
        loader = JsonDataLoader('[{invalid}]')
        with pytest.raises(Exception, match="Invalid JSON"):
            loader.load()
    
    def test_file_not_found(self):
        loader = JsonDataLoader("/nonexistent/nonexistent_file_xyz123.json")
        with pytest.raises(Exception, match="Invalid JSON"):
            loader.load()
    
    def test_get_source_info_file(self, tmp_path):
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump([], f)
        
        loader = JsonDataLoader(str(file_path))
        assert "JSON file:" in loader.get_source_info()
    
    def test_get_source_info_inline(self):
        loader = JsonDataLoader('[{"a": 1}]')
        assert "Inline JSON" in loader.get_source_info()
    
    def test_can_refresh_file(self, tmp_path):
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump([], f)
        
        loader = JsonDataLoader(str(file_path))
        assert loader.can_refresh() is True
    
    def test_cannot_refresh_inline(self):
        loader = JsonDataLoader('[{"a": 1}]')
        assert loader.can_refresh() is False
    
    def test_refresh_file(self, tmp_path):
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump([{"a": 1}, {"a": 2, "b": 3}], f)
        
        loader = JsonDataLoader(str(file_path))
        result = loader.load()
        assert result == [{"a": 1, "b": ""}, {"a": 2, "b": 3}]
        
        with open(file_path, 'w') as f:
            json.dump([{"a": 3, "b": 4}], f)
        
        refreshed = loader.refresh()
        assert refreshed == [{"a": 3, "b": 4}]
    
    def test_refresh_inline_raises(self):
        loader = JsonDataLoader('[{"a": 1}]')
        with pytest.raises(NotImplementedError, match="Cannot refresh inline JSON"):
            loader.refresh()


class TestCsvDataLoader:
    """Test CsvDataLoader."""
    
    def test_load_valid_csv_file(self, tmp_path):
        file_path = tmp_path / "test.csv"
        with open(file_path, 'w') as f:
            f.write("a,b\n1,2\n3,4\n")
        
        loader = CsvDataLoader(str(file_path))
        result = loader.load()
        assert len(result) == 2
        assert result[0] == {"a": "1", "b": "2"}
        assert result[1] == {"a": "3", "b": "4"}
    
    def test_load_csv_with_custom_delimiter(self, tmp_path):
        file_path = tmp_path / "test.csv"
        with open(file_path, 'w') as f:
            f.write("a;b\n1;2\n3;4\n")
        
        loader = CsvDataLoader(str(file_path), delimiter=';')
        result = loader.load()
        assert len(result) == 2
        assert result[0] == {"a": "1", "b": "2"}
        assert result[1] == {"a": "3", "b": "4"}
    
    def test_load_csv_with_missing_values(self, tmp_path):
        file_path = tmp_path / "test.csv"
        with open(file_path, 'w') as f:
            f.write("a,b,c\n1,2\n3,4,5\n")
        
        loader = CsvDataLoader(str(file_path))
        result = loader.load()
        assert len(result) == 2
        assert result[0] == {"a": "1", "b": "2", "c": ""}
        assert result[1] == {"a": "3", "b": "4", "c": "5"}
    
    def test_file_not_found(self):
        loader = CsvDataLoader("/nonexistent/file.csv")
        with pytest.raises(Exception, match="not found"):
            loader.load()
    
    def test_get_source_info(self, tmp_path):
        file_path = tmp_path / "test.csv"
        with open(file_path, 'w') as f:
            f.write("a,b\n")
        
        loader = CsvDataLoader(str(file_path), delimiter=';')
        info = loader.get_source_info()
        assert "CSV file:" in info
        assert ";" in info


class TestStdinDataLoader:
    """Test StdinDataLoader."""
    
    def test_load_valid_json_stdin(self):
        """Test loading valid JSON from stdin using subprocess."""
        import sys
        import subprocess
        import json
        
        test_script = """
import sys
import json
from dv_tui.data_loaders import StdinDataLoader

loader = StdinDataLoader(timeout=None)
result = loader.load()
print(json.dumps(result))
"""
        stdin_data = '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'
        
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        assert result.returncode == 0
        loaded_data = json.loads(result.stdout)
        assert loaded_data == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    
    def test_load_stdin_missing_keys(self):
        """Test loading JSON with missing keys from stdin using subprocess."""
        import sys
        import subprocess
        import json
        
        test_script = """
import sys
import json
from dv_tui.data_loaders import StdinDataLoader

loader = StdinDataLoader(timeout=None)
result = loader.load()
print(json.dumps(result))
"""
        stdin_data = '[{"a": 1}, {"a": 2, "b": 3}]'
        
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        assert result.returncode == 0
        loaded_data = json.loads(result.stdout)
        assert loaded_data == [{"a": 1, "b": ""}, {"a": 2, "b": 3}]
    
    def test_load_invalid_json_stdin(self):
        """Test loading invalid JSON from stdin using subprocess."""
        import sys
        import subprocess
        
        test_script = """
import sys
from dv_tui.data_loaders import StdinDataLoader

loader = StdinDataLoader(timeout=None)
try:
    loader.load()
    sys.exit(1)
except Exception as e:
    print(str(e))
    sys.exit(0)
"""
        stdin_data = '{"invalid": json}'
        
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        assert result.returncode == 0
        assert "Invalid JSON from stdin" in result.stdout
    
    def test_wait_for_stdin_data_no_timeout(self, monkeypatch):
        import sys
        from unittest.mock import patch
        
        with patch('dv_tui.data_loaders.select.select', return_value=([sys.stdin], [], [])):
            loader = StdinDataLoader(timeout=None)
            assert loader._wait_for_stdin_data(None) is True
    
    def test_wait_for_stdin_data_timeout(self, monkeypatch):
        import sys
        from unittest.mock import patch
        
        with patch('dv_tui.data_loaders.select.select', return_value=([], [], [])):
            loader = StdinDataLoader(timeout=1.0)
            assert loader._wait_for_stdin_data(1.0) is False
    
    def test_get_source_info(self):
        loader = StdinDataLoader(timeout=30)
        assert "Stdin" in loader.get_source_info()
        assert "30s" in loader.get_source_info()
        
        loader = StdinDataLoader(timeout=0)
        info = loader.get_source_info()
        assert "no timeout" in info


class TestLoadFile:
    """Test load_file function."""
    
    def test_load_json_file(self, tmp_path):
        data = [{"a": 1, "b": 2}]
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        result = load_file(str(file_path))
        assert result == data
    
    def test_load_csv_file(self, tmp_path):
        file_path = tmp_path / "test.csv"
        with open(file_path, 'w') as f:
            f.write("a,b\n1,2\n")
        
        result = load_file(str(file_path))
        assert result == [{"a": "1", "b": "2"}]
    
    def test_unsupported_format(self, tmp_path):
        file_path = tmp_path / "test.txt"
        with open(file_path, 'w') as f:
            f.write("test")
        
        with pytest.raises(Exception, match="Unsupported file format"):
            load_file(str(file_path))

    def test_load_file_descriptor_path(self):
        """Test that load_file handles file descriptor paths correctly."""
        import os
        import sys

        # Create a pipe to simulate process substitution
        r, w = os.pipe()
        pid = os.fork()

        if pid == 0:
            # Child process: write JSON to pipe
            os.close(r)
            data = [{"a": 1, "b": 2}]
            os.write(w, json.dumps(data).encode())
            os.close(w)
            os._exit(0)
        else:
            # Parent process: read from file descriptor
            os.close(w)
            try:
                fd_path = f'/dev/fd/{r}'
                # This should work without raising "Unsupported file format"
                result = load_file(fd_path)
                assert result == [{"a": 1, "b": 2}]
            finally:
                os.close(r)
                os.waitpid(pid, 0)


class TestCreateLoader:
    """Test create_loader function."""
    
    def test_create_json_file_loader(self, tmp_path):
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump([], f)
        
        loader = create_loader(str(file_path))
        assert isinstance(loader, JsonDataLoader)
        assert loader._is_file is True
    
    def test_create_csv_file_loader(self, tmp_path):
        file_path = tmp_path / "test.csv"
        with open(file_path, 'w') as f:
            f.write("a,b\n")
        
        loader = create_loader(str(file_path))
        assert isinstance(loader, CsvDataLoader)
    
    def test_create_inline_json_loader(self):
        loader = create_loader('[{"a": 1}]')
        assert isinstance(loader, JsonDataLoader)
        assert loader._is_file is False
    
    def test_create_inline_object_loader(self):
        loader = create_loader('{"a": 1}')
        assert isinstance(loader, JsonDataLoader)
        assert loader._is_file is False
    
    def test_create_stdin_loader(self):
        loader = create_loader('stdin', stdin_timeout=30)
        assert isinstance(loader, StdinDataLoader)
    
    def test_unsupported_source(self):
        with pytest.raises(Exception, match="Cannot load from source"):
            create_loader("nonexistent_file.xyz")
    
    def test_csv_delimiter_passed(self, tmp_path):
        file_path = tmp_path / "test.csv"
        with open(file_path, 'w') as f:
            f.write("a;b\n")

        loader = create_loader(str(file_path), delimiter=';')
        assert isinstance(loader, CsvDataLoader)
        assert loader.delimiter == ';'

    def test_create_file_descriptor_loader(self):
        """Test that file descriptor paths (e.g., /dev/fd/63) are recognized as JSON files."""
        loader = create_loader('/dev/fd/63')
        assert isinstance(loader, JsonDataLoader)
        assert loader._is_file is True

    def test_create_proc_self_fd_loader(self):
        """Test that /proc/self/fd/ paths are recognized as JSON files."""
        loader = create_loader('/proc/self/fd/11')
        assert isinstance(loader, JsonDataLoader)
        assert loader._is_file is True

    def test_create_proc_pid_fd_loader(self):
        """Test that /proc/<pid>/fd/ paths are recognized as JSON files."""
        loader = create_loader('/proc/12345/fd/11')
        assert isinstance(loader, JsonDataLoader)
        assert loader._is_file is True

    def test_file_descriptor_loading(self):
        """Test loading JSON from a file descriptor path."""
        import os
        import sys

        # Create a pipe to simulate process substitution
        r, w = os.pipe()
        pid = os.fork()

        if pid == 0:
            # Child process: write JSON to pipe
            os.close(r)
            data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
            os.write(w, json.dumps(data).encode())
            os.close(w)
            os._exit(0)
        else:
            # Parent process: read from file descriptor
            os.close(w)
            try:
                fd_path = f'/dev/fd/{r}'
                loader = create_loader(fd_path)
                assert isinstance(loader, JsonDataLoader)
                assert loader._is_file is True

                # Load the data
                result = loader.load()
                assert result == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
            finally:
                os.close(r)
                os.waitpid(pid, 0)


class TestDetectSource:
    """Test detect_source function."""
    
    def test_detect_inline_json_array(self):
        assert detect_source(['[{"a": 1}]']) == 'inline'
    
    def test_detect_inline_json_object(self):
        assert detect_source(['{"a": 1}']) == 'inline'
    
    def test_detect_file(self, monkeypatch, tmp_path):
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump([], f)
        
        assert detect_source([str(file_path)]) == 'file'
    
    def test_detect_no_files_with_stdin(self):
        """Test detect_source when stdin has data using subprocess."""
        import sys
        import subprocess
        
        test_script = """
import sys
from dv_tui.data_loaders import detect_source

result = detect_source([])
print(result)
"""
        stdin_data = '[{"a": 1}]'
        
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        assert result.returncode == 0
        assert 'stdin' in result.stdout
    
    def test_detect_no_files_no_stdin(self):
        """Test detect_source when stdin has no data using subprocess."""
        import sys
        import subprocess
        
        test_script = """
import sys
import os
from dv_tui.data_loaders import detect_source

# Close stdin to simulate no input
sys.stdin.close()
result = detect_source([])
print(result)
"""
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        assert result.returncode == 0
        assert 'file' in result.stdout


class TestIntegration:
    """Integration tests using existing test data."""
    
    def test_load_existing_json_file(self):
        data_path = Path(__file__).parent / "data" / "work_tasks.json"
        if data_path.exists():
            loader = JsonDataLoader(str(data_path))
            result = loader.load()
            assert len(result) > 0
            assert all(isinstance(item, dict) for item in result)
    
    def test_load_existing_csv_file(self):
        data_path = Path(__file__).parent / "data" / "mixed_tasks.csv"
        if data_path.exists():
            loader = CsvDataLoader(str(data_path))
            result = loader.load()
            assert len(result) > 0
            assert all(isinstance(item, dict) for item in result)


class TestProcessSubstitutionIntegration:
    """Test integration with bash process substitution <(...)"""
    
    def test_process_substitution_single_read(self):
        """Test that file descriptor paths are only read once (they can't be reread)."""
        import os
        import sys
        
        # Create a pipe to simulate process substitution
        r, w = os.pipe()
        pid = os.fork()
        
        if pid == 0:
            # Child process: write JSON to pipe
            os.close(r)
            data = [{"test": "value"}]
            os.write(w, json.dumps(data).encode())
            os.close(w)
            os._exit(0)
        else:
            # Parent process: read from file descriptor
            os.close(w)
            try:
                fd_path = f'/proc/self/fd/{r}'
                
                # First read should work
                data1 = load_file(fd_path)
                assert data1 == [{"test": "value"}]
                
                # Second read should fail (pipe is empty)
                # This tests that our CLI doesn't try to read FD paths twice
                with pytest.raises(Exception):
                    load_file(fd_path)
            finally:
                os.close(r)
                os.waitpid(pid, 0)
