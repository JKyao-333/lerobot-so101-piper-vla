from robot_learning.logging_utils import contains_sensitive_text, sanitize_text
from scripts.sanitize_logs import contains_unapproved_sensitive_text


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


def test_documented_manual_path_is_allowed_only_in_repository_scan() -> None:
    path = "/root/autodl-tmp/checkpoints/smolvla_piper_test/020000/pretrained_model"
    assert contains_sensitive_text(path)
    assert not contains_unapproved_sensitive_text(path)


def test_unlisted_autodl_path_is_still_rejected() -> None:
    assert contains_unapproved_sensitive_text("/root/autodl-tmp/private/unreviewed")
