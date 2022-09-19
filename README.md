# Yatube - социальная сеть для блогеров
Проект представляет собой социальную сеть в виде микробогов и обновляющейся лентой.

## Функционал
Возможность вести авторские блоки с текстом и картинкой в отдельном посте. Присутствует лента послених постов, возможность подписаться на авторов и отдельная избранная лента, в которой отображаются посты только тех авторов, на которых вы подписаны.
Также можно просмотеть все посты отдельного автора, перейдя в его профиль.

# Установка и запуск проекта
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:mowb5st/hw05_final.git
```

```
cd hw05_final
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
