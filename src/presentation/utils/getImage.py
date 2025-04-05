import src.presentation.screens.mainMenu as mainMenu
import src.presentation.screens.map as mapScreens
import src.presentation.screens.ship as shipScreens
import src.presentation.screens.arena as arenaScreens
import src.presentation.screens.registry as registry


def getImage(screenId: str):
    # https://www.reddit.com/r/programminghorror/comments/1cb6rca/source_code_from_balatro/

    match screenId:
        case mapScreens.MAP:
            return "https://i.imgur.com/yud0H9N.png"
        case arenaScreens.ARENA:
            return "https://i.imgur.com/3Tnlupf.png"
        case mainMenu.DEFAULT:
            return "https://i.imgur.com/VJLWNIn.png"
        case shipScreens.SHIP:
            return "https://i.imgur.com/1RCjddx.png"
        case _:
            return "https://i.imgur.com/I8oPG0w.png"
        
