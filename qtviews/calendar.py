##############################################################################
#       Copyright (C) 2012, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy import PBTableModel, ModelColumn, Signal, Slot
from qtalchemy.widgets import TableView
from PyQt4 import QtCore, QtGui
import datetime

day_names = "Sunday Monday Tuesday Wednesday Thursday Friday Saturday".split(' ')


class EventWrapper(object):
    """
    Structure for managing the individual items in a calendar view.  Note that
    the calendar has no more granularity than the day.

    These objects are likely created by the :class:`CalendarView`

    :param obj:  The object or some key of what is being represented in the calendar
    :param start_date:  The first date which the item should appear on the calendar
    :param end_date:  The last date for which the item should appear in the calendar
    :param text:  The text that should be shown on the calendar
    :param bkcolor:  something representing the background color of this item in
        the calendar
    """
    def __init__(self, obj, start_date, end_date, text, bkcolor):
        self.obj = obj
        self.start_date = start_date
        self.end_date = end_date
        self.text = text
        self.bkcolor = bkcolor


class CalendarRow(object):
    def __init__(self, day0_date, entries):
        assert len(entries) == 7, "We make a big assumption here that you have 7 days/week"
        self.day0_date = day0_date
        self.entries_by_day = entries
        for d in range(7):
            setattr(self,"day{0}".format(d),"{0}".format(self.day0_date + datetime.timedelta(d)))

    def entryList(self, index):
        """
        :param index: is a QModelIndex and the return is a list of entries on
            this day.
        """
        return self.entries_by_day[index.column()]

    def entryBlock(self, entry, index, indexRect):
        this_day = self.date(index)
        r = indexRect
        r.setHeight(18)
        if entry.start_date == this_day and entry.end_date == this_day:
            end_deflate = lambda x: x.adjusted(3, 0, -3, 0)
        elif entry.start_date == this_day:
            end_deflate = lambda x: x.adjusted(3, 0, 3, 0)
        elif entry.end_date == this_day:
            end_deflate = lambda x: x.adjusted(-3, 0, -3, 0)
        else:
            end_deflate = lambda x: x
        return end_deflate(r.translated(0, 20*(entry.visual_row_level+1)))

    def date(self, index):
        """
        :param index: is a QModelIndex and the return is the date of this cell
        """
        return self.day0_date + datetime.timedelta(index.column())


def GetContrastingTextColor(c):
    return QtGui.QColor("lightGray") if (max([c.red(), c.green(), c.blue()]) >=
            128) else QtGui.QColor("black")

class CalendarDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)
        
        style = QtGui.QApplication.style() if options.widget is None else options.widget.style()

        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter);

        painter.save()
        painter.translate(options.rect.topLeft())
        painter.setClipRect(options.rect.translated(-options.rect.topLeft()))
        
        this_day = index.internalPointer().date(index)

        #entry_back_color = options.palette.color(QtGui.QPalette.Highlight)

        deflated = lambda x: x.adjusted(2, 1, -2, -1)
        r = options.rect.translated(-options.rect.topLeft())
        r.setHeight(18)
        painter.drawText(deflated(r), 0, this_day.strftime("%b %d"))
        for entry in index.internalPointer().entryList(index):
            entry_back_color = entry.bkcolor
            entry_front_color = GetContrastingTextColor(entry_back_color)

            eventRect = index.internalPointer().entryBlock(entry, index,
                    options.rect.translated(-options.rect.topLeft()))

            painter.setBrush(QtGui.QBrush(entry.bkcolor))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(eventRect)
            if entry.start_date == this_day or this_day.weekday() == 6:
                painter.setPen(QtGui.QPen(entry_front_color))
                painter.drawText(deflated(eventRect), 0, entry.text)

        painter.restore()


class CalendarView(TableView):
    """


    >>> app = initQtapp()
    >>> c = CalendarView()
    >>> c.setDateRange(datetime.date(2012, 3, 18), 6)
    >>> c.setEventList([
    ...     {"start": datetime.date(2012, 3, 21), "end": datetime.date(2012, 3, 25), "text": "vacation"}, 
    ...     {"start": datetime.date(2012, 3, 28), "end": datetime.date(2012, 4, 4), "text": "nicer vacation"}, 
    ...     {"start": datetime.date(2012, 4, 9), "end": datetime.date(2012, 4, 9), "text": "wife birthday"}],
    ...     startDate = lambda x: x["start"],
    ...     endDate = lambda x: x["end"],
    ...     text = lambda x: x["text"],
    ...     bkColor = lambda x: QtGui.QColor(0, 0, 0))
    """
    doubleClickCalendarEvent = Signal(object)
    contextMenuCalendarEvent = Signal(QtCore.QPoint, object)

    def __init__(self, parent=None):
        TableView.__init__(self, parent)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setItemDelegate(CalendarDelegate(self))
        self.verticalHeader().setDefaultSectionSize(80)
        self.firstDate = None
        self.numWeeks = None

    def setDateRange(self, firstDate, numWeeks):
        self.firstDate = firstDate
        self.numWeeks = numWeeks

    def setEventList(self, events, startDate, endDate, text, bkColor):
        events = [EventWrapper(e, startDate(e), endDate(e), text(e), bkColor(e)) 
                        for e in events]

        rows = []
        for i in range(self.numWeeks):
            day0 = self.firstDate + datetime.timedelta(i*7)
            day6 = self.firstDate + datetime.timedelta(i*7+6)

            calWeek = []
            for i in range(7):
                d = day0 + datetime.timedelta(i)
                calWeek.append([e for e in events if e.start_date <= d and e.end_date >= d])
                zz = 0
                for x in calWeek[-1]:
                    x.visual_row_level = zz
                    zz += 1

            rows.append(CalendarRow(day0, calWeek))

        self.rows = PBTableModel(columns=[ModelColumn("day{0}".format(d),str,day_names[d]) for d in range(7)])
        self.setModel(self.rows)
        self.rows.reset_content_from_list(rows)

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index is not None and index.isValid():
            for entry in index.internalPointer().entryList(index):
                eventRect = index.internalPointer().entryBlock(entry, index, self.visualRect(index))
                if eventRect.contains(event.pos()):
                    self.doubleClickCalendarEvent.emit(entry.obj)
                    event.accept()
                    break
        TableView.mouseDoubleClickEvent(self, event)

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        if index is not None and index.isValid():
            for entry in index.internalPointer().entryList(index):
                eventRect = index.internalPointer().entryBlock(entry, index, self.visualRect(index))
                if eventRect.contains(event.pos()):
                    self.contextMenuCalendarEvent.emit(event.pos(), entry.obj)
                    event.accept()
                    break
        TableView.contextMenuEvent(self, event)
