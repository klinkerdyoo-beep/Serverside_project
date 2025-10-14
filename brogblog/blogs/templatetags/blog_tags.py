from django import template
from tags.models import Category, Tag
from blogs.models import Blog

register = template.Library()

@register.inclusion_tag('partials/navbar_categories.html')
def navbar_categories():
    categories = Category.objects.all()
    return {'categories': categories}

@register.inclusion_tag('partials/navbar_search.html', takes_context=True)
def navbar_search(context):
    request = context['request']
    search_query = request.GET.get('search', '').strip() if request else ''


    if search_query:
        print(f"🔍 Search query: {search_query}")
    else:
        print("🔍 No search query provided.")
        
    categories = []
    blogs = []
    tags = []
    

    if search_query:
        categories = Category.objects.filter(name__icontains=search_query)
        blogs = Blog.objects.filter(header__icontains=search_query)
        tags = Tag.objects.filter(name__icontains=search_query)
    
    return {
        'search_query': search_query,
        'categories': categories,
        'blogs': blogs,
        'tags' : tags,
    }
