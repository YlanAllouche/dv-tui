#!/usr/bin/env python3
"""
Quick test script for dv-tui functionality.
Run this to verify basic functionality without curses TUI.
"""

import sys
sys.path.insert(0, '.')

from dv_tui import load_file, load_config, DEFAULT_CONFIG
from dv_tui.utils import fuzzy_match, fuzzy_filter

def test_data_loading():
    print("Testing data loading...")
    
    files = [
        'tests/data/work_tasks.json',
        'tests/data/study_tasks.json',
        'tests/data/mixed_tasks.csv',
    ]
    
    for file in files:
        try:
            data = load_file(file)
            print(f"  ✓ {file}: {len(data)} items")
        except Exception as e:
            print(f"  ✗ {file}: {e}")
            return False
    
    return True

def test_config():
    print("\nTesting configuration...")
    config = load_config()
    
    keybinds = config.keybinds
    
    tests = [
        ('quit', [113, 81], "q/Q"),
        ('down', [106, 74, 258], "j/J/↓"),
        ('up', [107, 75, 259], "k/K/↑"),
        ('left', [104, 72, 260], "h/H/←"),
        ('right', [108, 76, 261], "l/L/→"),
        ('search', 47, "/"),
    ]
    
    all_ok = True
    for key, expected, name in tests:
        actual = keybinds.get(key)
        if actual == expected:
            print(f"  ✓ {key} ({name}): {actual}")
        else:
            print(f"  ✗ {key} ({name}): expected {expected}, got {actual}")
            all_ok = False
    
    return all_ok

def test_fuzzy_match():
    print("\nTesting fuzzy matching...")
    
    tests = [
        ("py", "python", True),
        ("wrk", "work", True),
        ("tsk", "task", True),
        ("xyz", "python", False),
    ]
    
    all_ok = True
    for query, text, expected in tests:
        matched, score = fuzzy_match(query, text)
        if matched == expected:
            print(f"  ✓ '{query}' vs '{text}': matched={matched}, score={score}")
        else:
            print(f"  ✗ '{query}' vs '{text}': expected {expected}, got {matched}")
            all_ok = False
    
    return all_ok

def test_fuzzy_filter():
    print("\nTesting fuzzy filter...")
    
    data = [
        {"summary": "Python programming"},
        {"summary": "Work on tasks"},
        {"summary": "Study algorithms"},
    ]
    
    result = fuzzy_filter(data, "py", "summary")
    if len(result) == 1 and result[0]["summary"] == "Python programming":
        print(f"  ✓ Filter for 'py': {len(result)} result(s)")
        return True
    else:
        print(f"  ✗ Filter for 'py': expected 1 result, got {len(result)}")
        return False

def main():
    print("=" * 50)
    print("dv-tui Functionality Tests")
    print("=" * 50)
    
    results = [
        ("Data Loading", test_data_loading()),
        ("Configuration", test_config()),
        ("Fuzzy Match", test_fuzzy_match()),
        ("Fuzzy Filter", test_fuzzy_filter()),
    ]
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
