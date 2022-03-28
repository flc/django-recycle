import datetime
from django.utils.translation import gettext as _, ngettext


def date_diff(d, date=False):
    now = datetime.datetime.now()
    delta = now - d

    days = delta.days
    hours = round(delta.seconds / 3600.0, 0)
    minutes = round(delta.seconds / 60.0, 0)
    time_format = '%H:%M'

    if days == 0:
        if hours == 0:
            if minutes > 0:
                return ngettext('1 minute ago', '%(minutes)d minutes ago', minutes) % {'minutes': minutes}
            return _("just now")
        return ngettext('1 hour ago', '%(hours)d hours ago', hours) % {'hours': hours}

    if days == 1:
        if date:
            return _("Yesterday")
        return _("Yesterday, %(time)s") % {'time': d.strftime(time_format)}

    if days > 1 and days <= 3:
        data = {'day': _(d.strftime('%A')), 'time': d.strftime(time_format)}
        if date:
            return _("%(day)s") % data
        return _("%(day)s, %(time)s") % data

    if now.year == d.year:
        data = {'month': _(d.strftime('%B')), 'day': d.day, 'time': d.strftime(time_format)}
        if date:
            return _("%(month)s %(day)d") % data
        return _("%(month)s %(day)d, %(time)s") % data

    data = {'year': d.year, 'month': _(d.strftime('%B')), 'day': d.day, 'time': d.strftime(time_format)}
    if date:
        return _("%(month)s %(day)d, %(year)d") % data
    return _("%(month)s %(day)d, %(year)d, %(time)s") % data


def get_datetime_uid(sep="_"):
    now = datetime.datetime.now()
    return now.isoformat(sep)
