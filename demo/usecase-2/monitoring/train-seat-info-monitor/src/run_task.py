async def run_task(logger, q, task_func):
    try:
        await task_func()
    except Exception:
        # if a task throws an exception, exit whole program
        logger.exception(f"Exception running {task_func.__name__}. Exit program")
        await q.put("stop")
