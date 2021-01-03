#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
from typing import Callable


class Assertion(object):
    def __init__(self) -> None:
        """
        static class
        """
        ...

    @staticmethod
    def evaluate_if_then_else(
        bool_value: bool,
        is_asserted: Callable[..., Any] = lambda *args, **kwargs: None,
        is_not_asserted: Callable[..., Any] = lambda *args, **kwargs: None,
    ) -> None:
        """
        evaluate bool_value

        If evaluation is True, will execute first argument as a Callable
          - is_asserted()
        Else will execute the second argument as a callable
          - is_not_asserted()

        While value parameter is mandatory, it is also possible to use only when_none or when_not_none
        parameter. By default, Nothing is done.

        Usage:

        .. code-block:: python
            myObject: bool = True
            AssertUtils.evaluate_if_then_else(myObject, lambda: print("hello"), lambda: print("bye"))
            # will print "hello"
            myObject: bool = False
            AssertUtils.evaluate_if_then_else(myObject, lambda: print("hello"), lambda: print("bye"))
            # will print "bye"
        """
        if bool_value:
            return is_asserted()
        else:
            return is_not_asserted()
