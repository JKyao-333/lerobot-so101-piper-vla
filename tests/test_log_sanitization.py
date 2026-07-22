from robot_learning.logging_utils import contains_sensitive_text, sanitize_text


def test_sensitive_values_are_redacted() -> None:
    text = "ssh root@example.com; token=hf_abcdefghijklmnopqrstuvwxyz; path=/home/alice/work"
    sanitized = sanitize_text(text)
    assert "root@example.com" not in sanitized
    assert "hf_abcdefghijklmnopqrstuvwxyz" not in sanitized
    assert "/home/alice" not in sanitized
    assert contains_sensitive_text(text)


def test_safe_placeholder_is_unchanged() -> None:
    text = "SSH_HOST=example.invalid\nSSH_USER=example_user\n"
    assert sanitize_text(text) == text

