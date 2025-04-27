import src.presentation.screens.mainMenu as mainMenu
import src.presentation.screens.map as mapScreens
import src.presentation.screens.ship as shipScreens
import src.presentation.screens.arena as arenaScreens
import src.presentation.screens.admin as adminScreens


def getImage(screenId: str):
    match screenId:
        case mapScreens.MAP:
            return "https://i.imgur.com/yud0H9N.png"
        case arenaScreens.ARENA_QUEUE:
            return "https://i.imgur.com/2wI46ca.png"
        case shipScreens.SHIP_BODY_REPAIR:
            return "https://i.imgur.com/UqtdzZI.png"
        case shipScreens.SHIP_WEAPON_UPGRADE:
            return "https://i.imgur.com/LskyLC3.png"
        case shipScreens.SHIP_HULL_UPGRADE:
            return "https://i.imgur.com/LskyLC3.png"
        case arenaScreens.ARENA:
            return "https://i.imgur.com/3Tnlupf.png"
        case mainMenu.DEFAULT:
            return "https://i.imgur.com/VJLWNIn.png"
        case shipScreens.SHIP:
            return "https://i.imgur.com/1RCjddx.png"
        case adminScreens.ADMIN:
            return "https://i.imgur.com/6QVpF1p.png"
        case _:
            return "https://i.imgur.com/I8oPG0w.png"
