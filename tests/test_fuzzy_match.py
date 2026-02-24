import pytest
from dv_tui.utils import fuzzy_match, fuzzy_filter


def test_fuzzy_match_exact():
    matched, score = fuzzy_match("test", "test")
    assert matched is True
    assert score == 0.0


def test_fuzzy_match_case_insensitive():
    matched, score = fuzzy_match("TEST", "test")
    assert matched is True
    assert score == 0.0


def test_fuzzy_match_substring():
    matched, score = fuzzy_match("tst", "test")
    assert matched is True
    assert score > 0


def test_fuzzy_match_prefix():
    matched, score = fuzzy_match("te", "test")
    assert matched is True
    assert score == 0.0


def test_fuzzy_match_suffix():
    matched, score = fuzzy_match("st", "test")
    assert matched is True
    assert score == 2.0


def test_fuzzy_match_no_match():
    matched, score = fuzzy_match("xyz", "test")
    assert matched is False
    assert score == float('inf')


def test_fuzzy_match_empty_query():
    matched, score = fuzzy_match("", "test")
    assert matched is True
    assert score == 0.0


def test_fuzzy_match_empty_text():
    matched, score = fuzzy_match("test", "")
    assert matched is False
    assert score == float('inf')


def test_fuzzy_match_repeated_chars():
    matched, score = fuzzy_match("tt", "test")
    assert matched is True
    assert score > 0


def test_fuzzy_match_complex():
    matched, score = fuzzy_match("tst", "testing")
    assert matched is True
    assert score == 1.0


def test_fuzzy_match_score_ordering():
    _, score1 = fuzzy_match("ab", "ab")
    _, score2 = fuzzy_match("a b", "a b")
    _, score3 = fuzzy_match("a", "ab")
    
    assert score1 == 0.0
    assert score2 == 0.0
    assert score3 == 0.0
    assert score1 <= score2


def test_fuzzy_filter_empty_query():
    items = [
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"}
    ]
    
    result = fuzzy_filter(items, "")
    assert len(result) == 3
    assert result == items


def test_fuzzy_filter_with_matches():
    items = [
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"}
    ]
    
    result = fuzzy_filter(items, "a", search_field="name")
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Charlie"


def test_fuzzy_filter_sorted_by_score():
    items = [
        {"name": "Test One"},
        {"name": "test two"},
        {"name": "testing three"}
    ]
    
    result = fuzzy_filter(items, "test", search_field="name")
    assert len(result) == 3
    assert result[0]["name"] == "Test One"
    assert result[1]["name"] == "test two"
    assert result[2]["name"] == "testing three"


def test_fuzzy_filter_custom_field():
    items = [
        {"summary": "Fix bug"},
        {"summary": "Add feature"},
        {"summary": "Refactor code"}
    ]
    
    result = fuzzy_filter(items, "bug", search_field="summary")
    assert len(result) == 1
    assert result[0]["summary"] == "Fix bug"


def test_fuzzy_filter_no_matches():
    items = [
        {"name": "Alice"},
        {"name": "Bob"}
    ]
    
    result = fuzzy_filter(items, "xyz")
    assert len(result) == 0


def test_fuzzy_filter_missing_field():
    items = [
        {"summary": "Alice task"},
        {"summary": "Bob task"},
        {"status": "active"}
    ]
    
    result = fuzzy_filter(items, "a")
    assert len(result) == 2


def test_fuzzy_filter_preserves_all_data():
    items = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    
    result = fuzzy_filter(items, "al", search_field="name")
    assert len(result) == 1
    assert result[0]["name"] == "Alice"
    assert result[0]["age"] == 30


def test_fuzzy_match_unicode():
    matched, score = fuzzy_match("tëst", "tëst")
    assert matched is True
    assert score == 0.0


def test_fuzzy_match_numbers():
    matched, score = fuzzy_match("123", "test123")
    assert matched is True
    assert score == 4.0


def test_fuzzy_filter_numbers():
    items = [
        {"id": "test123"},
        {"id": "test456"},
        {"id": "test789"}
    ]
    
    result = fuzzy_filter(items, "123", search_field="id")
    assert len(result) == 1
    assert result[0]["id"] == "test123"
