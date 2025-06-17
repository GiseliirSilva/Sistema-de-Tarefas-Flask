# app.py
import os
from dotenv import load_dotenv
from datetime import date, datetime
from sqlalchemy import and_
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer


# ✅ Carrega as variáveis do arquivo .env no ambiente local (apenas para desenvolvimento)
load_dotenv()

# ✅ Criação do app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY')

if not app.secret_key:
    raise ValueError("A variável de ambiente 'SECRET_KEY' não está definida. Por favor, defina-a.")

app.debug = False

# ✅ Configuração dos objetos com app
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para acessar esta página!"
login_manager.login_message_category = "info"

# ✅ Configuração do Serializer para tokens de redefinição de senha
s = URLSafeTimedSerializer(app.secret_key)


# ✅ Modelo Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    tarefas = db.relationship('Tarefa', backref='usuario', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


# ✅ Modelo Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo = db.Column(db.String(120), nullable=False)  # Mudado de 'descricao' para 'titulo' para consistência
    prazo = db.Column(db.Date)
    categoria = db.Column(db.String(50))
    concluida = db.Column(db.Boolean, default=False)


# ✅ Criação do banco de dados
with app.app_context():
    db.create_all()


# ✅ Carregar usuário
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ✅ Tela de boas-vindas
@app.route("/")
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("inicio.html")


# ✅ Página principal com tarefas
@app.route("/tarefas")  # Rota duplicada removida
@login_required  # Adicionado para garantir que apenas usuários logados vejam a home com as tarefas reais
def home():
    data_hoje = date.today()
    query_tarefas = Tarefa.query.filter_by(usuario_id=current_user.id)
    filtro = request.args.get("filtro", "todas")
    categoria_filtro = request.args.get("categoria", "")
    ordenar_por = request.args.get("ordenar", "")

    # Lógica de filtragem por status
    if filtro == "pendentes":
        query_tarefas = query_tarefas.filter_by(concluida=False)
    elif filtro == "concluidas":
        query_tarefas = query_tarefas.filter_by(concluida=True)
    elif filtro == "atrasadas":
        query_tarefas = query_tarefas.filter(
            and_(
                Tarefa.concluida.is_(False),
                Tarefa.prazo < data_hoje
            )
        )

    # ✅ Filtrar por categoria, se selecionada
    if categoria_filtro and categoria_filtro != "todas":
        query_tarefas = query_tarefas.filter_by(categoria=categoria_filtro)

    # ✅ Lógica de ordenação
    if ordenar_por == "prazo":
        query_tarefas = query_tarefas.order_by(Tarefa.prazo.asc())
    elif ordenar_por == "descricao":
        query_tarefas = query_tarefas.order_by(Tarefa.titulo.asc())
    else:
        # ✅ Ordenação padrão: por ID decrescente (tarefas mais novas primeiro)
        query_tarefas = query_tarefas.order_by(Tarefa.id.desc())

    tarefas = query_tarefas.all()  # Executar a query e obter as tarefas filtradas

    todas_as_tarefas_do_usuario = Tarefa.query.filter_by(usuario_id=current_user.id).all()
    categorias = sorted({t.categoria for t in todas_as_tarefas_do_usuario if t.categoria})

    # ✅ Recalcular totais com base na query do usuário logado
    total_concluidas = Tarefa.query.filter_by(
        usuario_id=current_user.id,
        concluida=True
    ).count()

    total_pendentes = Tarefa.query.filter_by(
        usuario_id=current_user.id,
        concluida=False
    ).count()

    # ✅ Cálculo correto de tarefas atrasadas para o contador:
    # ✅ Que não estão concluídas E cujo prazo é anterior à data de hoje
    total_atrasadas = Tarefa.query.filter(
        and_(
            Tarefa.usuario_id == current_user.id,
            Tarefa.concluida.is_(False),
            Tarefa.prazo < data_hoje
        )
    ).count()

    categorias = db.session.query(Tarefa.categoria).filter(
        Tarefa.usuario_id == current_user.id,
        Tarefa.categoria.isnot(None)  # Garante que não pega categorias nulas
    ).distinct().order_by(Tarefa.categoria).all()
    categorias = [c[0] for c in categorias if c[0]]  # Extrai os nomes das categorias da tupla

    return render_template(
        "index.html",
        tarefas=tarefas,
        total_concluidas=total_concluidas,
        total_pendentes=total_pendentes,
        total_atrasadas=total_atrasadas,
        filtro=filtro,
        categoria_filtro=categoria_filtro,
        data_hoje=data_hoje,
        categorias=categorias
    )


# ✅ Cadastro de usuário
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:  # Redireciona se já estiver logado
        return redirect(url_for("home"))
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        # ✅ --- INÍCIO DA NOVA LÓGICA DE VALIDAÇÃO DE SENHA ---
        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "error")
            return render_template("cadastro.html")

        if not any(char.isdigit() for char in senha):
            flash("A senha deve conter pelo menos um número.", "error")
            return render_template("cadastro.html")

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("Este e-mail já está cadastrado.", "error")
            return render_template("cadastro.html")

        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


# ✅ Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # Redireciona se já estiver logado
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("home"))
        else:
            flash("Email ou senha incorretos.", "danger")
    return render_template("login.html")


# ✅ Logout
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("inicio"))


# ✅ Nova rota para solicitar redefinição de senha
@app.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            # Gera um token seguro para o ID do usuário, com um 'salt' para segurança extra.
            # O token terá um tempo de validade padrão (3600 segundos = 1 hora)
            token = s.dumps(usuario.id, salt='password-reset-salt')

            reset_link = url_for('redefinir_senha', token=token, _external=True)
            print(f"\n--- LINK DE REDEFINIÇÃO DE SENHA PARA {email} ---\n{reset_link}\n------------------------------------------------\n")

            flash("Se o e-mail estiver cadastrado, um link de redefinição foi enviado para ele.", "info")
            return redirect(url_for('login'))  # Redireciona para o login após a mensagem

        flash("Se o e-mail estiver cadastrado, um link de redefinição foi enviado para ele.", "info")
        return render_template("esqueci_senha.html")  # Renderiza novamente a página para mostrar a mensagem

    return render_template("esqueci_senha.html")


# ✅ Nova rota para redefinir a senha
@app.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    try:
        # Tenta decodificar o token. max_age define a validade (em segundos), 1 hora.
        user_id = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token válido por 1 hora
    except Exception:
        # Se o token for inválido, expirou ou foi adulterado
        flash("Link de redefinição de senha inválido ou expirado. Por favor, solicite um novo.", "error")
        return redirect(url_for('esqueci_senha'))

    usuario = Usuario.query.get(user_id)
    if not usuario:
        # Se o usuário não for encontrado (mesmo que o token seja válido)
        flash("O usuário associado a este link não foi encontrado.", "error")
        return redirect(url_for('esqueci_senha'))

    if request.method == "POST":
        nova_senha = request.form.get("nova_senha")
        confirmar_senha = request.form.get("confirmar_senha")

        # Validação da nova senha (reutilizando a lógica do cadastro)
        if len(nova_senha) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres.", "error")
            return render_template("redefinir_senha.html", token=token)

        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem.", "error")
            return render_template("redefinir_senha.html", token=token)

        # Atualiza a senha do usuário
        usuario.set_senha(nova_senha)
        db.session.commit()

        flash("Sua senha foi redefinida com sucesso! Faça login com a nova senha.", "success")
        return redirect(url_for('login'))

    # Se for um GET (primeira vez acessando o link), apenas renderiza o formulário
    return render_template("redefinir_senha.html", token=token)


# ✅ Adicionar tarefa
@app.route("/adicionar", methods=["POST"])
@login_required
def adicionar():
    # 'tarefa' deve vir do campo 'name="tarefa"' no HTML
    titulo = request.form["tarefa"]
    prazo_str = request.form.get("prazo")
    categoria = request.form.get("categoria")

    prazo = datetime.strptime(prazo_str, "%Y-%m-%d").date() if prazo_str else None

    nova = Tarefa(
        titulo=titulo,  # Usando 'titulo' para corresponder ao modelo
        prazo=prazo,
        categoria=categoria,
        usuario_id=current_user.id
    )
    db.session.add(nova)
    db.session.commit()
    flash("Tarefa adicionada com sucesso!", "success")
    return redirect(url_for("home"))


# ✅ Concluir tarefa
@app.route("/concluir/<int:tarefa_id>", methods=["POST"])
@login_required
def concluir(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if tarefa.usuario_id != current_user.id:  # Garante que o usuário só possa manipular suas próprias tarefas
        flash("Você não tem permissão para realizar esta ação.", "danger")
        return redirect(url_for("home"))
    tarefa.concluida = True
    db.session.commit()
    flash("Tarefa concluída!", "success")
    return redirect(url_for("home"))


# ✅ Desfazer tarefa
@app.route("/desfazer/<int:tarefa_id>", methods=["POST"])
@login_required
def desfazer(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if tarefa.usuario_id != current_user.id:
        flash("Você não tem permissão para realizar esta ação.", "danger")
        return redirect(url_for("home"))
    tarefa.concluida = False
    db.session.commit()
    flash("Tarefa desfeita!", "info")
    return redirect(url_for("home"))


# ✅ Remover tarefa
@app.route("/remover/<int:tarefa_id>", methods=["POST"])
@login_required
def remover(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if tarefa.usuario_id != current_user.id:
        flash("Você não tem permissão para realizar esta ação.", "danger")
        return redirect(url_for("home"))
    db.session.delete(tarefa)
    db.session.commit()
    flash("Tarefa removida!", "warning")
    return redirect(url_for("home"))


# ✅ Editar tarefa
@app.route("/editar/<int:tarefa_id>", methods=["GET", "POST"])
@login_required
def editar(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if tarefa.usuario_id != current_user.id:
        flash("Você não tem permissão para realizar esta ação.", "danger")
        return redirect(url_for("home"))
    if request.method == "POST":
        tarefa.titulo = request.form["titulo"]
        tarefa.prazo = datetime.strptime(request.form["prazo"], "%Y-%m-%d").date() if request.form["prazo"] else None
        tarefa.categoria = request.form["categoria"]
        db.session.commit()
        flash("Tarefa atualizada com sucesso!", "success")
        return redirect(url_for("home"))
    return render_template("editar.html", tarefa=tarefa)


# ✅ Atualizar tarefa
@app.route("/atualizar/<int:tarefa_id>", methods=["POST"])
@login_required
def atualizar(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if tarefa.usuario_id != current_user.id:
        flash("Você não tem permissão para realizar esta ação.", "danger")
        return redirect(url_for("home"))
    tarefa.titulo = request.form.get("tarefa")  # ✅ Acesso ao campo 'tarefa' do HTML
    prazo_str = request.form.get("prazo")
    tarefa.prazo = datetime.strptime(prazo_str, "%Y-%m-%d").date() if prazo_str else None
    tarefa.categoria = request.form.get("categoria")
    db.session.commit()
    flash("Tarefa atualizada com sucesso!", "success")
    return redirect(url_for("home"))


@app.route('/')
def index():
    current_year = datetime.now().year
    return render_template('index.html', current_year=current_year)


# ✅ Rodar app
if __name__ == "__main__":
    app.run(debug=True)
