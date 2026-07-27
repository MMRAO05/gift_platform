# Gift Platform — Django Conversion

Aap ki 11 animated HTML "gift/celebration" templates (1.html–9.html, birthday.html,
index.html) ko is Django project mein convert kiya gaya hai. **Har template ka
CSS/animation/JS bilkul waisa hi rakha gaya hai** — sirf itna add kiya gaya hai
ke ab "Create Link" par jo shareable link banta hai woh **kisi bhi device/browser
se khulta hai**, kyunke data ab real database mein save hota hai (pehle localStorage
ya URL mein embed hota tha, jo sirf usi browser/tab tak mehdood tha).

## Project structure

```
gift_platform/
├── core/            # shared abstract Gift model + generic API views
├── classic/         # index.html — the main builder (already had a real API contract)
├── style1/ … style9/  # 1.html … 9.html — har ek apni alag app
├── birthday/        # birthday.html
└── gift_platform/   # Django project settings/urls
```

Har style app mein (jaisa aap ne maanga tha):
- `models.py`   → apna Gift model (alag table)
- `forms.py`    → ModelForm
- `views.py`    → create page + save API + reveal (shareable link) view
- `admin.py`    → apna admin panel entry
- `urls.py`     → page routes
- `urls_api.py` → `/api/<style>/...` routes
- `templates/<style>/page.html` → original HTML, animation/style 100% same

## URLs

| Style | Create page | API save | Shareable link |
|---|---|---|---|
| classic (index.html) | `/` | `POST /api/gift` | `/?id=<uuid>` |
| style1 (1.html) | `/style1/` | `POST /api/style1/save/` | `/style1/g/<uuid>/` |
| style2 (2.html) | `/style2/` | `POST /api/style2/save/` | `/style2/g/<uuid>/` |
| style3 (3.html) | `/style3/` | `POST /api/style3/save/` | `/style3/g/<uuid>/` |
| style4 (4.html) | `/style4/` | `POST /api/style4/save/` | `/style4/g/<uuid>/` |
| style5 (5.html) | `/style5/` | `POST /api/style5/save/` | `/style5/g/<uuid>/` |
| style6 (6.html) | `/style6/` | `POST /api/style6/save/` | `/style6/g/<uuid>/` |
| style7 (7.html) | `/style7/` | `POST /api/style7/save/` | `/style7/g/<uuid>/` |
| style8 (8.html) | `/style8/` | `POST /api/style8/save/` | `/style8/g/<uuid>/` |
| style9 (9.html) | `/style9/` | `POST /api/style9/save/` | `/style9/g/<uuid>/` |
| birthday | `/birthday/` | `POST /api/birthday/save/` | `/birthday/g/<uuid>/` |

`/admin/` → Django admin (default login: **admin / admin12345** — change this
immediately, see below).

## Kaise chalayen

```bash
cd gift_platform
python3 -m venv venv && source venv/bin/activate
pip install django
python3 manage.py migrate
python3 manage.py runserver
```

Phir browser mein `http://127.0.0.1:8000/` (classic) ya `http://127.0.0.1:8000/style1/`
waghera khol lein.

## Har style kaise kaam karta hai (architecture)

Original files 3 tareeqon se "shareable link" banate thay:

1. **query-param** (1.html, 2.html) — data seedha `?data=...` mein encode hota tha.
2. **hash** (3.html, 4.html) — data `#...` fragment mein encode hota tha.
3. **localStorage** (5–9.html) — sirf `?id=...` URL mein hota tha, actual data
   localStorage mein — is wajah se link sirf usi browser mein khulta tha.
4. **preset export** (birthday.html) — sirf ek standalone HTML file download hoti thi.

Har case mein maine original JS ko chhera nahi — sirf ek chhota "bridge" script
add kiya jo "Create Link" click par data ko Django backend (`/api/<style>/save/`)
per POST kar deta hai aur `shareLinkInput` ki value ko short backend link se replace
kar deta hai. Jab woh link kholi jati hai (`/style<N>/g/<uuid>/`), Django database
se data nikal kar **isi mechanism** (query/hash/localStorage/preset) ko dubara
bana deta hai jo original page pehle se samajhta tha — is liye page ka apna JS
bilkul unchanged rehta hai aur animation/style 100% same rehti hai.

`birthday.html` mein pehle koi shareable-link system tha hi nahi (sirf "Export
HTML" button tha) — is liye ek naya "🔗 Create Shareable Link" button aur share-box
add kiya gaya hai, jo isi backend pattern ko follow karta hai.

## Production ke liye zaroori changes

Ye setup development/testing ke liye ready hai. Live server par daalne se pehle:

1. `settings.py` mein `SECRET_KEY` naya generate karein aur environment variable
   se lein (hardcode na karein).
2. `DEBUG = False` karein aur `ALLOWED_HOSTS` mein apna domain likhein (abhi `['*']`
   hai jo sirf testing ke liye theek hai).
3. `python3 manage.py changepassword admin` chala kar admin ka password badlein
   (ya naya superuser banayein aur purana delete karein).
4. SQLite ki jagah Postgres/MySQL use karein agar traffic zyada expect hai.
5. Photos abhi base64 JSON ke andar store hote hain (jaisa original design tha) —
   agar bohat zyada photos/large images honge to unhe alag `ImageField` +
   media storage (ya S3) mein move karna behtar hoga.
6. `python3 manage.py collectstatic` chalayein agar static files serve karni hon.

## Admin panel

`/admin/` per jaa kar aap har style ke sab bhejay gaye gifts dekh saktay hain —
kis ne kis ko, kab, passkey kya thi, kab expire hoga, kitni baar dekha gaya, waghera.
