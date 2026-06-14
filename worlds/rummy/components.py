from worlds.LauncherComponents import Component, Type, components, launch, icon_paths
from worlds.rummy.Common import *


def run_client(*args: str) -> None:
    import webbrowser
    hostname: str = ""
    port: str = ""
    name: str = ""
    password: str = ""
    print(f"args {args}")
    try:
        split_url = args.url.split(":")
        hostname = split_url[0]
        port = split_url[1]
        split_name = args.name.split("@")
        name = split_name[0]
        password = split_name[1]
    except:
        pass

    webbrowser.open(
        f"https://miiroun.github.io/ap-rummy/?Hostname={hostname}&Port={port}&Name={name}&Password={password}", new=-1)


components.append(
    Component(
        f"{RUMMY_NAME} Client",
        func=run_client,
        game_name=f"{RUMMY_NAME}",
        component_type=Type.CLIENT,
        supports_uri=True,
        icon="docs/img/completed_board.png"
    )
)

icon_paths[f"{RUMMY_NAME}",] = f"ap:{__name__}/assets/component_icon.png"
