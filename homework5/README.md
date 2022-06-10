# yes

### Description:
    Запуск программы:
    1) Без Docker'a: `make upp` (up зарезервировано для Docker'а)
    2) При помощи Docker'а:
        docker build -t hw5 .
        docker run -d --name hw5_container -p 80:80 hw5
    Перейти по ссылке http://127.0.0.1/docs
    Примечание: make upp, а так же все другие команды (кроме up, используемой Docker'ом) написаны для работы на Windows.
    Чтобы они работали на Linux, необходимо: 
    Заменить все каталоги `Scripts` на `bin`
    На строке 13 заменить `python` на `python3.9`

### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format
