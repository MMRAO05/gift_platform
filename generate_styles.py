"""
One-time generator: builds models.py / forms.py / admin.py / views.py / urls.py
for every style app, and patches each source HTML file with:
  1) a small "bridge" snippet (inserted just before the final </script>,
     so it shares scope with the page's own `state` variable) that also
     saves the gift to the Django backend and swaps the share link for a
     short backend-served one.
  2) a tiny seed/redirect template used by the reveal ("/g/<uuid>/") URL,
     which re-uses each page's OWN existing load mechanism (?data=, #hash,
     or ?id=+localStorage / window.__PRESET__) so ZERO animation/style
     code is touched.
Run once with: python3 generate_styles.py
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "templates_src")

STYLES = {
    "style1": dict(file="1.html", type="query", param="data", create_btn=["btnCreateLink", "createLinkBtn"]),
    "style2": dict(file="2.html", type="query", param="data", create_btn=["btnCreateLink", "createLinkBtn"]),
    "style3": dict(file="3.html", type="hash", create_btn=["btnCreateLink", "createLinkBtn"]),
    "style4": dict(file="4.html", type="hash", create_btn=["createLinkBtn", "btnCreateLink"]),
    "style5": dict(file="5.html", type="localstorage", prefix="aurora_v5_", create_btn=["createLinkBtn", "btnCreateLink"]),
    "style6": dict(file="6.html", type="localstorage", prefix="nexus_v6_", create_btn=["createLinkBtn", "btnCreateLink"]),
    "style7": dict(file="7.html", type="localstorage", prefix="love_question_v4_", create_btn=["btnCreateLink", "createLinkBtn"]),
    "style8": dict(file="8.html", type="localstorage", prefix="eclipse_v7_", create_btn=["createLinkBtn", "btnCreateLink"]),
    "style9": dict(file="9.html", type="localstorage", prefix="surprise_v16_", create_btn=["btnCreateLink", "createLinkBtn"]),
    "birthday": dict(file="birthday.html", type="preset", create_btn=["btnCreateLink"]),
}

MODELS_TPL = '''from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "{slug}" template ({source_file})."""

    class Meta:
        verbose_name = "{title} Gift"
        verbose_name_plural = "{title} Gifts"
'''

FORMS_TPL = '''from django import forms
from .models import Gift


class GiftForm(forms.ModelForm):
    """Used by the admin / any server-rendered fallback form for {slug}."""

    class Meta:
        model = Gift
        fields = ["sender_name", "recipient_name", "passkey", "data", "expires_at", "is_active"]
'''

ADMIN_TPL = '''from django.contrib import admin
from .models import Gift


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient_name", "sender_name", "created_at", "expires_at", "view_count", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("id", "recipient_name", "sender_name")
    readonly_fields = ("id", "created_at", "view_count")
'''

VIEWS_TPL = '''from django.shortcuts import render
from django.views import View
from core.generic_views import BaseSaveGiftAPIView
from .models import Gift

STYLE_SLUG = "{slug}"


class CreatePageView(View):
    """Serves the original {source_file} page unchanged (setup + reveal
    in one template, exactly like the source file)."""

    def get(self, request):
        return render(request, "{slug}/page.html")


class SaveGiftAPIView(BaseSaveGiftAPIView):
    model = Gift
    style_slug = STYLE_SLUG


class RevealSeedView(View):
    """/{slug}/g/<uuid>/  — looks the gift up, then serves a tiny page
    that re-creates the EXACT url format ({load_type}) the original page
    already knows how to load from, so the real page code (unchanged)
    takes it from there."""

    def get(self, request, gift_id):
        from django.shortcuts import get_object_or_404
        from django.http import Http404
        gift = get_object_or_404(Gift, pk=gift_id)
        if gift.is_expired or not gift.is_active:
            raise Http404("This gift link has expired.")
        gift.register_view()
        return render(request, "{slug}/seed_redirect.html", {{
            "gift_json": gift.data,
            "gift_id": str(gift.id),
        }})
'''

URLS_TPL = '''from django.urls import path
from . import views

app_name = "{slug}"

urlpatterns = [
    path("", views.CreatePageView.as_view(), name="create"),
    path("g/<uuid:gift_id>/", views.RevealSeedView.as_view(), name="reveal"),
]

api_urlpatterns = [
    path("save/", views.SaveGiftAPIView.as_view(), name="save"),
]
'''


def bridge_snippet(slug, cfg):
    btn_ids = ", ".join(f"'{b}'" for b in cfg["create_btn"])
    return f"""
  // ── Django backend bridge (auto-added) ──────────────────────────────
  (function() {{
    var STYLE_SLUG = '{slug}';
    var btnIds = [{btn_ids}];
    var btn = null;
    for (var i = 0; i < btnIds.length; i++) {{
      btn = document.getElementById(btnIds[i]);
      if (btn) break;
    }}
    if (!btn) return;
    btn.addEventListener('click', function() {{
      setTimeout(function() {{
        try {{
          if (typeof state === 'undefined') return;
          fetch('/api/' + STYLE_SLUG + '/save/', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(state)
          }}).then(function(r) {{ return r.json(); }}).then(function(data) {{
            if (data && data.id) {{
              var input = document.getElementById('shareLinkInput');
              if (input) input.value = window.location.origin + '/' + STYLE_SLUG + '/g/' + data.id + '/';
            }}
          }}).catch(function(e) {{ console.warn('Backend save failed, using local link.', e); }});
        }} catch (e) {{ console.warn('Backend bridge error', e); }}
      }}, 350);
    }});
  }})();
"""


def make_seed_redirect(slug, cfg):
    if cfg["type"] == "query":
        param = cfg["param"]
        body = f"""<script>
  var GIFT = {{{{ gift_json|safe }}}};
  var target = '/{slug}/?{param}=' + encodeURIComponent(JSON.stringify(GIFT));
  window.location.replace(target);
</script>"""
    elif cfg["type"] == "hash":
        body = f"""<script>
  var GIFT = {{{{ gift_json|safe }}}};
  var target = '/{slug}/#' + encodeURIComponent(JSON.stringify(GIFT));
  window.location.replace(target);
</script>"""
    elif cfg["type"] == "localstorage":
        prefix = cfg["prefix"]
        body = f"""<script>
  var GIFT = {{{{ gift_json|safe }}}};
  var GID = "{{{{ gift_id }}}}";
  try {{
    localStorage.setItem('{prefix}' + GID, JSON.stringify(GIFT));
    var idsKey = '{prefix}ids';
    var ids = [];
    try {{ ids = JSON.parse(localStorage.getItem(idsKey) || '[]'); }} catch (e) {{}}
    if (ids.indexOf(GID) === -1) ids.push(GID);
    localStorage.setItem(idsKey, JSON.stringify(ids));
  }} catch (e) {{}}
  window.location.replace('/{slug}/?id=' + GID);
</script>"""
    elif cfg["type"] == "preset":
        body = f"""<style>#scr-setup{{display:none !important;}}</style>
<script>window.__PRESET__ = {{{{ gift_json|safe }}}};</script>
<script>window.location.replace('/{slug}/?gift=' + "{{{{ gift_id }}}}");</script>"""
    else:
        raise ValueError(cfg["type"])
    return f"<!DOCTYPE html>\n<html><head><meta charset='UTF-8'></head><body>\n{body}\n</body></html>\n"


def patch_html(slug, cfg):
    src_path = os.path.join(SRC, cfg["file"])
    with open(src_path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    idx = html.rfind("</script>")
    if idx == -1:
        raise RuntimeError(f"No </script> found in {cfg['file']}")
    snippet = bridge_snippet(slug, cfg)
    patched = html[:idx] + snippet + html[idx:]
    return patched


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    for slug, cfg in STYLES.items():
        app_dir = os.path.join(BASE, slug)
        title = slug.replace("_", " ").title()

        write(os.path.join(app_dir, "models.py"), MODELS_TPL.format(slug=slug, title=title, source_file=cfg["file"]))
        write(os.path.join(app_dir, "forms.py"), FORMS_TPL.format(slug=slug))
        write(os.path.join(app_dir, "admin.py"), ADMIN_TPL.format(slug=slug))
        write(os.path.join(app_dir, "views.py"), VIEWS_TPL.format(slug=slug, source_file=cfg["file"], load_type=cfg["type"]))
        write(os.path.join(app_dir, "urls.py"), URLS_TPL.format(slug=slug))

        patched_html = patch_html(slug, cfg)
        write(os.path.join(app_dir, "templates", slug, "page.html"), patched_html)
        write(os.path.join(app_dir, "templates", slug, "seed_redirect.html"), make_seed_redirect(slug, cfg))

        print(f"✔ generated {slug} ({cfg['file']}, type={cfg['type']})")


if __name__ == "__main__":
    main()
