from __future__ import annotations
import asyncio
from asynctosync.common import _transform_sync_class, _transform_sync_function
import asyncio


class TestAsyncClass:
    def __init__(self, value: float = 4) -> None:
        self.value = value
        self.event = asyncio.Event()

    async def print_value(self, _time: float = 3) -> int:
        await asyncio.sleep(_time)
        print(self.value)

    def set_value(self, value) -> int:
        self.value = value

    async def wait_for_event(self) -> None:
        await self.event.wait()

    async def _test_loop(self) -> None:
        i = 0
        while not self.event.is_set():
            print("in loop ", i)
            await asyncio.sleep(1)
            i += 1
            if i == 5:
                self.event.set()
                break

    def start_task(self) -> None:
        self.loop = asyncio.create_task(self._test_loop())


def for_all_methods(decorator):
    def decorate(cls: TestSyncClass):
        for attr in cls.FUNCTION_TO_CONVERT:  # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(cls, getattr(cls, attr)))
        return cls

    return decorate


# @for_all_methods(_transform_sync_class)
class TestSyncClass(TestAsyncClass):
    FUNCTION_TO_CONVERT = (
        "",
        "wait_for_event",
        "_test_loop",
        "print_value",
        "start_task",
    )
    pass

    def __init__(self, value: float = 4) -> None:
        _transform_sync_class(self, super().__init__)(value)
        # for function in self.FUNCTION_TO_CONVERT:
        #     setattr(self, function, _transform_sync_class(self, super().print_value))

    # def wait_for_event(self) -> None:
    #     return _transform_sync_class(self, super().wait_for_event)()

    # def _test_loop(self) -> None:
    #     return _transform_sync_class(self, super()._test_loop)()

    # def print_value(self, time: float = 3) -> int:
    #     return _transform_sync_class(self, super().print_value)(time)

    # def start_task(self) -> None:
    #     return _transform_sync_class(self, super().start_task)()

    def _convert(self, func, *args, **kwargs):
        func_name = func.__name__
        setattr(
            self, func_name, _transform_sync_class(self, getattr(super(), func_name))
        )
        getattr(self, func_name)(*args, **kwargs)


async def example_async():
    asyncclass = TestAsyncClass()
    print("******************** Start Async test ********************")
    await asyncclass.print_value(2)
    asyncclass.set_value(44)
    await asyncclass.print_value(3)
    asyncclass.start_task()
    await asyncclass.wait_for_event()
    print("******************** End Async test ********************")


def example_sync():
    syncclass = TestSyncClass()
    print("******************** Start Sync test ********************")
    syncclass.print_value(2)
    syncclass.set_value(44)
    syncclass.print_value(3)
    syncclass.start_task()
    syncclass.wait_for_event()
    print("******************** End Sync test ********************")


if __name__ == "__main__":
    # asyncio.run(example_async())
    example_sync()
