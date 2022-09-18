

# Установка и запуск проекта
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Dimtiv/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

>для Linux
> 
>```
>python3 -m venv env
>```
>```
>source env/bin/activate
>```
>```
>python3 -m pip install --upgrade pip

>для Windows
> 
>```
>python -m venv venv
>```
>```
>source venv/Scripts/activate 
>```
>```
>python -m pip install --upgrade pip

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

>для Linux
>```
>python3 manage.py migrate

>для Windows
>```
>python manage.py migrate

Запустить проект:

>для Linux
>```
>python3 manage.py runserver

>для Windows
>```
>python manage.py runserver
