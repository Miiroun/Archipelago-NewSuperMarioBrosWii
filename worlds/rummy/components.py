from worlds.LauncherComponents import Component, Type, components, launch
from worlds.rummy.Common import *



def run_client(*args: str) -> None:
    from .client.launch import launch_rummy_client
    launch(launch_rummy_client, name=f"{RUMMY_NAME} Client", args=args)

components.append(
    Component(
        f"{RUMMY_NAME} Client",
        func=run_client,
        game_name=f"{RUMMY_NAME}",
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)
