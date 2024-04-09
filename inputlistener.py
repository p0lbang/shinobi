import pyautogui
from pynput.mouse import Listener as MouseListener, Button
from pynput.keyboard import Listener as KeyboardListener, Key
import logging

from shinobi import Shinobi


class InputListener:
    def __init__(self, shinobi: Shinobi):
        logging.basicConfig(
            filename="mouse_log.txt",
            level=logging.DEBUG,
            format="%(asctime)s: %(message)s",
        )
        self.Shinobi = shinobi

    def on_press(self, key):
        if "char" in dir(key):  # check if char method exists,
            print(key.char)
            if key.char == "q":  # check if it is 'q' key
                self.stop()
            elif key.char == "s":
                self.Shinobi.start()

    def on_move(self, x, y):
        logging.info("Mouse moved to ({0}, {1})".format(x, y))

    def on_click(self, x, y, button, pressed):
        if pressed and button == Button.right:
            print(pyautogui.position())
            logging.info("Mouse clicked at ({0}, {1}) with {2}".format(x, y, button))

    def on_scroll(self, x, y, dx, dy):
        logging.info("Mouse scrolled at ({0}, {1})({2}, {3})".format(x, y, dx, dy))

    def start(self):
        # change listener to self.listener so that it can be accessed in other class methods
        self.MouseListenerContainer = MouseListener(on_click=self.on_click)
        self.MouseListenerContainer.daemon = False  # set it to a non-daemon thread
        self.MouseListenerContainer.start()

        self.KeyboardListenerContainer = KeyboardListener(on_press=self.on_press)
        self.KeyboardListenerContainer.daemon = False  # set it to a non-daemon thread
        self.KeyboardListenerContainer.start()

    def stop(self):
        self.MouseListenerContainer.stop()
        self.KeyboardListenerContainer.stop()
        exit()


if __name__ == "__main__":
    INPUTS = InputListener()
    INPUTS.start()
    print("hamdog")
