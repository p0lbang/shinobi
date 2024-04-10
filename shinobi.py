from PIL import ImageGrab, Image
import pyautogui
import easyocr
import numpy
import time

from dataclasses import dataclass
from typing import List

import collections
import logging


@dataclass
class Actions:
    ui: List[str]
    attacks: List[str]


@dataclass
class State:
    forceclose: bool


logging.basicConfig(
    filename="runtime.txt",
    level=logging.DEBUG,
    format="%(asctime)s: %(message)s",
)

values = {
    "Mission": (1425, 773, 2.5),
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
    "Battle.Talent.5": (805, 457),
    "Battle.Talent.6": (898, 548),
    "Battle.Talent.7": (1000, 548),
    "Battle.Talent.8": (1090, 457),
    "Accomplished": (1658, 696, 2.25),
    "LevelUp": (1662, 766, 1),
    "Center": (960, 540, 0),
}

reader = easyocr.Reader(["en"], verbose=False)


class Shinobi:
    def __init__(self):
        self.actions: Actions = Actions(
            ui=[
                "Mission",
                "Mission.Grade.C",
                # "Mission.Menu.Next",
                "Mission.Menu.Option1",
                "Mission.Menu.Accept",
            ],
            attacks=[
                "Battle.Skill.1",
                "Battle.Talent.2",
                "Battle.Skill.2",
                "Battle.Skill.3",
                "Battle.Talent.4",
                "Battle.Skill.4",
                "Battle.Skill.8", 
                "Battle.Skill.Charge",
                "Battle.Talent.5",
                "Battle.Talent.6",
                # "Battle.Skill.5",
                # "Battle.Skill.6",
                # "Battle.Skill.7",
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
        sc = self.getScreen()
        self.checkIfFullscreen(sc)

        self.autoUI()

        sc = self.getScreen()
        self.checkIfFullscreen(sc)

        self.autoAttacks()

    def autoUI(self):
        for k in self.actions.ui:
            self.clickSleep(k)
            if self.state.forceclose:
                print("Forced Close")
                break

    def checkIfFullscreen(self, sc: Image):
        cropped = sc.crop((0, 0, 200, 30))
        text = self.getText(cropped).lower()
        if not ("shinobi" in text or "warfare" in text):
            exit()

    def autoAttacks(self):
        Accomplished = False

        attackslength = len(self.actions.attacks)
        attackindex = 0

        recentAttacks = collections.deque(maxlen=3)
        while not self.state.forceclose:
            k = self.actions.attacks[attackindex % attackslength]

            self.click("Center")
            while not self.state.forceclose:
                sc = self.getScreen()

                self.checkIfFullscreen(sc)

                cropped = sc.crop((840, 830, 1070, 910))
                text = self.getText(cropped).lower()
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

                time.sleep(0.25)

            if Accomplished:
                break

            # check if the 3 latest tries where the same attack so we could skip it
            if len(recentAttacks) == 3 and recentAttacks.count(recentAttacks[0]) == 3:
                if recentAttacks[0] != "Battle.Skill.Attack":
                    attackindex += 1
                    self.click("Battle.Skill.Attack")
                    recentAttacks.clear()
                    continue

            self.click(k)

            # Check if restricted
            time.sleep(0.1)
            sc = self.getScreen()
            if self.checkAbleToAttack(sc):
                # print("RESTRICTED: Doing a basic attack")
                # try next skill
                tryk = self.actions.attacks[(attackindex+1) % attackslength]
                self.click(tryk)
                
                sc = self.getScreen()
                if self.checkAbleToAttack(sc):
                    self.click("Battle.Skill.Attack")
                    tryk = "Battle.Skill.Attack"
                else:
                    attackindex += 2
                    
                recentAttacks.append(tryk)
                continue

            # print(f"Attack Index: {attackindex}")
            recentAttacks.append(k)
            attackindex += 1
    
    def checkAbleToAttack(self, sc: Image):
        cropped = sc.crop((840, 830, 1070, 910))
        text = self.getText(cropped).lower()
        return "run" in text or "charge" in text or "attack" in text or "skip" in text

    def start(self):
        print("Starting Shinobi script")
        while True:
            start = time.time()
            self.grind()
            print(f"Runtime: {time.time()-start}")
            logging.info(f"Runtime: {time.time()-start}")

    def experiment(self):
        time.sleep(2)
        logging.basicConfig(
            filename="debuff.txt",
            level=logging.DEBUG,
            format="%(asctime)s: %(message)s",
        )
        inc = 0
        while True:
            sc = self.getScreen()
            # sc = sc.convert("L")
            # cropped = sc.crop((840,830,1070,910))
            # cropped = sc.crop((401,245,665,466))
            cropped = sc.crop((0, 0, 200, 30))
            text = self.getText(cropped)
            if len(text) > 2:
                inc += 1
                cropped.save(f"images/debuff-{inc}.jpg")
                logging.info(f"debuff-{inc}: {text}")

            time.sleep(0.25)


if __name__ == "__main__":
    SHINOBI = Shinobi()
    SHINOBI.start()
    # SHINOBI.autoAttacks()
    # SHINOBI.experiment()
