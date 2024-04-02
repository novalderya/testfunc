import asyncio
from asynctosync.common import _transform_sync_class


class Test:

    def __init__(self) -> None:
        pass

    async def print_value(self, _time: float = 1) -> int:
        await asyncio.sleep(_time)
        print("print")


class TestHerit(Test):

    def __init__(self) -> None:
        pass

    def print_value(self, _time: float = 3):
        self._convert(self.print_value, _time)

    def _convert(self, func, *args, **kwargs):
        func_name = func.__name__
        setattr(
            self, func_name, _transform_sync_class(self, getattr(super(), func_name))
        )
        getattr(self, func_name)(*args, **kwargs)


if __name__ == "__main__":
    a = TestHerit()
    a.print_value(5)
    a.print_value()
    a.print_value()
