import asyncio
from asynctosync.common import transform_sync_decorator


class TestAsyncSyncClass:
    def __init__(self, sync: bool = False, value: float = 4) -> None:
        self.value = value
        self.sync = sync

    @transform_sync_decorator
    async def print_value(self, _time: float = 3) -> int | float:
        await asyncio.sleep(_time)
        print(self.value)

    def set_value(self, value) -> int:
        self.value = value


async def example_async():
    asyncclass = TestAsyncSyncClass()
    await asyncclass.print_value(2)
    asyncclass.set_value(44)
    await asyncclass.print_value(3)


def example_sync():
    syncclass = TestAsyncSyncClass(sync=True)
    syncclass.print_value(2)
    syncclass.set_value(66)
    syncclass.print_value(3)


if __name__ == "__main__":
    asyncio.run(example_async())
    example_sync()
