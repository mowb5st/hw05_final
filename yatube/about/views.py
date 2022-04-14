from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'label': 'Об авторе проекта',
            'header': 'Привет, я автор',
            'text': (
                'Меня зовут Мансур, мне 26, я из Красноярска. '
                'Желание учиться чему-то новому и интерес к программированию '
                '- это главные причины, по которым я пришел в эту сферу. '
                'С самого начала у меня был особый интерес к IT технологиям, '
                'Начав с самостоятельного изучения C++ и C#, я дошел до '
                'курсов по Python. Сейчас я занимаюсь только изучением '
                'Python. Хочется профессионально овладеть этим языком и '
                'начать с этого свою карьеру в разработке.'
            ),
            'git': 'https://github.com/mowb5st',
            'vk': 'https://vk.com/mowb5st',
        }
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'label': 'Технологии',
            'header': 'Вот что я умею',
            'text': (
                'Сайт написан на языке Python при помощи фреймворка Django. '
                'Для генерации страниц используется язык разметки HTML '
                '(вот так неожиданность) Все происходит в рамках изучения '
                'курса "Бэкенд на Django" в Яндекс.Практикуме'
            ),
            'first_tech': 'Python',
            'second_tech': 'Django',
        }
        return context
