# Source: https://github.com/Lonami/TelethonianBotExt/blob/master/__init__.py


import asyncio
import importlib
import inspect
import os
import time

from loguru import logger


async def init(bot):
    plugins = [
        # Dynamically import
        importlib.import_module(f".", f"{__name__}.{file[:-3]}")
        # All the files in the current directory
        for file in os.listdir(os.path.dirname(__file__))
        # If they start with a letter and are Python files
        if file[0].isalpha()
        and file.endswith(".py")
        and not file.startswith("!example")
    ]

    # Keep a mapping of module name to module for easy access inside the bot_actions
    modules = {m.__name__.split(".")[-1]: m for m in plugins}

    # All kwargs provided to get_init_args are those that bot_actions may access
    to_init = (get_init_coro(plugin, bot=bot, modules=modules) for plugin in plugins)

    # Plugins may not have a valid init so those need to be filtered out
    await asyncio.gather(*(filter(None, to_init)))


def get_init_coro(plugin, **kwargs):
    p_init = getattr(plugin, "init", None)
    if not callable(p_init):
        return

    result_kwargs = {}
    sig = inspect.signature(p_init)
    for param in sig.parameters:
        if param in kwargs:
            result_kwargs[param] = kwargs[param]
        else:
            logger.error(
                "Plugin %s has unknown init parameter %s",
                plugin.__name__,
                param.__name__,
            )
            return

    return _init_plugin(plugin, result_kwargs)


async def _init_plugin(plugin, kwargs):
    try:
        logger.warning(f"Loading plugin {plugin.__name__}…")
        start = time.time()
        ret = await plugin.init(**kwargs)
        took = time.time() - start
        logger.warning(f"Loaded plugin {plugin.__name__} (took {took:.2f}s)")
    except Exception as e:
        logger.exception(f"Failed to load plugin {plugin} with error {e}")
    else:
        # Plugins may return a task that should not just be lost.
        if asyncio.iscoroutinefunction(ret):
            await ret


async def start_plugins(bot, plugins):
    await asyncio.gather(*(_init_plugin(bot, plugin) for plugin in plugins))