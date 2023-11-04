from asyncio import (
    gather,
    create_task,
    to_thread,
    wait
)

from asyncio import (
    Task
)

from typing import (
    Any,
    Coroutine
)

def run_in_background(coro: Coroutine) -> Task:
    """Runs coroutine in the background, returning the created `asyncio.Task`

    Args:
        coro (Coroutine): Corotune to execute in the background.

    Returns:
        Task: The task created.
    """    
    create_task(coro)

def run_in_background_promise(coro: Coroutine, timeout: int = 7) -> Any:
    """Runs coroutine and returns un-awaited `asyncio.wait` function for you to await when ready.

    Args:
        coro (Coroutine):  Coroutine to execute in the background and wait for.
        timeout (int, optional): The max time waiting for the coroutine to execute. Defaults to 7.

    Returns:
        Any
    """
    task = create_task(coro)
    return wait(task, timeout=timeout)

async def run_tasks_concurrent(coros: list[Coroutine]) -> Any:
    """Runs `asyncio.gather` on provided coroutines. Please provite arguments to coroutine before passing.

    Args:
        coros (list[Coroutine]): The list of initialized coroutines (with arguments) ready to be awaited.

    Returns:
        Any: Results from `asyncio.gather`.
    """    
    return await gather(*coros)