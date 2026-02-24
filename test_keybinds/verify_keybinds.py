#!/usr/bin/env python3
"""
Manual verification test for keybind system.
Run this to verify the keybind system is working correctly.
"""

from dv_tui.handlers import KeyHandler, KeybindManager, Mode
from dv_tui.config import load_config


def test_default_keybinds():
    """Test default keybinds work."""
    print("✓ Test 1: Default keybinds")
    kh = KeyHandler()
    assert kh.is_down_key(ord('j')), "j should be default down key"
    assert kh.is_up_key(ord('k')), "k should be default up key"
    assert kh.is_search_key(ord('/')), "/ should be default search key"
    assert kh.is_quit_key(ord('q')), "q should be default quit key"
    print("  All default keys work correctly")


def test_cli_bind():
    """Test CLI bind adds/overrides keybinds."""
    print("\n✓ Test 2: CLI bind")
    config = load_config(cli_config={'binds': [{'key': 'n', 'action': 'down', 'mode': 'normal'}]})
    kh = KeyHandler(config)
    assert kh.is_down_key(ord('n')), "n should be down key after bind"
    assert not kh.is_down_key(ord('j')), "j should not be down key after bind is replaced"
    print("  CLI bind 'n:down' works correctly")


def test_cli_unbind():
    """Test CLI unbind removes keys."""
    print("\n✓ Test 3: CLI unbind")
    from dv_tui.config import load_config
    from dv_tui.handlers import KeyHandler
    
    config = load_config(cli_config={'unbinds': [{'key': 'j', 'mode': 'normal'}]})
    print(f"  Config unbinds: {config.unbinds}")
    kh = KeyHandler(config)
    print(f"  KM unbinds: {kh.keybind_manager.unbinds}")
    print(f"  KM defaults['normal']['down']: {kh.keybind_manager.defaults['normal']['down']}")
    down_keybind = kh.keybind_manager.get_keybind('down')
    print(f"  Down keybind: {down_keybind}")
    j_result = kh.is_down_key(ord('j'))
    print(f"  Is j down? {j_result} (expected False)")
    if j_result:
        print(f"  DEBUG: Checking ord('j')={ord('j')} against {down_keybind}")
    assert not kh.is_down_key(ord('j')), "j should not be down key after unbind"
    assert kh.is_down_key(ord('J')), "J should still work"
    assert kh.is_down_key(258), "Arrow down should still work"
    print("  CLI unbind 'j' works correctly")


def test_multiple_binds():
    """Test multiple binds accumulate."""
    print("\n✓ Test 4: Multiple binds")
    config = load_config(cli_config={
        'binds': [
            {'key': 'n', 'action': 'down', 'mode': 'normal'},
            {'key': 'arrow_down', 'action': 'down', 'mode': 'normal'}
        ]
    })
    kh = KeyHandler(config)
    assert kh.is_down_key(ord('n')), "n should be down key"
    assert kh.is_down_key(258), "arrow_down should be down key"
    print("  Multiple binds accumulate correctly")


def test_mode_switching():
    """Test mode switching works."""
    print("\n✓ Test 5: Mode switching")
    kh = KeyHandler()
    assert kh.keybind_manager.get_mode() == Mode.NORMAL
    kh.keybind_manager.set_mode(Mode.SEARCH)
    assert kh.keybind_manager.get_mode() == Mode.SEARCH
    print("  Mode switching works correctly")


def test_named_keys():
    """Test named key parsing."""
    print("\n✓ Test 6: Named keys")
    config = load_config(cli_config={'binds': [
        {'key': 'arrow_up', 'action': 'up', 'mode': 'normal'},
        {'key': 'escape', 'action': 'quit', 'mode': 'normal'}
    ]})
    kh = KeyHandler(config)
    assert kh.is_up_key(259), "arrow_up should be up key"
    assert kh.is_quit_key(27), "escape should be quit key"
    print("  Named keys work correctly")


def test_precedence():
    """Test CLI > inline > file > defaults precedence."""
    print("\n✓ Test 7: Precedence")
    # Inline config sets search to 'f'
    config = load_config(
        inline_config={'keybinds': {'normal': {'search': ord('f')}}},
        cli_config={'binds': [{'key': 'x', 'action': 'search', 'mode': 'normal'}]}
    )
    kh = KeyHandler(config)
    assert kh.is_search_key(ord('x')), "CLI bind should override inline"
    assert not kh.is_search_key(ord('f')), "Inline should be overridden"
    assert not kh.is_search_key(ord('/')), "Default should be overridden"
    print("  CLI > inline > defaults precedence works")


def test_unbind_all():
    """Test unbinding all keys makes action unbound."""
    print("\n✓ Test 8: Unbind all keys")
    config = load_config(cli_config={'unbinds': [
        {'key': 'q', 'mode': 'normal'},
        {'key': 'Q', 'mode': 'normal'}
    ]})
    kh = KeyHandler(config)
    assert kh.keybind_manager.get_keybind('quit') is None, "Quit should be unbound"
    assert not kh.is_quit_key(ord('q')), "q should not be quit"
    assert not kh.is_quit_key(ord('Q')), "Q should not be quit"
    print("  Unbinding all keys works correctly")


def test_mode_specific_bind():
    """Test mode-specific bindings."""
    print("\n✓ Test 9: Mode-specific bindings")
    config = load_config(cli_config={'binds': [
        {'key': 'x', 'action': 'quit', 'mode': 'search'}
    ]})
    kh = KeyHandler(config)
    kh.keybind_manager.set_mode(Mode.NORMAL)
    assert not kh.is_quit_key(ord('x')), "x should not be quit in normal mode"
    kh.keybind_manager.set_mode(Mode.SEARCH)
    assert kh.is_quit_key(ord('x')), "x should be quit in search mode"
    print("  Mode-specific bindings work correctly")


def test_file_config():
    """Test config file loading."""
    print("\n✓ Test 10: Config file")
    import os
    os.chdir('test_keybinds')
    config = load_config(
        config_path='custom_config.json'
    )
    kh = KeyHandler(config)
    assert kh.is_down_key(ord('n')), "Config should set n to down"
    assert kh.is_search_key(ord('f')), "Config should set f to search"
    os.chdir('..')
    print("  Config file loading works correctly")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Keybind System Verification Tests")
    print("=" * 50)
    
    tests = [
        test_default_keybinds,
        test_cli_bind,
        test_cli_unbind,
        test_multiple_binds,
        test_mode_switching,
        test_named_keys,
        test_precedence,
        test_unbind_all,
        test_mode_specific_bind,
        test_file_config,
    ]
    
    failed = []
    for i, test in enumerate(tests, 1):
        print(f"\n--- Running test {i}: {test.__name__} ---")
        try:
            test()
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed.append(test.__name__)
        except Exception as e:
            import traceback
            print(f"  ✗ ERROR: {e}")
            traceback.print_exc()
            failed.append(test.__name__)
    
    print("\n" + "=" * 50)
    if failed:
        print(f"FAILED: {len(failed)} test(s)")
        for name in failed:
            print(f"  - {name}")
        return 1
    else:
        print("SUCCESS: All tests passed!")
        print("=" * 50)
        return 0


if __name__ == "__main__":
    exit(main())
