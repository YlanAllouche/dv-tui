import pytest
import tempfile
import json
from dv_tui.table import Table


class TestDynamicColumnDetection:
    """Test dynamic column detection from data."""
    
    def test_detect_columns_empty_data(self):
        """Test with empty data list."""
        table = Table([])
        assert table.columns == []
    
    def test_detect_columns_single_item(self):
        """Test with single item."""
        data = [{"a": 1, "b": 2, "c": 3}]
        table = Table(data)
        assert sorted(table.columns) == ["a", "b", "c"]
    
    def test_detect_columns_multiple_items_same_keys(self):
        """Test with multiple items having same keys."""
        data = [
            {"a": 1, "b": 2},
            {"a": 3, "b": 4},
        ]
        table = Table(data)
        assert sorted(table.columns) == ["a", "b"]
    
    def test_detect_columns_multiple_items_different_keys(self):
        """Test with multiple items having different keys."""
        data = [
            {"a": 1, "b": 2},
            {"c": 3, "d": 4},
        ]
        table = Table(data)
        assert sorted(table.columns) == ["a", "b", "c", "d"]
    
    def test_detect_columns_mixed_keys(self):
        """Test with mixed keys across items."""
        data = [
            {"a": 1, "b": 2},
            {"a": 3, "c": 4},
            {"b": 5, "d": 6},
        ]
        table = Table(data)
        assert sorted(table.columns) == ["a", "b", "c", "d"]


class TestColumnFiltering:
    """Test column filtering via config."""
    
    def test_filter_columns_subset(self):
        """Test filtering to show only specified columns."""
        data = [{"a": 1, "b": 2, "c": 3}]
        columns = ["a", "c"]
        table = Table(data, columns=columns)
        assert table.columns == ["a", "c"]
    
    def test_filter_columns_all(self):
        """Test requesting all columns."""
        data = [{"a": 1, "b": 2}]
        columns = ["a", "b"]
        table = Table(data, columns=columns)
        assert table.columns == ["a", "b"]
    
    def test_filter_columns_nonexistent(self):
        """Test filtering with non-existent columns falls back to detected."""
        data = [{"a": 1, "b": 2}]
        columns = ["x", "y"]
        table = Table(data, columns=columns)
        # Falls back to detected columns
        assert sorted(table.columns) == ["a", "b"]
    
    def test_filter_columns_mixed_existence(self):
        """Test filtering with some columns existing, some not."""
        data = [{"a": 1, "b": 2, "c": 3}]
        columns = ["a", "x", "c"]
        table = Table(data, columns=columns)
        # Only includes columns that exist
        assert sorted(table.columns) == ["a", "c"]


class TestColumnReordering:
    """Test column reordering via config."""
    
    def test_reorder_columns(self):
        """Test changing column order."""
        data = [{"a": 1, "b": 2, "c": 3}]
        columns = ["c", "a", "b"]
        table = Table(data, columns=columns)
        assert table.columns == ["c", "a", "b"]
    
    def test_reorder_and_filter(self):
        """Test reordering and filtering together."""
        data = [{"a": 1, "b": 2, "c": 3, "d": 4}]
        columns = ["d", "b", "a"]
        table = Table(data, columns=columns)
        assert table.columns == ["d", "b", "a"]


class TestDynamicColumnWidths:
    """Test dynamic column width calculation."""
    
    def test_calculate_widths_empty_table(self):
        """Test with empty table."""
        table = Table([])
        widths = table.calculate_column_widths([], 80)
        assert widths == []
    
    def test_calculate_widths_single_column(self):
        """Test with single column."""
        table = Table([{"name": "test"}])
        widths = table.calculate_column_widths(["Name"], 80)
        assert len(widths) == 1
        # Width should be at least minimum (8) and fit in available space
        assert widths[0] >= 8
        assert widths[0] <= 80
    
    def test_calculate_widths_fits_in_space(self):
        """Test when all columns fit in available width."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        table = Table(data)
        widths = table.calculate_column_widths(["Name", "Age"], 100)
        assert len(widths) == 2
        assert all(w >= 8 for w in widths)  # Minimum width is 8
        # Should fit easily
        assert sum(widths) + 1 <= 100
    
    def test_calculate_widths_needs_scaling(self):
        """Test when columns need to be scaled down."""
        data = [
            {"name": "Alice Smith", "description": "Very long description text"},
            {"name": "Bob Jones", "description": "Another very long description"},
        ]
        table = Table(data)
        widths = table.calculate_column_widths(["Name", "Description"], 30)
        assert len(widths) == 2
        assert sum(widths) + 1 <= 30  # Including spacing
        assert all(w >= 8 for w in widths)
    
    def test_calculate_widths_considers_content(self):
        """Test that widths consider content length."""
        data = [
            {"short": "x", "long": "Very long text here"},
            {"short": "y", "long": "Another long text"},
        ]
        table = Table(data)
        # Table columns are sorted: ["long", "short"]
        widths = table.calculate_column_widths(["Long", "Short"], 100)
        # Long column should get more width
        # widths[0] is for "long", widths[1] is for "short"
        assert widths[0] > widths[1]


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""
    
    def test_legacy_get_type_color_exists(self):
        """Test that get_type_color method exists."""
        table = Table([{"type": "work"}])
        assert hasattr(table, 'get_type_color')
    
    def test_legacy_get_status_color_exists(self):
        """Test that get_status_color method exists."""
        table = Table([{"status": "active"}])
        assert hasattr(table, 'get_status_color')
    
    def test_legacy_get_dynamic_color_exists(self):
        """Test that get_dynamic_color method exists."""
        table = Table([{"field": "value"}])
        assert hasattr(table, 'get_dynamic_color')
    
    def test_legacy_render_exists(self):
        """Test that render method exists."""
        table = Table([{"a": 1}])
        assert hasattr(table, 'render')
    
    def test_legacy_render_headers_exists(self):
        """Test that render_headers method exists."""
        table = Table([{"a": 1}])
        assert hasattr(table, 'render_headers')
    
    def test_legacy_scroll_methods_exist(self):
        """Test that scroll methods exist."""
        table = Table([{"a": 1}, {"b": 2}])
        assert hasattr(table, 'scroll_up')
        assert hasattr(table, 'scroll_down')
    
    def test_legacy_properties_exist(self):
        """Test that legacy properties exist."""
        table = Table([{"a": 1}])
        assert hasattr(table, 'row_count')
        assert hasattr(table, 'selected_item')
    
    def test_legacy_scroll_behavior(self):
        """Test that scroll methods work as before."""
        data = [{"a": i} for i in range(10)]
        table = Table(data)
        
        # Initially at index 0
        assert table.selected_index == 0
        
        # Scroll down
        table.scroll_down()
        assert table.selected_index == 1
        
        # Scroll up
        table.scroll_up()
        assert table.selected_index == 0
        
        # Can't go below 0
        table.scroll_up()
        assert table.selected_index == 0
        
        # Can't go beyond last item
        table.selected_index = 9
        table.scroll_down()
        assert table.selected_index == 9


class TestScrollOffsetManagement:
    """Test scroll offset management."""
    
    def test_scroll_offset_initial(self):
        """Test initial scroll offset is 0."""
        table = Table([{"a": i} for i in range(10)])
        assert table.scroll_offset == 0
    
    def test_scroll_offset_can_be_set(self):
        """Test scroll offset can be set."""
        table = Table([{"a": i} for i in range(10)])
        table.scroll_offset = 5
        assert table.scroll_offset == 5
    
    def test_render_uses_scroll_offset(self):
        """Test that render respects scroll offset (integration check)."""
        # This is a structural test - actual rendering tested in integration
        data = [{"a": i} for i in range(10)]
        table = Table(data)
        assert hasattr(table, 'render')
        assert table.scroll_offset == 0
