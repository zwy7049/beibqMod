#coding:utf-8
from flask import Blueprint
admin = Blueprint("admin", __name__)

import app.admin.views

from app.models import site


from app.models.role import Permission


@admin.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

