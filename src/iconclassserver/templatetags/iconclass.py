from django import template
register = template.Library()

@register.filter(name='text_lan')
def text_lan(n_obj, language):
    if not n_obj: return u''
    t = n_obj.get('txt', {}).get(language, u'')
    return t


@register.filter(name='kw_lan')
def kw_lan(n_obj, language):
    if not n_obj: return u''
    k = n_obj.get('kw', {}).get(language, [])
    return k