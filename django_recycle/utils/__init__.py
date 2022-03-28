try:
    from django.utils.encoding import force_unicode as force_str
except ImportError:
    # Python 3 / Django 2
    try:
        from django.utils.encoding import force_str as force_str
    except ImportError:
        from django.utils.encoding import force_str


def get_choice_display(choices, choice):
    """
    Return the display value of a choices 2-tuple.

    >> A = 1
    >> B = 2
    >> CHOICES = ((A, _("A")), (B, _("B")),)
    >> get_choice_display(CHOICES, A)
    u'A'
    """
    return force_str(dict(choices).get(choice), strings_only=True)


def copy_qdict(qdict, exclude=None):
    if exclude is None:
        exclude = ['csrfmiddlewaretoken']
    new = qdict.copy()
    for e in exclude:
        try:
            del new[e]
        except KeyError:
            continue
    return new


def add_query_extra_item(query_extras, query_extra):
    if query_extra:
        if 'select' in query_extra:
            query_extras['select'].extend(
                list(query_extra['select'].items())
                )
        if 'select_params' in query_extra:
            query_extras['select_params'].extend(
                query_extra['select_params']
                )
    return query_extras
