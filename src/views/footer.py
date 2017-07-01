from flask import Blueprint, render_template, request
from flask_login import current_user

from shared.util import config, get_logger, log_request

logger = get_logger(__name__)
footer_module = Blueprint('footer', __name__)

def make_page_route(page):
    def route():
        log_request(request, current_user)
        logger.debug('{View|%s}' % page)
        env = {'module': page.capitalize(), 'header': True}
        return render_template('footer/%s.html' % page, **env)
    return route

for page in config['footer-pages']:
    route = make_page_route(page)
    footer_module.add_url_rule('/%s' % page, page, route)
