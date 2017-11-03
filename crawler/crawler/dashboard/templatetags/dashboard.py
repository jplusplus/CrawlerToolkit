from importlib import import_module
from django.conf import settings
from django.template import Library

register = Library()

def get_admin_site():
    site_module = getattr(
        settings,
        'MATERIAL_ADMIN_SITE',
        'django.contrib.admin.site'
    )
    mod, inst = site_module.rsplit('.', 1)
    mod = import_module(mod)
    return getattr(mod, inst)

site = get_admin_site()

@register.assignment_tag
def get_dashboard_app_list(request):
    blocks = list()
    for model, model_admin in site._registry.items():
        block_dict = dict()
        block_template = getattr(model_admin, 'dashboard_template')
        block_title = getattr(model_admin, 'dashboard_title')
        if block_tile:
            block_dict['template'] = block_template

        if block_template:
            block_dict['template'] = block_template
            # only add the block if it has a template
            blocks.append(block_dict)
    return blocks;



