from bot.start import router as router_start
from bot.add_script import router as router_add_script
from bot.get_access import router as router_get_access
from bot.admin import router as router_admin
from bot.pipeline_add_script import router as router_add_script_P


routers = [router_start, router_add_script, router_get_access, router_admin, router_add_script_P]