# OlimpHub – full Django prototype (no Docker)

## Quick start

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install django==5.0.*
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`

* Admin: `/admin/`
* Auth routes: `/accounts/login/`, `/accounts/logout/`
* Sign‑up: `/signup/`
