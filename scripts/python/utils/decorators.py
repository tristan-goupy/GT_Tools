####################### Decorators #######################
# Imports
import sys
import traceback
import time
import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

def err_handler(func, name="", plugin=False, silent=False):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if not silent:
                exc_type, exc_obj, exc_tb = sys.exc_info()

                data = {}
                versionStr = ""
                logger.error(f"[{name}] ERROR in {func.__name__}: {e}")
    return func_wrapper

def err_catcher(name, silent=False):
    return lambda x, y=name, z=False: err_handler(x, name=y, plugin=z, silent=silent)

def err_catcher_plugin(name):
    return lambda x, y=name, z=True: err_handler(x, name=y, plugin=z)

def timer(name):
    def timer_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            startTime = datetime.now()
            logger.info("starttime: %s" % startTime.strftime("%Y-%m-%d %H:%M:%S"))
            func(*args, **kwargs)
            endTime = datetime.now()
            logger.info("endtime: %s" % endTime.strftime("%Y-%m-%d %H:%M:%S"))
            logger.info("duration: %s" % (endTime - startTime))

        return func_wrapper
    
    return timer_decorator