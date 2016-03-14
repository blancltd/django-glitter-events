# -*- coding: utf-8 -*-

import calendar
import datetime
from collections import OrderedDict

from django.utils import timezone
from django.views.generic.dates import MonthArchiveView

from .models import Category, Event


class EventsMixin(object):
    def get_context_data(self, **kwargs):
        context = super(EventsMixin, self).get_context_data(**kwargs)
        context['events_categories'] = True
        context['categories'] = Category.objects.all()
        return context


class EventsQuerysetMixin(object):
    model = Event
    queryset = Event.objects.published()


class CalendarMixin(EventsQuerysetMixin, MonthArchiveView):
    allow_future = True
    allow_empty = True
    year_format = '%Y'
    month_format = '%m'
    date_field = 'date_url'

    def get_time_now(self):
        return timezone.now()

    def get_current_month(self):
        if 'month' in self.kwargs:
            if self.get_year() and self.get_month():
                date = datetime.date(int(self.get_year()), int(self.get_month()), 1)
        else:
            date = self.get_time_now().replace(day=1)
        return date

    def get_context_data(self, **kwargs):
        context = super(CalendarMixin, self).get_context_data(**kwargs)

        current_month = self.get_current_month()
        now = self.get_time_now()
        current_month = self.get_current_month()
        previous_month = self.get_previous_month(current_month)
        next_month = self.get_next_month(current_month)

        context['calendar_headings'] = self.get_calendar_day_names()
        context['event_list'] = self.get_events_list()
        context['now_month'] = now
        context['previous_month'] = previous_month
        context['next_month'] = next_month
        context['current_month'] = current_month
        context['total_events'] = self.get_month_total_events_no()

        return context

    def get_events_list(self):
        current_month = self.get_current_month()
        next_month = self.get_next_month(current_month)

        month_days = OrderedDict()

        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        for week in cal.monthdatescalendar(current_month.year, current_month.month):
            for i in week:
                month_days[i] = []

        # Get queryset from Mixin
        qs = self.get_queryset()

        qs = qs.filter(start__gte=current_month, start__lte=next_month)

        for i in qs:
            event_date = i.start.date()
            month_days[event_date].append(i)

        return month_days.items()

    def get_month_total_events_no(self):
        current_month = self.get_current_month()
        next_month = self.get_next_month(current_month)

        # QuerySet from mixin
        qs = self.get_queryset()
        return qs.filter(start__gte=current_month, start__lte=next_month).count()

    def get_calendar_day_names(self):
        calendar_days = []
        day_names = list(calendar.day_name)
        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)

        for i in cal.iterweekdays():
            calendar_days.append(day_names[i])

        return calendar_days
