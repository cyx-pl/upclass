"""Was der Tutor erfährt, wenn im Portal ein Termin abgesagt oder verschoben
oder eine Serie beendet wird.

Die Texte entstehen vor dem Löschen bzw. Ändern, weil die Stunde danach nicht
mehr (so) existiert. Versand: email_service.send_change_notification_portal.
"""

from django.utils import translation
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from apps.lessons.booking_origin import TUTOR, account_phrase

WEEKDAYS = [
    ("monday", "Mo"),
    ("tuesday", "Di"),
    ("wednesday", "Mi"),
    ("thursday", "Do"),
    ("friday", "Fr"),
    ("saturday", "Sa"),
    ("sunday", "So"),
]


def _when(date, time, minutes=None) -> str:
    text = _('{value0}, {value1} Uhr').format(value0=date_format(date, 'D, d.m.Y'), value1=time.strftime('%H:%M'))
    return f"{text} ({minutes} Min.)" if minutes else text


def _actor(portal_user, contract) -> str:
    return _('über das Portal ') + account_phrase(portal_user.user, contract.user_id, TUTOR)


def cancel_notice(session, portal_user) -> dict:
    contract = session.contract
    name = contract.full_name
    with translation.override(translation.get_language()):
        when = _when(session.date, session.start_time, session.duration_minutes)
        return {
            "subject": _('Termin abgesagt: {value0} — {value1}').format(value0=name, value1=session.date.strftime('%d.%m.%Y')),
            "heading": _('Termin abgesagt'),
            "intro": (
                _('Ein Termin von {value0} wurde im Portal abgesagt. Er ist aus deinem Kalender entfernt und steht beim Schüler unter „Im Portal abgesagte Termine“.').format(value0=name)
            ),
            "rows": [
                (_('Schüler'), name),
                (_('Termin'), when),
                (_('Abgesagt'), _actor(portal_user, contract)),
            ],
            "push_title": _('Termin abgesagt: {value0}').format(value0=name),
            "push_body": when,
            "contract_pk": contract.pk,
        }


def reschedule_notice(session, old_date, old_time, portal_user) -> dict:
    """Nach dem Speichern aufrufen: session trägt schon den neuen Termin."""
    contract = session.contract
    name = contract.full_name
    with translation.override(translation.get_language()):
        old = _when(old_date, old_time)
        new = _when(session.date, session.start_time, session.duration_minutes)
        return {
            "subject": _('Termin verschoben: {value0} — {value1}').format(value0=name, value1=session.date.strftime('%d.%m.%Y')),
            "heading": _('Termin verschoben'),
            "intro": _('Ein Termin von {value0} wurde im Portal verschoben.').format(value0=name),
            "rows": [
                (_('Schüler'), name),
                (_('Bisher'), old),
                (_('Neu'), new),
                (_('Verschoben'), _actor(portal_user, contract)),
            ],
            "push_title": _('Termin verschoben: {value0}').format(value0=name),
            "push_body": f"{old} → {new}",
            "contract_pk": contract.pk,
        }


def series_cancel_notice(series, sessions, portal_user) -> dict:
    """sessions: die entfallenden Termine, vor dem Löschen geladen."""
    contract = series.contract
    name = contract.full_name
    days = ", ".join(label for field, label in WEEKDAYS if getattr(series, field))
    with translation.override(translation.get_language()):
        dates = sorted(s.date for s in sessions)
        if dates:
            dropped = _('{value0} ({value1} bis {value2})').format(value0=len(dates), value1=date_format(dates[0], 'd.m.Y'), value2=date_format(dates[-1], 'd.m.Y'))
        else:
            dropped = _('keine')
        pattern = _('{value0}, {value1} Uhr').format(value0=days, value1=series.start_time.strftime('%H:%M'))
        return {
            "subject": _('Serie beendet: {value0}').format(value0=name),
            "heading": _('Serie beendet'),
            "intro": (
                _('Eine Serie von {value0} wurde im Portal beendet. Die kommenden Termine sind aus deinem Kalender entfernt und stehen beim Schüler unter „Im Portal abgesagte Termine“.').format(value0=name)
            ),
            "rows": [
                (_('Schüler'), name),
                (_('Serie'), pattern),
                (_('Entfallene Termine'), dropped),
                (_('Beendet'), _actor(portal_user, contract)),
            ],
            "push_title": _('Serie beendet: {value0}').format(value0=name),
            "push_body": _('{value0} · {value1} Termine entfallen').format(value0=pattern, value1=len(dates)),
            "contract_pk": contract.pk,
        }
