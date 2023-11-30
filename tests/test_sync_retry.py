from easy_retry import retry
import pytest
from time import time

BACKOFF_DEVIATION = 0.005


@pytest.mark.parametrize('attempts', [1, 5, 7])
def test_attempts(attempts):
    current_attempts = 0

    @retry(attempts=attempts)
    def zero_divider():
        nonlocal current_attempts
        current_attempts += 1
        return 5 / 0

    try:
        zero_divider()
    except ZeroDivisionError:
        pass

    assert current_attempts == attempts, (
        'Count of retries doesnt match with parameter value'
    )


@pytest.mark.parametrize('backoff', [0.5, 2])
def test_backoff(backoff):
    times = []

    @retry(attempts=3, backoff=backoff)
    def zero_divider():
        nonlocal times
        times.append(time())
        return 5 / 0

    try:
        zero_divider()
    except ZeroDivisionError:
        pass

    time_differences = [times[i + 1] - times[i] for i in range(len(times) - 1)]

    average_backoff = sum(time_differences) / (len(times) - 1)

    assert average_backoff - backoff < BACKOFF_DEVIATION, (
        "Backoff doesnt match with parameter value"
    )
