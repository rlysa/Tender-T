from .commands.start import router as router_start
from .commands.add_script import router as router_add_script


routers = [router_start, router_add_script]