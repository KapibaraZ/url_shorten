pip install -r requirements.txt

in root
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python main.py
