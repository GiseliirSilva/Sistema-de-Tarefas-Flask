# 🚀 Sistema de Tarefas com Flask e Python

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey.svg) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-green.svg)
![LoginManager](https://img.shields.io/badge/Flask--Login-blueviolet.svg)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen.svg)

## 📄 Sobre o Projeto

Este é um sistema web completo de gerenciamento de tarefas, desenvolvido com o framework **Flask** em **Python**, utilizando **SQLAlchemy** para interação com o banco de dados.
O projeto permite aos usuários realizar operações CRUD (Criar, Ler, Atualizar, Excluir) em tarefas, além de funcionalidades de autenticação de usuários e redefinição de senha.

O objetivo principal foi a aplicação prática de conhecimentos em desenvolvimento backend e automação com Python, com foco em boas práticas de organização de código e segurança.

## ✨ Funcionalidades

* **Autenticação de Usuário:** Cadastro, Login e Logout seguros com criptografia de senha (`werkzeug.security`).
* **Recuperação de Senha:** Funcionalidade "Esqueci a Senha" com geração de token seguro por e-mail (simulação para ambiente local).
* **Gerenciamento de Tarefas:**
    * **Criação:** Adicione novas tarefas com descrição e status.
    * **Visualização:** Liste todas as suas tarefas.
    * **Edição:** Altere o nome e o status de tarefas existentes.
    * **Exclusão:** Remova tarefas.
* **Controle de Acesso:** Páginas protegidas que exigem autenticação do usuário.
* **Interface Responsiva:** Desenvolvida com HTML/CSS básico para uma experiência de usuário funcional.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.x
* **Framework Web:** Flask
* **ORM (Object-Relational Mapping):** Flask-SQLAlchemy
* **Autenticação:** Flask-Login
* **Segurança de Senha:** Werkzeug Security
* **Geração de Token (Redefinição de Senha):** ItsDangerous
* **Servidor de Produção:** Gunicorn
* **Banco de Dados:** SQLite3 (local, para desenvolvimento e deploy simples)
* **Gerenciamento de Dependências:** pip / requirements.txt
* **Variáveis de Ambiente:** python-dotenv (para desenvolvimento local)

## ⚙️ Como Rodar o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto em sua máquina.

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/GiseliirSilva/Sistema-de-Tarefas-Flask.git](https://github.com/GiseliirSilva/Sistema-de-Tarefas-Flask.git)
    cd Sistema-de-Tarefas-Flask
    ```

2.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No Linux/macOS:
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente:**
    * Crie um arquivo `.env` na raiz do projeto (no mesmo diretório de `app.py`). * Adicione a seguinte linha, substituindo pelo seu valor:
        ```
        SECRET_KEY='sua_chave_secreta_para_desenvolvimento'
        ```
        *Para gerar uma chave forte, você pode usar `python -c "import os; print(os.urandom(24))"` no terminal.*

5.  **Execute o Aplicativo:**
    ```bash
    python app.py ```
    O servidor estará rodando em `http://127.0.0.1:5000/` (ou outra porta indicada no terminal).

## ☁️ Deploy Online

Este projeto está publicado e pode ser acessado em:

* **URL:** [https://GiseliirSilva.pythonanywhere.com/](https://GiseliirSilva.pythonanywhere.com/)

O deploy foi realizado utilizando o **PythonAnywhere**, configurado para rodar o aplicativo com `Gunicorn`.

## 📈 Melhorias Futuras (Roadmap)

* [ 1 ] Implementar envio real de e-mails para redefinição de senha (integrar com serviço de e-mail).
* [ 2 ] Migrar o banco de dados SQLite para PostgreSQL em ambiente de produção para maior persistência e escalabilidade.
* [ 3 ] Adicionar validações mais robustas em formulários (Flask-WTF).
* [ 4 ] Melhorar a interface do usuário com um framework CSS (ex: Bootstrap ou Tailwind CSS).
* [ 5 ] Funcionalidade de filtragem e busca de tarefas.
* [ 6 ] Testes unitários e de integração.

## 🧑‍💻 Autor(a)

* **Giseliir Silva** - Estudante de Análise e Desenvolvimento de Sistemas com foco em backend e automação com Python.
* Apaixonada por resolução de problemas e otimização de processos. Busco aplicação prática dos conhecimentos adquiridos em projetos reais
* para aprimorar minhas habilidades e contribuir com soluções eficientes. Minha experiência anterior em suporte técnico e enfermagem me
* proporcionou competências transferíveis como trabalho em equipe, organização e comunicação eficaz, que aplico no desenvolvimento de sistemas.

    * **GitHub:** [@GiseliirSilva](https://github.com/GiseliirSilva)
    * **LinkedIn:** [Giseliir Silva](https://www.linkedin.com/in/giseli-irsilva)

## 📜 Licença

Este projeto está sob a licença [MIT License](https://opensource.org/licenses/MIT).
Você pode escolher outra se preferir, como a Apache 2.0 ou GNU GPL. A MIT é simples e permite bastante liberdade.

---
