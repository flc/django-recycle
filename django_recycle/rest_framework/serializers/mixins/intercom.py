import hmac
import hashlib

from django.conf import settings

from rest_framework import serializers


class IntercomUserHashMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(settings, "INTERCOM_SECURE_KEY", None):
            self.fields['intercom_user_hash'] = serializers.SerializerMethodField('_get_intercom_user_hash')

    def _get_intercom_user_hash(self, obj):
        secure_key = getattr(settings, "INTERCOM_SECURE_KEY", None)
        if not secure_key:
            return None

        hmac_value = str(obj.id) if obj.id else str(obj.email)
        try:
            user_hash = hmac.new(secure_key, hmac_value, digestmod=hashlib.sha256).hexdigest()
        except TypeError:
            # in Python3: TypeError: key: expected bytes or bytearray, but got 'str'
            user_hash = hmac.new(
                bytes(secure_key, 'utf-8'), bytes(hmac_value, 'utf-8'), digestmod=hashlib.sha256
            ).hexdigest()
        return user_hash
