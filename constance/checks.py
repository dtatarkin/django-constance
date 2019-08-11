from datetime import datetime

from django.core import checks
from django import conf
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from constance.admin import get_values
from . import settings



@checks.register("constance")
def check_fieldsets(*args, **kwargs):
    """
    A Django system check to make sure that, if defined, CONFIG_FIELDSETS accounts for
    every entry in settings.CONFIG.
    """
    if hasattr(settings, "CONFIG_FIELDSETS") and settings.CONFIG_FIELDSETS:
        inconsistent_fieldnames = get_inconsistent_fieldnames()
        if inconsistent_fieldnames:
            return [
                checks.Warning(
                    _(
                        "CONSTANCE_CONFIG_FIELDSETS is missing "
                        "field(s) that exists in CONSTANCE_CONFIG."
                    ),
                    hint=", ".join(sorted(inconsistent_fieldnames)),
                    obj="settings.CONSTANCE_CONFIG",
                    id="constance.E001",
                )
            ]
    return []


@checks.register("constance")
def check_inconsistent_use_tz_setting(*args, **kwargs):
    """
    A Django system check to make sure that, if the `USE_TZ = True` then
    the config CONSTANCE_CONFIG should contain datetimes with timezone and vice versa.
    """
    use_tz = conf.settings.USE_TZ
    check_results = []
    for k, v in get_values().items():
        if isinstance(v, datetime):
            if timezone.is_aware(v) != use_tz:
                if use_tz:
                    check_results.append(checks.Warning(
                        _(
                            "Using naive datetime values while USE_TZ = True"
                        ),
                        hint="Add `tzinfo` to value of the field {}".format(k),
                        obj=v,
                        id="constance.E002",
                    ))
                else:
                    check_results.append(checks.Warning(
                        _(
                            "Using datetime with timezone while USE_TZ = False"
                        ),
                        hint="Remove `tzinfo` from value of the field {}".format(k),
                        obj=v,
                        id="constance.E003",
                    ))
    return check_results


def get_inconsistent_fieldnames():
    """
    Returns a set of keys from settings.CONFIG that are not accounted for in
    settings.CONFIG_FIELDSETS.
    If there are no fieldnames in settings.CONFIG_FIELDSETS, returns an empty set.
    """
    field_name_list = []
    for fieldset_title, fields_list in settings.CONFIG_FIELDSETS.items():
        for field_name in fields_list:
            field_name_list.append(field_name)
    if not field_name_list:
        return {}
    return set(set(settings.CONFIG.keys()) - set(field_name_list))
