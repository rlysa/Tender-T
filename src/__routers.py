from .commands.start import router as router_start
from .commands.add_script import router as router_add_script
from .commands.get_access import router as router_get_access


routers = [router_start, router_add_script, router_get_access]