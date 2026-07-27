from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

STYLES = ["style1", "style2", "style3", "style4", "style5", "style6", "style7",
          "style8", "style9", "birthday"]

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main builder (index.html) at the site root, its API at /api/gift...
    path('', include('classic.urls')),
    path('api/', include('classic.urls_api')),
]

for slug in STYLES:
    urlpatterns += [
        path(f'{slug}/', include((f'{slug}.urls', slug), namespace=slug)),
        path(f'{slug}.html', include((f'{slug}.urls', slug), namespace=slug)),
        path(f'api/{slug}/', include((f'{slug}.urls_api', f'{slug}_api'), namespace=f'{slug}_api')),
    ]

# Add numeric .html patterns for styles
for i in range(1, 10):
    slug = f'style{i}'
    urlpatterns += [
        path(f'{i}.html', include((f'{slug}.urls', slug), namespace=slug)),
    ]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)