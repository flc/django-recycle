from django.db.models import FloatField


class RealField(FloatField):
    """PostgreSQL real field.
    real | 4 bytes | variable-precision, inexact | 6 decimal digits precision
    """

    def db_type(self, connection):
        if 'postgresql' in connection.settings_dict['ENGINE']:
            return 'real'
        return super(RealField, self).db_type(connection)
