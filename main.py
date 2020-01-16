import configparser

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from Code.resume_generator import generate_template
from Code.sql_tools import SQLDataBase


def construct_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Трудоустройство', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Резюме', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Заявка на профтестирование', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Собеседование', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Сопроводительное письмо к резюме', color=VkKeyboardColor.DEFAULT)
    return keyboard


def get_resume(user_id, database):
    user = database.get_user(user_id)
    resume = database.get_resume(user_id)
    context = {"phone": resume.phone, "email": resume.email,
               "full_name": " ".join([user.first_name, user.second_name, user.last_name]),
               "birthday": resume.birthday,
               "full_years": resume.full_years,
               "wanted_profession": resume.wanted_profession,
               "work_period": resume.work_period,
               "company_name": resume.company_name,
               "work_exp": resume.work_exp,
               "profession": resume.profession,
               "job_responsibilities": resume.job_responsibilities,
               "finish_education": resume.finish_education,
               "university": resume.university,
               "specialty": resume.specialty,
               "qualification": resume.qualification,
               "finish_education_ad": resume.finish_education_ad,
               "university_ad": resume.university_ad,
               "qualification_ad": resume.qualification_ad,
               "personal_skills": resume.personal_skills,
               "recommendations": resume.recommendations
               }
    return generate_template(context)


def main():
    states = dict()
    # Various states:
    # IDLE
    # {"TESTING": 0 }
    # {"RESUME": 0 }

    config = configparser.ConfigParser()
    config.read("./config.ini")
    token = config.get("credentials", "token")
    group_id = config.get("credentials", "group_id")

    vk_session = vk_api.VkApi(token=token)
    upload = vk_api.VkUpload(vk_session)
    vk = vk_session.get_api()

    database = SQLDataBase()
    keyboard = construct_keyboard()
    longpoll = VkBotLongPoll(vk_session, group_id=group_id)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            event: vk_api.bot_longpoll.VkBotEvent = event

            states.setdefault(event.obj.from_id, 'IDLE')

            if event.obj.text.lower() == 'начать' or event.obj.text.lower() == 'выход':
                states[event.obj.from_id] = 'IDLE'
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="Привет! Я бот Центра Карьеры!"
                )

            elif event.obj.text.lower() == 'резюме':
                nkeyboard = VkKeyboard(one_time=True)
                nkeyboard.add_button('Составить резюме самому', color=VkKeyboardColor.DEFAULT)
                nkeyboard.add_line()  # Переход на новую строку
                nkeyboard.add_button('Составить с помощью новых сервисов', color=VkKeyboardColor.DEFAULT)
                nkeyboard.add_line()  # Переход на новую строку
                nkeyboard.add_button('Составить резюме с помощью бота', color=VkKeyboardColor.DEFAULT)
                nkeyboard.add_line()  # Переход на новую строку
                nkeyboard.add_button('Получить резюме', color=VkKeyboardColor.DEFAULT)
                nkeyboard.add_button('Выход', color=VkKeyboardColor.DEFAULT)
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=nkeyboard.get_keyboard(),
                    message="Выберите способ:"
                )

            elif event.obj.text.lower() == 'составить резюме самому':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="Как правильно составить резюме?\n"
                            "https://hiterbober.ru/work/kak-pravilno-sostavit-rezyume-obrazec.html"
                )

            elif event.obj.text.lower() == 'составить с помощью новых сервисов':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="7 новых сервисов создания резюме:\n"
                            "https://www.cossa.ru/trends/104949/www.smmashing.media/www.ntmedia.ru"
                )

            elif event.obj.text.lower() == 'составить резюме с помощью бота':
                states[event.obj.from_id] = {'RESUME': -1, 'USER_QUERY': database.User(),
                                             'RESUME_QUERY': database.Resume()}

            elif event.obj.text.lower() == 'получить резюме, составленное ботом':
                if database.get_resume(event.obj.from_id):
                    resume_document = get_resume(event.obj.from_id, database)
                    file = upload.document_message(resume_document, 'resume', peer_id=event.obj.from_id)
                    vk.messages.send(
                        user_id=event.obj.from_id,
                        random_id=get_random_id(),
                        attachment=file['doc']['url'][len('https://vk.com/'):],
                        keyboard=keyboard.get_keyboard(),
                        message="Вот ваше резюме!"
                    )
                else:
                    vk.messages.send(
                        user_id=event.obj.from_id,
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard(),
                        message="Сначала создайте резюме :)"
                    )

            elif event.obj.text.lower() == 'заявка на профтестирование':
                if database.get_testing(event.obj.from_id):
                    vk.messages.send(
                        user_id=event.obj.from_id,
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard(),
                        message="Вы уже отправляли заявку. Пожалуйста, ожидайте письмо на почте."
                    )
                else:
                    states[event.obj.from_id] = {'TESTING': -1, 'USER_QUERY': database.User(),
                                                 'TESTING_QUERY': database.Testing()}

            elif event.obj.text.lower() == 'трудоустройство':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="Вакансии и стажировки доступные на данный момент:\n"
                            "https://misis.ru/students/vacancies/"
                )

            elif event.obj.text.lower() == 'собеседование':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="Как пройти собеседование?\n"
                            "https://hh.ru/article/301412"
                )

            elif event.obj.text.lower() == 'сопроводительное письмо к резюме':
                nkeyboard = VkKeyboard(one_time=True)
                nkeyboard.add_button('Пример', color=VkKeyboardColor.POSITIVE)
                nkeyboard.add_button('Статья', color=VkKeyboardColor.DEFAULT)
                nkeyboard.add_line()
                nkeyboard.add_button('Выход', color=VkKeyboardColor.DEFAULT)
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=nkeyboard.get_keyboard(),
                    message="Вы можете посмотреть несколько готовых примеров сопроводительных писем"
                            " или прочитать статью как правильно их составлять."
                )

            elif event.obj.text.lower() == 'статья':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="Как писать сопроводительное письмо к резюме?\n"
                            "https://jobresumes.ru/resume/soprovoditelnoe-pismo-k-rezyume/"
                )

            elif event.obj.text.lower() == 'привет':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="Привет! Выбирай нужное действие в меню!"
                )

            elif event.obj.text.lower() == 'пока':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message="До встречи!",
                )

            elif event.obj.text.lower() == 'пример':
                nkeyboard = VkKeyboard(one_time=True)
                nkeyboard.add_button('Посмотреть пример №2', color=VkKeyboardColor.DEFAULT)
                nkeyboard.add_line()
                nkeyboard.add_button('Выход', color=VkKeyboardColor.DEFAULT)
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=nkeyboard.get_keyboard(),
                    message="Пример №1\nВниманию HR-менеджера по кадрам Соколовой Е. П.\n"
                            "Уважаемая Елена Петровна!\nМеня заинтересовала вакансия администратора"
                            " в развлекательном комплексе «Город» о которой я узнала на вашем интернет-портале.\n"
                            "Считаю необходимым сообщить Вам, что в административной сфере имею достаточно большой"
                            " опыт (более 5 лет). Коммуникабельна, хорошо схожусь с людьми, ответственная, "
                            "в работе педантична.\nРезюме прилагаю.\nБлагодарю за внимание и надеюсь на одобрение."
                            "\nС уважением, Иванова Анастасия\n"
                            "Тел. 321-78-87\n Email. ivanovanastya@mail.ru\n"
                )

            elif event.obj.text.lower() == 'посмотреть пример №2':
                nkeyboard = VkKeyboard(one_time=True)
                nkeyboard.add_button('Посмотреть пример №3', color=VkKeyboardColor.DEFAULT)
                nkeyboard.add_line()
                nkeyboard.add_button('Выход', color=VkKeyboardColor.DEFAULT)
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=nkeyboard.get_keyboard(),
                    message="Пример №2\n Добрый день!\n\nМеня зовут Евдокия Озерная."
                            " Меня заинтересовала вакансия главного менеджера по продажам,"
                            " открытая на интернет-портале. Имею достаточно большой опыт работы в торговой"
                            " сфере. На предыдущих должностях занимала место марчендайзера и регионального менеджера. "
                            "В процессе трудовой деятельности достигла довольно высоких результатов:\n"
                            "- Увеличение продаж на 30%;\n- Стимулировала клиентов на покупку наших товаров;\n"
                            "- Разработала и внедрила схему более эффективного управления персоналом.\n"
                            "Поиском нового места работы занимаюсь по причине смены жительства.\n"
                            "Резюме прилагаю. Надеюсь на одобрение своей кандидатуры на предложенную вакансию и "
                            "благодарю за время, уделенное моей кандидатуре.\nС уважением, Евдокия Озерная\nКонтакты:"
                            " тел.908-78-67, email. ozornaya@mail.ru\n"
                            "Как составить сопроводительное письмо к резюме без вакансии? Есть ситуации, "
                            "когда организация не размещала ни на одном ресурсе объявление о вакансии, "
                            "но вы горите желанием работать в этой фирме и предполагаете, что возможно именно для вас "
                            "найдется должность, соответствующая вашим профессиональным навыкам. Составление такого "
                            "документа требует индивидуального подхода и максимум внимания к потенциальному "
                            "работодателю. В этом случае вам нужно решительно заявить о себе, сообщить о готовности"
                            " личной встречи и собеседования."
                )

            elif event.obj.text.lower() == 'посмотреть пример №3':
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message="Пример №3\nВаши личные и контактные данные (ФИО, телефон, Email)\n"
                            "Название компании\nДанные адресата(ФИО)\nДата отправки\nДобрый день!\n"
                            "Я Иванов Иван Иванович инженер металлоконструкций с опытом работы более 10 лет."
                            " Работал на различных строительных объектах. Разработал проекты многих конструкций,"
                            " которые успешно реализованы. Имею налаженные партнерские отношения с металлобазами,"
                            " под моим руководством находится бригада опытных сварщиков, в наличии профессиональное"
                            " оборудование.\nО вашем предприятии узнал изучая сайты строительных компаний."
                            " Изучил деятельность вашей компании и готов получить должность инженера по "
                            "металлоконструкциям.\nБуду вам признателен за интерес, проявленный к моей кандидатуре "
                            "и обратную связь. Высылаю свое резюме и портфолио проектов. очень надеюсь на "
                            "плодотворное сотрудничество.\nБлагодарю за внимание!\nС уважением, Иванов Иван Иванович\n"
                            "Очень важно при написании документа, сопровождающего резюме, сразу заинтересовать "
                            "работодателя преимуществами перед прочими соискателями. При приеме на работу немаловажное "
                            "значение имеет человеческий фактор. Задача кандидата вызвать симпатию у кадрового менеджер"
                            "а или руководителя и именно письмо – это залог положительного расположение в ваш адрес."
                )

            user = event.obj.from_id
            if 'RESUME' in states[user]:
                resume_state = states[user]['RESUME']
                user_query = states[user]['USER_QUERY']
                resume_query = states[user]['RESUME_QUERY']
                if resume_state == 0:
                    user_query.first_name = event.obj.text
                elif resume_state == 1:
                    user_query.second_name = event.obj.text
                elif resume_state == 2:
                    user_query.last_name = event.obj.text
                elif resume_state == 3:
                    resume_query.birthday = event.obj.text
                elif resume_state == 4:
                    resume_query.full_years = event.obj.text
                elif resume_state == 5:
                    resume_query.phone = event.obj.text
                elif resume_state == 6:
                    resume_query.email = event.obj.text
                elif resume_state == 7:
                    resume_query.wanted_profession = event.obj.text
                elif resume_state == 8:
                    resume_query.company_name = event.obj.text
                elif resume_state == 9:
                    resume_query.work_period = event.obj.text
                elif resume_state == 10:
                    resume_query.work_exp = event.obj.text
                elif resume_state == 11:
                    resume_query.profession = event.obj.text
                elif resume_state == 12:
                    resume_query.job_responsibilities = event.obj.text
                elif resume_state == 13:
                    resume_query.university = event.obj.text
                elif resume_state == 14:
                    resume_query.finish_education = event.obj.text
                elif resume_state == 15:
                    resume_query.specialty = event.obj.text
                elif resume_state == 16:
                    resume_query.qualification = event.obj.text
                elif resume_state == 17:
                    resume_query.university_ad = event.obj.text
                elif resume_state == 18:
                    resume_query.finish_education_ad = event.obj.text
                elif resume_state == 19:
                    resume_query.qualification_ad = event.obj.text
                elif resume_state == 20:
                    resume_query.personal_skills = event.obj.text
                elif resume_state == 21:
                    resume_query.recommendations = event.obj.text
                states[user]['USER_QUERY'] = user_query
                states[user]['RESUME_QUERY'] = resume_query
                states[user]['RESUME'] += 1
            if 'RESUME' in states[user]:
                resume_state = states[user]['RESUME']
                if resume_state == 0:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите имя: "
                    )
                elif resume_state == 1:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите фамилию: "
                    )
                elif resume_state == 2:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите отчество: "
                    )
                elif resume_state == 3:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите дату рождения: "
                    )
                elif resume_state == 4:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите количество полных лет: "
                    )
                elif resume_state == 5:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите телефон: "
                    )
                elif resume_state == 6:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите электронную почту: "
                    )
                elif resume_state == 7:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите желаемую должность: \n"
                                "Рекомендации: В этом поле необходимо указать должность, на которую "
                                "вы претендуете. Именно на это поле в первую очередь смотрят работодатели, "
                                "поэтому не стоит писать что-то вроде «ищу работу» или «хочу реализовать себя»."
                                " Такое резюме скорее всего попадет в мусорную корзину или же привлечет внимание "
                                "MLM-компаний. Если же вы человек разносторонний и владеете несколькими специальностями"
                                ", то не нужно писать их все одновременно. Обычно компания ищет вполне конкретного "
                                "специалиста. Лучше составить резюме отдельно под каждую должность, а навыки из других"
                                " областей, напрямую не связанных с желаемой должностью, указать в графе «доп. "
                                "информация»."
                    )
                elif resume_state == 8:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Раздел: Опыт работы\nВведите название компании: \nВнимание!!! Если у вас нет опыта "
                                "работы или он небольшой, то обязательно укажите где, когда и какие практики вы "
                                "проходили. Рекомендации: Если название компании, в которой вы работали, неизвестно"
                                " массовой аудитории, то стоит указать ее сферу деятельности – ООО «Лютик» (ведущая"
                                " компания по выращиванию и продаже цветов). Также, не стоит указывать те места "
                                "работы, которые не имеют отношение к желаемой должности. О них можно будет в краткой"
                                " форме рассказать в графе «доп. информация»."
                    )
                elif resume_state == 9:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите период работы в этой компании: "
                    )
                elif resume_state == 10:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите стаж работы: "
                    )
                elif resume_state == 11:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите название должности: \nРекомендации: Если название вашей должности не "
                                "является общеупотребительным или не раскрывает суть деятельности (например, «старший "
                                "специалист» или «менеджер-визуализатор»), лучше напишите общеупотребительный аналог, "
                                "поскольку до просмотра опыта работы hr-менеджер может и не дойти, сразу решив, что вы "
                                "не подходите."
                    )
                elif resume_state == 12:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите описание своих служебных обязанностей: \n Рекомендации: В описании вашей"
                                " деятельности старайтесь описывать то, что вы конкретно делали и чего добились, и "
                                "избегайте штампов и ничего не значащих фраз, типа «повышение эффективности "
                                "деятельности», «оптимизация бизнес-процессов», «налаживание процессов» и пр. Если "
                                "пишите такие фразы, старайтесь пояснять в чем именно это заключалось. Мы также не "
                                "рекомендуем писать это поле только заглавными буквами или сильно разбавлять русские "
                                "фразы английскими словами – такой текст выглядит небрежно и тяжело читается."

                    )
                elif resume_state == 13:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Раздел: Образование \nВведите институт: "
                    )
                elif resume_state == 14:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите год окончания: "
                    )
                elif resume_state == 15:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите специальность: \nРекомендации: Пишите название специальности полностью, "
                                "особенно если аббревиатура не является широко известной."
                    )
                elif resume_state == 16:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите квалификацию(бакалавр, магистр, специалист и т.п.): "
                    )
                elif resume_state == 17:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Дополнительное образование \nВведите учебное заведение: "
                    )
                elif resume_state == 18:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите год окончания: "
                    )
                elif resume_state == 19:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите квалификацию: \n(название курсов, программ переподготовки и т.п.)"
                    )
                elif resume_state == 20:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Раздел: Дополнительная информация \nВведите список умений и навыков: \n"
                                "Рекомендации: В этой графе не нужно писать про вашу стрессоустойчивость, "
                                "коммуникабельность и обучаемость. Все равно это те навыки, о которых будут судить при "
                                "личном общении. Лучше написать что-то, что характеризует вас как живого человека, у "
                                "которого есть свои достоинства и сильные качества."
                    )
                elif resume_state == 21:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Рекомендации \nВведите имена, фамилии и контактную информацию ваших руководителей с "
                                "предыдущих мест работы."
                    )
                elif resume_state == 22:
                    user_query = states[user]['USER_QUERY']
                    resume_query = states[user]['RESUME_QUERY']
                    user_query.id = user
                    resume_query.user_id = user_query.id

                    database.add_user(user_query)
                    database.add_resume(resume_query)

                    resume_document = get_resume(event.obj.from_id, database)
                    file = upload.document_message(resume_document, 'resume', peer_id=event.obj.from_id)

                    states[user] = 'IDLE'

                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        attachment=file['doc']['url'][len('https://vk.com/'):],
                        keyboard=keyboard.get_keyboard(),
                        message="Спасибо! Мы составили Вам резюме!\n"
                                "ВНИМАНИЕ!!!\nСоветуем придерживаться представленной формы (шрифты, цвета и т.п.)."
                                "После окончания заполнения информации не забудьте провести окончательное "
                                "редактирование резюме:\n1. Выполнить выравнивание.\n2. Удалить все вспомогательные "
                                "текста и подсказки.\n3. Обязательно разместите свою фотографию. Пример фото приведён."
                                "\n4. Уместите всё резюме на один лист."
                    )
            if 'TESTING' in states[user]:
                testing_state = states[user]['TESTING']
                testing_query = states[user]['TESTING_QUERY']
                if testing_state == 0:
                    testing_query.first_name = event.obj.text
                elif testing_state == 1:
                    testing_query.second_name = event.obj.text
                elif testing_state == 2:
                    testing_query.last_name = event.obj.text
                elif testing_state == 3:
                    testing_query.institute = event.obj.text
                elif testing_state == 4:
                    testing_query.group = event.obj.text
                elif testing_state == 5:
                    testing_query.email = event.obj.text
                states[user]['TESTING_QUERY'] = testing_query
                states[user]['TESTING'] += 1
            if 'TESTING' in states[user]:
                testing_state = states[user]['TESTING']
                if testing_state == 0:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите имя: "
                    )
                elif testing_state == 1:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите фамилию: "
                    )
                elif testing_state == 2:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите отчество: "
                    )
                elif testing_state == 3:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите свой институт(ИТАСУ, Горный или другое): "
                    )
                elif testing_state == 4:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите академическую группу: "
                    )
                elif testing_state == 5:
                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        message="Введите свой email (мы отправим ссылку на тестирование туда): "
                    )
                elif testing_state == 6:
                    user_query = states[user]['USER_QUERY']
                    testing_query = states[user]['TESTING_QUERY']
                    user_query.id = user
                    testing_query.user_id = user_query.id

                    # database.add_user(user_query)
                    database.add_testing(testing_query)

                    # resume_document = get_resume(event.obj.from_id, database)
                    # file = upload.document_message(resume_document, 'resume', peer_id=event.obj.from_id)

                    states[user] = 'IDLE'

                    import sqlite3
                    import csv
                    import os
                    con = sqlite3.connect('Data/database.sqlite')
                    if os.path.exists('test.csv'):
                        os.remove('test.csv')
                    outfile = open('test.csv', 'w')
                    outcsv = csv.writer(outfile)

                    cursor = con.execute('select * from Testing')

                    # dump column titles (optional)
                    outcsv.writerow(x[0] for x in cursor.description)
                    # dump rows
                    outcsv.writerows(cursor.fetchall())
                    outfile.close()

                    import smtplib
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.text import MIMEText
                    from email.mime.base import MIMEBase
                    from email import encoders
                    mail_content = '''Hello,
                    This is a test mail.
                    In this mail we are sending some attachments.
                    The mail is sent using Python SMTP library.
                    Thank You
                    '''
                    # The mail addresses and password
                    sender_address = 'orzhekheuge@gmail.com'
                    sender_pass = 'ntcnbyu198'
                    receiver_address = 'zorzheh000@mail.ru'
                    # Setup the MIME
                    message = MIMEMultipart()
                    message['From'] = sender_address
                    message['To'] = receiver_address
                    message['Subject'] = 'A test mail sent by Python. It has an attachment.'
                    # The subject line
                    # The body and the attachments for the mail
                    message.attach(MIMEText(mail_content, 'plain'))
                    attach_file_name = 'test.csv'
                    attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
                    payload = MIMEBase('application', 'octate-stream')
                    payload.set_payload((attach_file).read())
                    encoders.encode_base64(payload)  # encode the attachment
                    # add payload header with filename
                    payload.add_header('Content-Decomposition', 'attachment; filename="test.csv"')
                    message.attach(payload)
                    # Create SMTP session for sending the mail
                    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
                    session.starttls()  # enable security
                    session.login(sender_address, sender_pass)  # login with mail_id and password
                    text = message.as_string()
                    session.sendmail(sender_address, receiver_address, text)
                    session.quit()

                    vk.messages.send(
                        user_id=user,
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard(),
                        message="Спасибо! Заявка на профтестирование отправлена, ожидайте письмо на почте!"
                    )


if __name__ == '__main__':
    main()
