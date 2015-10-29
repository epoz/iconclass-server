from django import template
register = template.Library()

@register.filter(name='text_lan')
def text_lan(n_obj, language):
    t = n_obj.get('txt', {}).get(language, '&nbsp;')
    return t


@register.filter(name='kw_lan')
def kw_lan(n_obj, language):
    k = n_obj.get('kw', {}).get(language, [])
    return k