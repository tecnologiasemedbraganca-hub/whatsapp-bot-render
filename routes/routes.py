from flask import Blueprint
from controllers.webhook_controller import webhook

routes = Blueprint("routes", __name__)

routes.add_url_rule("/webhook", view_func=webhook, methods=["GET","POST"])
