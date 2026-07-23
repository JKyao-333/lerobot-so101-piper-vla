import argparse
from unittest.mock import Mock

import pytest

from scripts import run_dual_act


def apply(answer: str) -> tuple[bool, Mock]:
    machine = Mock()
    return run_dual_act.apply_handoff_answer(machine, answer), machine


def test_empty_input_confirms_handoff() -> None:
    confirmed, machine = apply("")
    assert confirmed
    machine.confirm_handoff.assert_called_once_with()


def test_yes_confirms_handoff() -> None:
    confirmed, machine = apply("yes")
    assert confirmed
    machine.confirm_handoff.assert_called_once_with()


def test_next_confirms_handoff() -> None:
    confirmed, machine = apply("next")
    assert confirmed
    machine.confirm_handoff.assert_called_once_with()


def test_n_rejects_handoff() -> None:
    confirmed, machine = apply("n")
    assert not confirmed
    machine.abort.assert_called_once_with("operator rejected handoff")


def test_no_rejects_handoff() -> None:
    confirmed, machine = apply("no")
    assert not confirmed
    machine.abort.assert_called_once_with("operator rejected handoff")


def test_q_rejects_handoff() -> None:
    confirmed, machine = apply("q")
    assert not confirmed
    machine.abort.assert_called_once_with("operator rejected handoff")


def test_unknown_handoff_input_aborts() -> None:
    confirmed, machine = apply("continue maybe")
    assert not confirmed
    machine.abort.assert_called_once_with("unrecognized handoff confirmation")


class FailingLoadAdapter:
    instances: list["FailingLoadAdapter"] = []
    fail_on_load = 1
    fail_cleanup = False

    def __init__(self, **kwargs) -> None:
        del kwargs
        self.load_count = 0
        self.disconnect_count = 0
        self.hold_count = 0
        self.__class__.instances.append(self)

    def connect(self) -> None:
        return None

    def load_skill(self, checkpoint, task):
        del checkpoint, task
        self.load_count += 1
        if self.load_count == self.fail_on_load:
            raise RuntimeError(f"skill {self.load_count} load failed")
        return Mock()

    def hold_current_pose_best_effort(self) -> bool:
        self.hold_count += 1
        if self.fail_cleanup:
            raise RuntimeError("cleanup hold failed")
        return True

    def disconnect(self) -> None:
        self.disconnect_count += 1
        if self.fail_cleanup:
            raise RuntimeError("cleanup disconnect failed")


def hardware_args() -> argparse.Namespace:
    return argparse.Namespace(
        config="configs/dual_act/dual_act.example.yaml",
        hardware=True,
        execute_robot=False,
        auto_confirm_mock=False,
    )


def run_with_failing_adapter(monkeypatch, *, fail_on_load: int, fail_cleanup: bool = False):
    FailingLoadAdapter.instances = []
    FailingLoadAdapter.fail_on_load = fail_on_load
    FailingLoadAdapter.fail_cleanup = fail_cleanup
    monkeypatch.setattr(run_dual_act, "parse_args", hardware_args)
    monkeypatch.setattr(run_dual_act, "LerobotPiperAdapter", FailingLoadAdapter)
    with pytest.raises(RuntimeError, match=f"skill {fail_on_load} load failed") as caught:
        run_dual_act.main()
    return caught.value, FailingLoadAdapter.instances[0]


def test_skill_a_load_failure_disconnects_adapter(monkeypatch) -> None:
    _, adapter = run_with_failing_adapter(monkeypatch, fail_on_load=1)
    assert adapter.hold_count == 1
    assert adapter.disconnect_count == 1


def test_skill_b_load_failure_disconnects_adapter(monkeypatch) -> None:
    _, adapter = run_with_failing_adapter(monkeypatch, fail_on_load=2)
    assert adapter.hold_count == 1
    assert adapter.disconnect_count == 1


def test_cleanup_does_not_hide_original_exception(monkeypatch, caplog) -> None:
    error, adapter = run_with_failing_adapter(monkeypatch, fail_on_load=1, fail_cleanup=True)
    assert str(error) == "skill 1 load failed"
    assert adapter.disconnect_count == 1
    assert "partial-initialization cleanup" in caplog.text
    assert "disconnect failed during final cleanup" in caplog.text
