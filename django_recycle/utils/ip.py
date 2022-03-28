# borrowed mostly from https://github.com/Gidsy/django-geoip-utils/blob/master/geoip_utils/utils.py
from django.core.exceptions import ImproperlyConfigured


def get_ip_of_request(request, ip_resolver=None):
    """
    Get the IP from the request,
    Other resolvers can be passed.
    """
    if ip_resolver is None:
        ip_resolver = remote_addr_ip
    return ip_resolver(request)


def remote_addr_ip(request):
    """
    This is for the development setup.
    """
    return request.META.get('REMOTE_ADDR') or None


def x_forwarded_ip(request):
    """
    Amazon ELB stores the IP in the HTTP_X_FORWARDED_FOR META attribute.
    It is realiably the first one of the IP adresses sent and can be
    trusted (eg.: cannot be spoofed) Warning: This might not be true for
    other load balancers

    This function assumes that your Nginx is configured with:
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    """
    ip_address_list = request.headers.get('X-Forwarded-For')
    if ip_address_list:
        ip_address_list = ip_address_list.split(',')
        return ip_address_list[0]


def real_ip(request):
    """
    Behind a Wsgi (Nginx) server.
    """
    return request.headers.get('X-Real-Ip') or None
