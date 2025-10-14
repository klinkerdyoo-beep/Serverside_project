from django import template
from blogs.models import Category

register = template.Library()

@register.inclusion_tag('./partials/navbar.html')
def navbar_categories():
    categories = Category.objects.all()
    return {'categories': categories}
