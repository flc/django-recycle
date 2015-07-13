def get_obj_closest_to(qs, field, target):
    """
    Return the closest object by the specified datetime field
    in the given queryset.

    :param qs: queryset to filter against
    :param field: name of the datetime field
    :param target: target timestamp (datetime object)
    """
    closest_greater_qs = qs.filter(
        **{'{}__gte'.format(field): target}
        ).order_by(field)
    closest_less_qs = qs.filter(
        **{'{}__lte'.format(field): target}
        ).order_by('-{}'.format(field))

    try:
        try:
            closest_greater = closest_greater_qs[0]
        except IndexError:
            return closest_less_qs[0]

        try:
            closest_less = closest_less_qs[0]
        except IndexError:
            return closest_greater_qs[0]
    except IndexError:
        raise qs.model.DoesNotExist(
            "There is no closest object because there aren't any objects."
            )

    if getattr(closest_greater, field) - target > target - getattr(closest_less, field):
        return closest_less
    return closest_greater
