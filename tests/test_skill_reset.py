from tests.test_dual_act_state_machine import machine


def test_both_policies_reset_at_start_and_b_resets_again_on_handoff() -> None:
    state, policy_a, policy_b = machine()
    state.start()
    assert policy_a.resets == 1
    assert policy_b.resets == 1
    state.complete_skill_a()
    state.confirm_handoff()
    assert policy_a.resets == 1
    assert policy_b.resets == 2

