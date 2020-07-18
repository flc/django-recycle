import tempfile

from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext

import pdfkit


def render_to_pdf_pdfkit(request, template_name, context, filename, extra_options=None):
    template = get_template(template_name)
    html = template.render(context, request=request)

    tmp_file = tempfile.NamedTemporaryFile(prefix='pdf_output_{}')
    options = {
        'encoding': 'UTF-8',
        'footer-right': 'Page [page] of [toPage]',
        'margin-top': '0.5cm',
        'margin-right': '0.5cm',
        'margin-bottom': '0.5cm',
        'margin-left': '0.5cm',
        # 'footer-spacing': '-0.2',
    }
    extra_options = extra_options or {}
    options.update(extra_options)

    pdfkit.from_string(html, tmp_file.name, options=options)
    tmp_file.seek(0)
    pdf = tmp_file.read()

    response = HttpResponse(content_type='application/pdf')
    response.write(pdf)
    if filename is not None:
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response
