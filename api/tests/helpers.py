import pytest
import requests


def assert_dict_subset(res: dict, exp: dict, *, name: str | None = None, resp_text: str | None = None):
    """Goes through each key in b, check if it exists in a and if the values match.
    If the key doesn't exist, the test fails, if it exists but the values don't match
    the assert will fail and propegate up.
    """
    for exp_key, exp_val in exp.items():
        try:
            res_val = res[exp_key]
        except KeyError:
            msg = []
            if name:
                msg.append(f"[{name}]")
            msg.append(f"missing key {exp_key!r} in {res}")
            if resp_text:
                msg.append(f"response text: {resp_text}")
            pytest.fail(" ".join(msg))

        assert res_val == exp_val, f"error asserting dict, got: {res_val}, expected: {exp_val}"


def assert_status_code(exp: int, r: requests.Response):
    if r.status_code != exp:
        pytest.fail(
            f"wrong status code: expected: {exp}, got: {r.status_code}\n"
            + f"response body: {r.text}"
        )
