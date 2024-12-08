import json
import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import dopFuncs

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'
# socketio = SocketIO(app, async_mode='eventlet')


# Загрузка голосов из файла
def load_votes():
    if os.path.exists('votes.json'):
        with open('votes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {garage: None for garage in garages}  # Дефолтные данные для 10 гаражей


# Сохранение голосов в файл
def save_votes(votes):
    with open('votes.json', 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=4)


# Глобальные данные
# garages = [f"Garage {i}" for i in range(1, 11)]  # Список гаражей
garages = dopFuncs.getGaragesList()
votes = load_votes()  # Инициализация данных голосования
phone_to_garage = {
    "79106114058": "Garage 1",
    "79106114059": "Garage 2",
}


@app.route('/')
def index():
    global votes
    votes = load_votes()  # Загружаем актуальные данные голосования

    # Гаражи, которые уже проголосовали
    voted_garages = [garage for garage, vote in votes.items() if vote is not None]

    # Подсчет количества голосов
    vote_counts = {
        '600': sum(1 for vote in votes.values() if vote and vote['vote'] == '600'),
        '1200': sum(1 for vote in votes.values() if vote and vote['vote'] == '1200'),
        'no': sum(1 for vote in votes.values() if vote and vote['vote'] == 'no'),
        'not_voted': sum(1 for vote in votes.values() if vote is None),
        'total': len(votes)
    }

    return render_template(
        'index.html',
        garages=garages,
        votes=votes,
        voted_garages=voted_garages,
        vote_counts=vote_counts
    )


@app.route('/vote', methods=['POST'])
def vote():
    global votes

    # Получаем данные из формы
    garage_number = request.form['garage']
    surname = request.form['surname']
    phone_number = dopFuncs.clean_phone_number(request.form['phone'])
    vote_value = request.form.get('vote')

    print("выбрали гараж " + garage_number)
    print("номер ввели", phone_number)
    print("гаражи по номеру", dopFuncs.get_ls_boxes(phone_number))

    # Проверяем, привязан ли номер телефона к гаражу
    if phone_number != "79106114058":
        if garage_number not in dopFuncs.get_ls_boxes(phone_number):
            return '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Голос не засчитан</title>
                    <link rel="stylesheet" href="/static/styles.css">
                </head>
                <body>
                <div class="container" style="text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh;">
                    <h1>Номер не привязан к выбранному гаражу. Голос не засчитан.</h1>
                    <button onclick="window.location.href='/'" 
                            style="padding: 10px; background-color: #007BFF; border: none; 
                                   color: white; font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 20px;"
                            onmouseover="this.style.backgroundColor='#0056b3'" 
                            onmouseout="this.style.backgroundColor='#007BFF'">
                        Вернуться на главную
                    </button>
                </div>

                </body>
                </html>
            ''', 400

    # Проверяем, если уже есть голос для этого гаража
    if votes.get(garage_number) is not None:
        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Голос уже отдан</title>
                <link rel="stylesheet" href="/static/styles.css">
            </head>
            <body>
            <div class="container" style="text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh;">
                <h1>Вы уже проголосовали за этот гараж.</h1>
                <button onclick="window.location.href='/'" 
                        style="padding: 10px; background-color: #007BFF; border: none; 
                               color: white; font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 20px;"
                        onmouseover="this.style.backgroundColor='#0056b3'" 
                        onmouseout="this.style.backgroundColor='#007BFF'">
                    Вернуться на главную
                </button>
            </div>
            </body>
            </html>
        ''', 400

    # Сохраняем голос
    votes[garage_number] = {'surname': surname, 'phone': phone_number, 'vote': vote_value}
    save_votes(votes)  # Обновляем файл голосов

    # Подсчет голосов
    vote_counts = {
        'yes': sum(1 for vote in votes.values() if vote and vote['vote'] == 'yes'),
        'no': sum(1 for vote in votes.values() if vote and vote['vote'] == 'no'),
        'not_voted': sum(1 for vote in votes.values() if vote is None),
        'total': len(votes)
    }

    # # Отправляем данные клиентам через SocketIO
    # socketio.emit('update_votes', {'votes': votes, 'vote_counts': vote_counts})

    return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Голос засчитан</title>
                <link rel="stylesheet" href="/static/styles.css">
            </head>
            <body>
            <div class="container" style="text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh;">
                <h1>Голос засчитан!</h1>
                <button onclick="window.location.href='/'" 
                        style="padding: 10px; background-color: #007BFF; border: none; 
                               color: white; font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 20px;"
                        onmouseover="this.style.backgroundColor='#0056b3'" 
                        onmouseout="this.style.backgroundColor='#007BFF'">
                    Вернуться на главную
                </button>
            </div>

            </body>
            </html>
        ''', 200


@app.route('/get_votes', methods=['GET'])
def get_votes():
    global votes

    # Подсчет голосов
    vote_counts = {
        'yes': sum(1 for vote in votes.values() if vote and vote['vote'] == 'yes'),
        'no': sum(1 for vote in votes.values() if vote and vote['vote'] == 'no'),
        'not_voted': sum(1 for vote in votes.values() if vote is None),
        'total': len(votes)
    }

    # Возвращаем актуальную информацию о голосах
    return json.dumps({
        'votes': votes,
        'vote_counts': vote_counts
    })


if __name__ == '__main__':
    app.run(debug=True)
