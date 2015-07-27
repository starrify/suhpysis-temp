# coding: utf8
"""suhpysis-temp"""

import sys
assert sys.version_info.major == 2  # For now for Python 2 only

import wx
import pyscreenshot
import numpy
import matplotlib.pyplot
import matplotlib.widgets
import pytesseract

import RectangleSelectorPanel


__copyright__ = 'Pengyu Chen (pengyu[at]libstarrify.so)'
__version__ = ''
__status__ = 'development'


BORDER_0 = 2
BORDER_1 = 5


class Selection(object):
    """Class for selections."""

    def __init__(self, parent, default_var_id=0):
        """Initializes the class."""
        self.rect = None
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        var_name = 'var%d' % default_var_id
        self.tc_name = wx.TextCtrl(parent, value=var_name, size=(48, -1))
        self.hbox.Add(self.tc_name, flag=wx.LEFT | wx.EXPAND, border=BORDER_1)
        btn = wx.Button(parent, style=wx.BU_EXACTFIT, label='Pick')
        btn.Bind(wx.EVT_BUTTON, self.pick_rect)
        self.hbox.Add(btn, flag=wx.LEFT, border=BORDER_1)
        self.st_value = wx.StaticText(parent, label='None')
        self.hbox.Add(
            self.st_value,
            flag=wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT,
            border=BORDER_1
        )

    def pick_rect(self, event):
        """Picks an rectangle"""
        screen_img = pyscreenshot.grab()
        self.fig = matplotlib.pyplot.figure()
        self.sub_plt = self.fig.add_subplot(1, 1, 1)
        arr = numpy.asarray(screen_img)
        plt_image = matplotlib.pyplot.imshow(arr)
        rect_selector = matplotlib.widgets.RectangleSelector(
            self.sub_plt,
            self.pick_callback,
            rectprops={
                'facecolor': 'red',
                'edgecolor': 'black',
                'alpha': 0.5,
            }
        )
        matplotlib.pyplot.show()

    def pick_callback(self, event_click, event_release):
        """Invokes when a rectangle picked."""
        x_range = sorted((event_click.xdata, event_release.xdata))
        y_range = sorted((event_click.ydata, event_release.ydata))
        self.sub_plt.set_xlim(*x_range)
        self.sub_plt.set_ylim(*y_range[::-1])
        self.rect = [int(x) for x in x_range + y_range]
        self.fig.canvas.draw()


class Formula(object):
    """Class for formulas."""

    def __init__(self, parent):
        """Initializes the class."""
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_template = wx.TextCtrl(parent, size=(128, -1))
        self.hbox.Add(
            self.tc_template, flag=wx.LEFT | wx.EXPAND, border=BORDER_1)
        self.st_value = wx.StaticText(parent, label='None')
        self.hbox.Add(
            self.st_value,
            flag=wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT,
            border=BORDER_1
        )


class SuhpysisFrame(wx.Frame):
    """The Suhpysis main frame"""

    def __init__(self, *args, **kwargs):
        """Initializes the class."""
        super(type(self), self).__init__(*args, **kwargs)
        self.selections = []
        self.formulas = []
        self.init_UI()
        self.Show(True)

    def init_UI(self):
        """Initializes the UI."""
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)

        selection_box = wx.StaticBox(
            self, label='Selections', style=wx.ALIGN_CENTRE)
        self.selection_vbox = wx.StaticBoxSizer(selection_box, wx.VERTICAL)
        self.vbox.Add(
            self.selection_vbox, flag=wx.EXPAND | wx.ALL, border=BORDER_0)

        formula_box = wx.StaticBox(
            self, label='Formulas', style=wx.ALIGN_CENTRE)
        self.formula_vbox = wx.StaticBoxSizer(formula_box, wx.VERTICAL)
        self.vbox.Add(
            self.formula_vbox, flag=wx.EXPAND | wx.ALL, border=BORDER_0)

        btn = wx.Button(self, style=wx.BU_EXACTFIT, label='Add')
        btn.Bind(wx.EVT_BUTTON, self.add_selection)
        self.selection_vbox.Add(
            btn, flag=wx.ALIGN_CENTRE | wx.ALL, border=BORDER_0 * 2)
        btn = wx.Button(self, style=wx.BU_EXACTFIT, label='Add')
        btn.Bind(wx.EVT_BUTTON, self.add_formula)
        self.formula_vbox.Add(
            btn, flag=wx.ALIGN_CENTRE | wx.ALL, border=BORDER_0 * 2)

        self.vbox.Layout()
        self.vbox.Fit(self)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.timer.Start(1000)

    def add_selection(self, event):
        """Adds a selection."""
        selection = Selection(self, len(self.selections) + 1)
        self.selections.append(selection)
        self.selection_vbox.Add(
            selection.hbox, flag=wx.EXPAND | wx.ALL, border=BORDER_0)
        self.vbox.Layout()
        self.vbox.Fit(self)

    def add_formula(self, event):
        """Adds a formula."""
        formula = Formula(self)
        self.formulas.append(formula)
        self.formula_vbox.Add(
            formula.hbox, flag=wx.EXPAND | wx.ALL, border=BORDER_0)
        self.vbox.Layout()
        self.vbox.Fit(self)

    def on_timer(self, event):
        """Callback on timer."""
        if self.selections and any(x.rect for x in self.selections):
            screen_img = pyscreenshot.grab()
            data = {}
            for selection in self.selections:
                if selection.rect:
                    x0, x1, y0, y1 = selection.rect
                    img = screen_img.crop((x0, y0, x1, y1))
                    text = pytesseract.image_to_string(img)
                    if not text:
                        text = 'None'
                    selection.st_value.SetLabel(text)
                    name = selection.tc_name.GetValue()
                    data[name] = text
            for formula in self.formulas:
                template = formula.tc_template.GetValue()
                if template:
                    try:
                        raw = template.format(**data)
                        result = str(eval(raw))
                    except:
                        result = 'None'
                    formula.st_value.SetLabel(result)

        self.vbox.Layout()
        self.vbox.Fit(self)


def main():
    """The main entry."""
    app = wx.App(False)
    frame = SuhpysisFrame(None, title='Jarry Test')
    app.MainLoop()


if __name__ == '__main__':
    main()
