from .core_testing import session_testing


def test_method(session_testing):
    print("session_testing", session_testing)
    result = 1 + 3
    assert result == 4
