from PIL import ImageGrab, Image
import pyautogui
import easyocr
import numpy
import time

from dataclasses import dataclass
from typing import List


@dataclass
class Actions:
    ui: List[str]
    attacks: List[str]


@dataclass
class State:
    forceclose: bool


values = {
    "Mission": (1425, 773, 2.25),
    "Mission.Grade.C": (1298, 593, 0.4),
    "Mission.Grade.D": (1298, 737, 0.4),
    "Mission.Menu.Accept": (1416, 767, 3),
    "Mission.Menu.Next": (1369, 775, 0.3),
    "Mission.Menu.Option1": (1037, 318, 0.3),
    "Mission.Menu.Option2": (1037, 473, 0.3),
    "Mission.Menu.Option3": (1037, 634, 0.3),
    "Battle.Skill.1": (490, 820, 8),
    "Battle.Skill.2": (590, 820, 8),
    "Battle.Skill.3": (690, 820, 8),
    "Battle.Skill.4": (790, 820, 8),
    "Battle.Skill.5": (1110, 820, 8),
    "Battle.Skill.6": (1210, 820, 8),
    "Battle.Skill.7": (1310, 820, 8),
    "Battle.Skill.8": (1410, 820, 8),
    "Battle.Skill.Attack": (900, 745, 8),
    "Battle.Skill.Skip": (1010, 745),
    "Battle.Skill.Charge": (900, 850),
    "Battle.Skill.Run": (1010, 850),
    "Battle.Talent.1": (805, 353),
    "Battle.Talent.2": (898, 269),
    "Battle.Talent.3": (1000, 269),
    "Battle.Talent.4": (1090, 353),
    "Accomplished": (1658, 696, 2.5),
    "LevelUp": (1662, 766, 1),
    "Center": (960, 540, 0),
    # "", (,),
}

reader = easyocr.Reader(["en"])


class Shinobi:
    def __init__(self):
        self.actions: Actions = Actions(
            ui=[
                "Mission",
                "Mission.Grade.C",
                "Mission.Menu.Option1",
                "Mission.Menu.Accept",
            ],
            attacks=[
                "Battle.Talent.4",
                "Battle.Skill.3",
                "Battle.Skill.8",
                "Battle.Skill.5",
                "Battle.Skill.1",
                "Battle.Skill.4",
                "Battle.Skill.2",
                "Battle.Skill.Charge",
                "Battle.Skill.Attack",
                "Battle.Skill.7",
                "Battle.Skill.6",
                "Battle.Skill.Attack",
                "Battle.Skill.Charge",
                "Battle.Skill.Charge",
            ],
        )
        self.state = State(forceclose=False)

    def setStateForceClose(self, value: bool):
        self.state.forceclose = value

    def getScreen(self):
        screenshot = ImageGrab.grab()
        return screenshot

    def getText(self, image: Image):
        result = reader.recognize(numpy.array(image))
        (_, text, _) = result[0]
        return text

    # def ProcessText_OLD():
    #     image = getScreen()
    #     text = pytesseract.image_to_string(image, lang="eng")
    #     return text

    def ProcessText(self):
        image = self.getScreen()
        return self.getText(image)

    def click(self, k: str):
        v = values[k]
        pyautogui.moveTo(v[0], v[1])
        pyautogui.leftClick()

    def clickSleep(self, k: str):
        v = values[k]
        pyautogui.moveTo(v[0], v[1])
        pyautogui.leftClick()
        sleeptime = 5
        if len(v) == 3:
            sleeptime = v[2]
        time.sleep(sleeptime)

    def grind(self):
        for k in self.actions.ui:
            self.clickSleep(k)
            if self.state.forceclose:
                print("Forced Close")
                break

        Accomplished = False

        for k in self.actions.attacks:
            self.click("Center")
            while not self.state.forceclose:
                # print("Image processing")

                sc = self.getScreen()
                # cropped = sc.crop((840,700,1070,905))
                cropped = sc.crop((840, 830, 1070, 910))

                text = self.getText(cropped).lower()
                print(f"Printing text: {text}")
                if (
                    "run" in text
                    or "charge" in text
                    or "attack" in text
                    or "skip" in text
                ):
                    break

                cropped = sc.crop((641, 132, 1448, 255))
                text = self.getText(cropped).lower()
                if "accomplished" in text:
                    self.clickSleep("Accomplished")
                    Accomplished = True
                    break

                cropped = sc.crop((641, 132, 1448, 400))
                text = self.getText(cropped).lower()
                if "level" in text or "up" in text:
                    self.clickSleep("LevelUp")
                    break

                time.sleep(0.5)

            if Accomplished:
                break

            if self.state.forceclose:
                print("Forced Close")
                break

            self.click(k)

    def start(self):
        print("Starting Shinobi script")
        while True:
            start = time.time()
            self.grind()
            print(f"Runtime: {time.time()-start}")


if __name__ == "__main__":
    SHINOBI = Shinobi()
    SHINOBI.start()

# time.sleep(2)
# sc = getScreen().convert("L")
# # cropped = sc.crop((840,830,1070,910))
# cropped = sc.crop((641,132,1448,400))
# cropped.save("test.png")
# print(getText(cropped))
