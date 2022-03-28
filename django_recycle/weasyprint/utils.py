import io

from django.http import HttpResponse
from django.template.loader import get_template, render_to_string

import weasyprint

from .url_fetcher import static_file_url_fetcher


def render_to_pdf(
    request,
    template_name,
    context,
    filename=None,
    url_fetcher=static_file_url_fetcher,
):
    template = get_template(template_name)
    html = template.render(context, request=request)
    response = HttpResponse(content_type='application/pdf')
    base_url = request.build_absolute_uri('/')
    weasyprint.HTML(string=html, base_url=base_url, url_fetcher=url_fetcher).write_pdf(response)
    if filename is not None:
        response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def generate_pdf(template_name, context, file_object=None, url_fetcher=static_file_url_fetcher):
    if not file_object:
        file_object = io.BytesIO()
    if not context:
        context = {}
    html = render_to_string(template_name, context)
    weasyprint.HTML(string=html, url_fetcher=url_fetcher).write_pdf(file_object)
    return file_object
