import logging
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

import requests

logger = logging.getLogger(__name__)

def FileActionResults(extension, app_id):

    if(not CheckIfAppIsInstalled(app_id=app_id)):

        return [
                ExtensionResultItem(
                    icon='images/Install.png',
                    name='Install',
                    on_enter=RunScriptAction(f"flatpak install -y flathub {app_id}")
                )
            ]
    
    else:

        return [
            ExtensionResultItem(
                icon='images/Update.png',
                name='Update',
                on_enter=RunScriptAction(f"flatpak update -y {app_id}")
            ),
            ExtensionResultItem(
                icon='images/Uninstall.png',
                name='Uninstall',
                on_enter=RunScriptAction(f"flatpak uninstall -y {app_id}")
            )
        ]
    

def CheckIfAppIsInstalled(app_id):

    result = subprocess.run(["flatpak","info", app_id], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    if(result.returncode == 0):
        logger.info(f"{app_id} Exists")
        return True
    else:
        logger.info(f"{app_id} Does Not Exists")
        return False






class DemoExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):

        if not event.get_argument():
            return RenderResultListAction([ExtensionResultItem(icon='images/icon.png',
                                                               name=f'{extension.preferences["kw"]} <app>',
                                                               on_enter=HideWindowAction())])

        items = []
        
        responce = requests.post("https://flathub.org/api/v2/search?locale=en", json=
        {
            "query": event.get_argument()
        })

        print(str(responce.json()["hits"][0]["app_id"]))

        for i in range(len(responce.json()["hits"])):

            if(i >= 10):
                break

            items.append(ExtensionResultItem(icon='images/icon.png',
                                    name=str(responce.json()["hits"][i]["name"]),
                                    description=str(responce.json()["hits"][i]["description"]).replace("\n", "")[:100],
                                    on_enter=RenderResultListAction(FileActionResults(extension=extension, app_id=responce.json()["hits"][i]["app_id"]))))
        
        return RenderResultListAction(items)

if __name__ == '__main__':
    DemoExtension().run()