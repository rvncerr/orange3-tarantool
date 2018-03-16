from Orange.data import Domain, Table, ContinuousVariable
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets import widget, gui

import concurrent.futures
from Orange.widgets.utils.concurrent import (
    ThreadExecutor, FutureWatcher, methodinvoke
)

from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import numpy as np
import tarantool
import threading
import time


class TimerWidget(OWWidget):
    name = "Timer Trigger"
    category = "Tarantool"
    description = "Just a Timer."
    icon = "icons/timer.svg"
    want_main_area = False
    priority = 10000

    delay = Setting(60)
    current = 0

    _trigger_value = True

    class Error(OWWidget.Error):
        error = widget.Msg("{}")

    class Outputs:
        trigger = Output('Trigger', bool)

    @pyqtSlot()
    def _thread_tick(self):
        self.progressBarSet(100 * self.current / self.delay)

    @pyqtSlot()
    def _thread_trigger(self):
            self.Outputs.trigger.send(self._trigger_value)

    def _thread_func(self):
        _thread_tick = methodinvoke(self, "_thread_tick", ())
        _thread_trigger = methodinvoke(self, "_thread_trigger", ())
        while True:
            _thread_tick(self)
            time.sleep(1)
            self.current = self.current + 1
            if self.current >= self.delay:
                _thread_trigger(self)
                self._trigger_value = not self._trigger_value
                self.current = 0

    def __init__(self):
        super().__init__()

        #self.progress = gui.ProgressBar(self, 1)
        self.progressBarInit()
        delay_hslider = gui.hSlider(self.controlArea, self, 'delay', minValue=1, maxValue=60)

        self.thread = threading.Thread(target=self._thread_func)
        self.thread.daemon = True
        self.thread.start()
