#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Generator

from _pytest.capture import CaptureFixture

from punchbox.utils.assertion import Assertion


class TestAssertion(object):
    @staticmethod
    def out(capfd: Generator[CaptureFixture[str], None, None]) -> str:
        _out: str
        _err: str
        out, err = capfd.readouterr()
        return str(out)

    def test_evaluation_if_none_else(
        self, capfd: Generator[CaptureFixture[str], None, None]
    ) -> None:
        Assertion.evaluate_if_then_else(
            1 == 0,
            is_asserted=lambda: print("hello"),
            is_not_asserted=lambda: print("yeah"),
        )
        assert TestAssertion.out(capfd) == "yeah\n"
        Assertion.evaluate_if_then_else(
            1 == 1,
            is_asserted=lambda: print("hello"),
            is_not_asserted=lambda: print("yeah"),
        )
        assert TestAssertion.out(capfd) == "hello\n"
        Assertion.evaluate_if_then_else(1 == 1, is_not_asserted=lambda: print("hello"))
        assert TestAssertion.out(capfd) == ""
        Assertion.evaluate_if_then_else(1 == 0, is_asserted=lambda: print("hello"))
        assert TestAssertion.out(capfd) == ""
        Assertion.evaluate_if_then_else(1 == 0)
        assert TestAssertion.out(capfd) == ""
        Assertion.evaluate_if_then_else(1 == 1)
        assert TestAssertion.out(capfd) == ""
