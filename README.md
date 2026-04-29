# Dojo Manager

Sistema de gestão para academias de artes marciais. Controle de alunos, turmas, presenças, graduações e financeiro.

## Tecnologias

- Python 3.13 / Django 5.2
- PostgreSQL (produção) / SQLite (desenvolvimento)
- Bootstrap 5
- Railway (deploy)

## Rodando localmente

```bash
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
cp .env.example .env      
python manage.py migrate
python manage.py seed
python manage.py runserver
```

## Deploy (Railway)

Acesso: https://dojomanager-production.up.railway.app

login: `admin` / `admin123`

Variáveis de ambiente necessárias:

| Variável | Valor |
|---|---|
| `SECRET_KEY` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | domínio gerado pelo Railway |
| `DATABASE_URL` | preenchido automaticamente pelo PostgreSQL do Railway |
| `DJANGO_SUPERUSER_USERNAME` | `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | `admin123` |
| `DJANGO_SUPERUSER_EMAIL` | seu email |


## Funcionalidades

- Cadastro de alunos com foto e histórico de graduações
- Gestão de turmas, horários e instrutores
- Controle de presenças
- Financeiro: planos, matrículas e mensalidades
- Dashboard com resumo do dia
