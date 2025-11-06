from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key, 0)
    except Exception:
        return 0

@register.filter
def status_badge_class(percent):
    """
    Mapeia o percentual (int/str) para a mesma paleta de cores usada nas tarefas:
    - 0%      -> vermelho
    - 25%/50% -> amarelo
    - 75%     -> azul
    - 100%    -> verde
    Para valores intermediários, aproxima para o bucket mais próximo acima.
    """
    try:
        p = int(str(percent).replace('%', '').strip())
    except Exception:
        return ''
    buckets = [0, 25, 50, 75, 100]
    nearest = min(buckets, key=lambda b: abs(p - b))
    if nearest == 0:
        return 'status-vermelho'
    if nearest in (25, 50):
        return 'status-amarelo'
    if nearest == 75:
        return 'status-azul'
    if nearest == 100:
        return 'status-verde'
    return ''
