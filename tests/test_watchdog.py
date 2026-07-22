from robot_learning.safety.watchdog import NetworkSafetyMonitor, Watchdog


class Robot:
    def __init__(self) -> None:
        self.stop_count = 0

    def stop(self) -> None:
        self.stop_count += 1


def test_network_timeout_enters_safe_stop_path() -> None:
    now = [0.0]
    watchdog = Watchdog(2.0, clock=lambda: now[0])
    assert not watchdog.expired()
    now[0] = 2.0
    assert watchdog.expired()
    assert watchdog.remaining_s == 0.0


def test_network_monitor_stops_robot_once_after_timeout() -> None:
    now = [0.0]
    robot = Robot()
    monitor = NetworkSafetyMonitor(Watchdog(1.0, clock=lambda: now[0]))
    assert not monitor.enforce(robot)
    now[0] = 1.0
    assert monitor.enforce(robot)
    assert monitor.enforce(robot)
    assert robot.stop_count == 1
