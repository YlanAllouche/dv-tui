import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Any


class MockCurses:
    """Mock curses module for testing TUI components."""
    
    def __init__(self):
        self.initscr_called = False
        self.endwin_called = False
        self.current_color_pairs = {}
        self.color_pair_count = 0
        
        # Mock constants
        self.COLOR_BLACK = 0
        self.COLOR_RED = 1
        self.COLOR_GREEN = 2
        self.COLOR_YELLOW = 3
        self.COLOR_BLUE = 4
        self.COLOR_MAGENTA = 5
        self.COLOR_CYAN = 6
        self.COLOR_WHITE = 7
        
        self.A_NORMAL = 0
        self.A_BOLD = 1
        self.A_REVERSE = 2
        self.A_UNDERLINE = 4
        self.A_BLINK = 65536
        
        self.KEY_DOWN = 258
        self.KEY_UP = 259
        self.KEY_LEFT = 260
        self.KEY_RIGHT = 261
        self.KEY_ENTER = 10
        self.KEY_BACKSPACE = 263
        self.KEY_DC = 330
        self.KEY_HOME = 262
        self.KEY_END = 365
        self.KEY_NPAGE = 338
        self.KEY_PPAGE = 339
        self.KEY_RESIZE = 410
        
    def initscr(self):
        self.initscr_called = True
        return MockWindow(self)
    
    def endwin(self):
        self.endwin_called = True
    
    def use_default_colors(self):
        pass
    
    def init_pair(self, pair_number, fg, bg):
        self.current_color_pairs[pair_number] = (fg, bg)
        return 0
    
    def curs_set(self, visibility):
        pass
    
    def noecho(self):
        pass
    
    def cbreak(self):
        pass
    
    def keypad(self, stdscr, enable):
        pass
    
    def mousemask(self, mask):
        return 0
    
    def doupdate(self):
        pass
    
    def resize_term(self, lines, cols):
        pass
    
    def color_pair(self, n):
        return n * 256
    
    def error(self):
        pass


class MockWindow:
    """Mock curses window."""
    
    def __init__(self, curses_mock):
        self.curses = curses_mock
        self.y = 0
        self.x = 0
        self.max_y = 24
        self.max_x = 80
        self.contents = {}
        self.changes = []
        self.refreshes = 0
        
    def addstr(self, y, x, text, attr=0):
        self.changes.append(('addstr', y, x, text, attr))
        self.contents[(y, x)] = (text, attr)
    
    def addnstr(self, y, x, text, n, attr=0):
        self.addstr(y, x, text[:n], attr)
    
    def move(self, y, x):
        self.y = y
        self.x = x
    
    def getyx(self):
        return (self.y, self.x)
    
    def getmaxyx(self):
        return (self.max_y, self.max_x)
    
    def clear(self):
        self.contents = {}
        self.changes.append(('clear',))
    
    def clrtoeol(self):
        for col in range(self.x, self.max_x):
            self.contents[(self.y, col)] = (' ', 0)
    
    def clrtobot(self):
        for row in range(self.y, self.max_y):
            for col in range(self.max_x):
                self.contents[(row, col)] = (' ', 0)
    
    def refresh(self):
        self.refreshes += 1
        self.changes.append(('refresh',))
    
    def box(self, vert=0, hor=0):
        pass
    
    def hline(self, y, x, ch, n):
        for i in range(n):
            self.contents[(y, x + i)] = (ch, 0)
    
    def vline(self, y, x, ch, n):
        for i in range(n):
            self.contents[(y + i, x)] = (ch, 0)
    
    def nodelay(self, enable):
        pass
    
    def timeout(self, delay):
        pass
    
    def getch(self):
        return -1
    
    def erase(self):
        self.contents = {}
        self.changes.append(('erase',))
    
    def bkgd(self, ch, attr=0):
        pass
    
    def enclose(self, y, x):
        return 0 <= y < self.max_y and 0 <= x < self.max_x


@pytest.fixture
def mock_curses():
    """Provide a mock curses module."""
    curses_mock = MockCurses()
    with patch('curses.wrapper', side_effect=lambda func, *args: func(MockWindow(curses_mock), *args)):
        with patch('curses.initscr', return_value=MockWindow(curses_mock)):
            with patch('curses.endwin'):
                with patch('curses.color_pair', side_effect=curses_mock.color_pair):
                    with patch('curses.init_pair', side_effect=curses_mock.init_pair):
                        with patch('curses.use_default_colors'):
                            yield curses_mock


@pytest.fixture
def mock_window(mock_curses):
    """Provide a mock curses window."""
    return MockWindow(mock_curses)


def test_mock_curses_initialization(mock_curses):
    assert mock_curses.initscr_called is False
    assert mock_curses.endwin_called is False


def test_mock_window_creation(mock_window):
    assert mock_window.max_y == 24
    assert mock_window.max_x == 80
    assert len(mock_window.contents) == 0


def test_mock_window_addstr(mock_window):
    mock_window.addstr(5, 10, "Hello", 1)
    
    assert (5, 10) in mock_window.contents
    assert mock_window.contents[(5, 10)] == ("Hello", 1)
    assert len(mock_window.changes) == 1


def test_mock_window_addnstr(mock_window):
    mock_window.addnstr(5, 10, "Hello World", 5)
    
    assert (5, 10) in mock_window.contents
    assert mock_window.contents[(5, 10)] == ("Hello", 0)


def test_mock_window_move(mock_window):
    mock_window.move(10, 20)
    
    assert mock_window.y == 10
    assert mock_window.x == 20


def test_mock_window_getyx(mock_window):
    mock_window.y = 15
    mock_window.x = 25
    
    y, x = mock_window.getyx()
    
    assert y == 15
    assert x == 25


def test_mock_window_getmaxyx(mock_window):
    mock_window.max_y = 40
    mock_window.max_x = 120
    
    y, x = mock_window.getmaxyx()
    
    assert y == 40
    assert x == 120


def test_mock_window_clear(mock_window):
    mock_window.addstr(1, 1, "test")
    mock_window.clear()
    
    assert len(mock_window.contents) == 0
    assert len(mock_window.changes) == 2


def test_mock_window_refresh(mock_window):
    assert mock_window.refreshes == 0
    
    mock_window.refresh()
    
    assert mock_window.refreshes == 1


def test_mock_window_resize(mock_window):
    mock_window.max_y = 50
    mock_window.max_x = 160
    
    y, x = mock_window.getmaxyx()
    
    assert y == 50
    assert x == 160


def test_mock_window_enclose(mock_window):
    assert mock_window.enclose(10, 20) is True
    assert mock_window.enclose(-1, 10) is False
    assert mock_window.enclose(100, 20) is False


def test_curses_mock_constants(mock_curses):
    assert mock_curses.KEY_DOWN == 258
    assert mock_curses.KEY_UP == 259
    assert mock_curses.KEY_LEFT == 260
    assert mock_curses.KEY_RIGHT == 261
    assert mock_curses.KEY_ENTER == 10
    assert mock_curses.KEY_BACKSPACE == 263


def test_curses_mock_color_pair(mock_curses):
    pair = mock_curses.color_pair(5)
    assert pair == 5 * 256


def test_curses_mock_init_pair(mock_curses):
    mock_curses.init_pair(1, 2, 0)
    
    assert 1 in mock_curses.current_color_pairs
    assert mock_curses.current_color_pairs[1] == (2, 0)


def test_curses_mock_multiple_color_pairs(mock_curses):
    mock_curses.init_pair(1, 2, 0)
    mock_curses.init_pair(2, 4, 0)
    mock_curses.init_pair(3, 6, 0)
    
    assert len(mock_curses.current_color_pairs) == 3
    assert mock_curses.current_color_pairs[2] == (4, 0)
    assert mock_curses.current_color_pairs[3] == (6, 0)
