import pytest


def assert_dict_subset(a: dict, b: dict, *, name: str | None = None, resp_text: str | None = None):
    """Goes through each key in b, check if it exists in a and if the values match.
    If the key doesn't exist, the test fails, if it exists but the values don't match
    the assert will fail and propegate up.
    """
    for b_key, b_val in b.items():
        try:
            a_val = a[b_key]
        except KeyError:
            msg = []
            if name:
                msg.append(f"[{name}]")
            msg.append(f"missing key {b_key!r} in {a}")
            if resp_text:
                msg.append(f"response text: {resp_text}")
            pytest.fail(" ".join(msg))

        assert a_val == b_val
        print(f"comparing {a_val} and {b_val}")
