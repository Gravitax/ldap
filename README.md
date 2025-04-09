faire un venv

pip install backend/requirements.txt

uvicorn backend.main:app --host 127.0.0.1 --port 8000

----------

users:

admin - admin

test - test (aucun droit)

----------

Au login le back renvoit un token qui est set dans une variable JS si la connection est OK

à chaque fetch le token est transmit et l'api vérifie si il est OK avant de répondre
