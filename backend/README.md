# kibasumba backend

Django + DRF backend for the kibasumba maternal health app.

## Sprint 3.5 — fresh database required

Sprint 3.5 replaced the `Mother` user model with `accounts.CustomUser`
(adds `role`: woman / midwife / chw / admin). Because `AUTH_USER_MODEL`
changed, all migrations were regenerated and `db.sqlite3` was deleted and
recreated. **No production data was lost — the app had no production data
at this stage.**

If you pull this change onto a machine with an old database:

```
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser   # phone number + password; role becomes "admin"
```

Dev superuser created during the sprint: phone `0799999999`, password
`admin123` (change for anything beyond local development).

## Running

```
python manage.py runserver
```

## One-time setup for the Ifishi PDF (Sprint 5)

```
pip install reportlab cairosvg requests
python manage.py download_assets   # saves static/coat_of_arms.png
```

`download_assets` renders the Rwanda coat of arms from Wikimedia. On
Windows, where cairo's native library is usually missing, it automatically
falls back to Wikimedia's own PNG rendering — same image either way.

SMS delivery is configured in `.env` (`SMS_BACKEND=twilio|console`) — see
`accounts/sms.py`.
