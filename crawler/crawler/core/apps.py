# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from material.frontend.apps import ModuleMixin

class CoreConfig(ModuleMixin, AppConfig):
    name = 'crawler.core'
    icon = '<i class="material-icons">archive</i>'
    verbose_name = _("Crawler")
