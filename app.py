from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Categoria, Produto, Pedido, PedidoItem, Endereco
from datetime import datetime
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///junior_food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações para upload de imagens
app.config['UPLOAD_FOLDER'] = 'static/uploads/produtos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def check_admin_access():
    if request.endpoint and 'admin_' in request.endpoint:
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('cardapio'))

# Funções de validação
def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_senha(senha):
    return len(senha) >= 6

def validar_preco(preco):
    try:
        valor = float(preco)
        return valor > 0
    except (ValueError, TypeError):
        return False
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Adicionar timestamp para evitar conflitos de nome
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None

# Rotas principais
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('cardapio'))
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('cardapio'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validações
        if not all([username, email, password, confirm_password]):
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('cadastro.html')
        
        if len(username) < 3:
            flash('Nome de usuário deve ter pelo menos 3 caracteres', 'error')
            return render_template('cadastro.html')
        
        if not validar_email(email):
            flash('Email inválido', 'error')
            return render_template('cadastro.html')
        
        if not validar_senha(password):
            flash('A senha deve ter pelo menos 6 caracteres', 'error')
            return render_template('cadastro.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'error')
            return render_template('cadastro.html')
        
        # Verificar se usuário ou email já existem
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já está em uso', 'error')
            return render_template('cadastro.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email já está cadastrado', 'error')
            return render_template('cadastro.html')
        
        # Criar novo usuário
        novo_user = User(username=username, email=email, is_admin=False)
        novo_user.set_password(password)
        
        try:
            db.session.add(novo_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
    
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('cardapio'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()  # Mudei para email
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()  
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('cardapio'))
        else:
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('carrinho', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

@app.route('/cardapio')
@login_required
def cardapio():
    categorias = Categoria.query.filter_by(ativo=True).all()
    carrinho_count = len(session.get('carrinho', []))
    return render_template('cardapio.html', categorias=categorias, carrinho_count=carrinho_count)

@app.route('/api/produtos/<int:categoria_id>')
@login_required
def api_produtos(categoria_id):
    try:
        produtos = Produto.query.filter_by(categoria_id=categoria_id, ativo=True).all()
        produtos_data = []
        for produto in produtos:
            produtos_data.append({
                'id': produto.id,
                'nome': produto.nome,
                'descricao': produto.descricao,
                'preco': produto.preco,
                'imagem': produto.imagem
            })
        return jsonify(produtos_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adicionar_carrinho', methods=['POST'])
@login_required
def adicionar_carrinho():
    try:
        produto_id = request.form.get('produto_id')
        observacao = request.form.get('observacao', '').strip()
        
        if not produto_id:
            return jsonify({'success': False, 'message': 'Produto não especificado'})
        
        produto = Produto.query.filter_by(id=produto_id, ativo=True).first()
        if not produto:
            return jsonify({'success': False, 'message': 'Produto não encontrado'})
        
        carrinho = session.get('carrinho', [])
        
        #ele Verifica se o produto já está no carrinho
        item_existente = next((item for item in carrinho if item['produto_id'] == produto.id), None)
        
        if item_existente:
            item_existente['observacao'] = observacao
        else:
            carrinho.append({
                'produto_id': produto.id,
                'nome': produto.nome,
                'preco': float(produto.preco),
                'observacao': observacao
            })
        
        session['carrinho'] = carrinho
        
        return jsonify({
            'success': True, 
            'message': 'Produto adicionado ao carrinho', 
            'carrinho_count': len(carrinho)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/carrinho')
@login_required
def carrinho():
    carrinho_itens = session.get('carrinho', [])
    total = sum(item['preco'] for item in carrinho_itens)
    return render_template('carrinho.html', carrinho_itens=carrinho_itens, total=total)

@app.route('/remover_carrinho/<int:index>')
@login_required
def remover_carrinho(index):
    carrinho = session.get('carrinho', [])
    if 0 <= index < len(carrinho):
        item_removido = carrinho.pop(index)
        session['carrinho'] = carrinho
        flash(f'{item_removido["nome"]} removido do carrinho', 'success')
    else:
        flash('Item não encontrado no carrinho', 'error')
    return redirect(url_for('carrinho'))

@app.route('/limpar_carrinho')
@login_required
def limpar_carrinho():
    if session.get('carrinho'):
        session.pop('carrinho')
        flash('Carrinho limpo com sucesso', 'success')
    else:
        flash('Carrinho já está vazio', 'info')
    return redirect(url_for('carrinho'))

@app.route('/atualizar_carrinho', methods=['POST'])
@login_required
def atualizar_carrinho():
    try:
        index = int(request.form.get('index'))
        nova_observacao = request.form.get('observacao', '').strip()
        
        carrinho = session.get('carrinho', [])
        if 0 <= index < len(carrinho):
            carrinho[index]['observacao'] = nova_observacao
            session['carrinho'] = carrinho
            return jsonify({'success': True, 'message': 'Observação atualizada'})
        else:
            return jsonify({'success': False, 'message': 'Item não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/finalizar_pedido', methods=['POST'])
@login_required
def finalizar_pedido():
    try:
        carrinho_itens = session.get('carrinho', [])
        if not carrinho_itens:
            flash('Carrinho vazio', 'error')
            return redirect(url_for('carrinho'))
        
        forma_pagamento = request.form.get('forma_pagamento')
        observacao_geral = request.form.get('observacao_geral', '').strip()
        troco_para = request.form.get('troco_para', 0)
        endereco_entrega_id = request.form.get('endereco_entrega_id')
        
        if not forma_pagamento:
            flash('Selecione uma forma de pagamento', 'error')
            return redirect(url_for('carrinho'))
        
        if not endereco_entrega_id:
            flash('Selecione um endereço para entrega', 'error')
            return redirect(url_for('carrinho'))
        
        endereco = Endereco.query.filter_by(id=endereco_entrega_id, user_id=current_user.id).first()
        if not endereco:
            flash('Endereço inválido', 'error')
            return redirect(url_for('carrinho'))
        
        if forma_pagamento == 'dinheiro' and troco_para:
            try:
                troco_para = float(troco_para)
                total = sum(item['preco'] for item in carrinho_itens)
                if troco_para < total:
                    flash('Valor para troco deve ser maior ou igual ao total', 'error')
                    return redirect(url_for('carrinho'))
            except ValueError:
                flash('Valor para troco inválido', 'error')
                return redirect(url_for('carrinho'))
        
        total = sum(item['preco'] for item in carrinho_itens)
        
        pedido = Pedido(
            user_id=current_user.id,
            forma_pagamento=forma_pagamento,
            troco_para=float(troco_para) if troco_para else 0,
            observacao=observacao_geral,
            total=total,
            endereco_entrega_id=int(endereco_entrega_id)
        )
        
        db.session.add(pedido)
        db.session.flush()
        
        for item in carrinho_itens:
            produto = Produto.query.get(item['produto_id'])
            if produto:
                pedido_item = PedidoItem(
                    pedido_id=pedido.id,
                    produto_id=item['produto_id'],
                    quantidade=1,
                    observacao=item.get('observacao', ''),
                    preco_unitario=item['preco']
                )
                db.session.add(pedido_item)
        
        db.session.commit()
        session.pop('carrinho', None)
        
        flash('Pedido realizado com sucesso! Aguarde a preparação.', 'success')
        return redirect(url_for('perfil'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao finalizar pedido: {str(e)}', 'error')
        return redirect(url_for('carrinho'))

@app.route('/perfil')
@login_required
def perfil():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    pedidos = Pedido.query.filter_by(user_id=current_user.id).order_by(Pedido.created_at.desc()).limit(10).all()
    return render_template('perfil.html', pedidos=pedidos)

@app.route('/alterar_senha', methods=['POST'])
@login_required
def alterar_senha():
    if current_user.is_admin:
        flash('Administradores não podem alterar senha pelo perfil', 'error')
        return redirect(url_for('admin_dashboard'))
    
    senha_atual = request.form.get('senha_atual', '')
    nova_senha = request.form.get('nova_senha', '')
    confirmar_senha = request.form.get('confirmar_senha', '')
    
    if not senha_atual or not nova_senha or not confirmar_senha:
        flash('Todos os campos são obrigatórios', 'error')
        return redirect(url_for('perfil'))
    
    if not current_user.check_password(senha_atual):
        flash('Senha atual incorreta', 'error')
        return redirect(url_for('perfil'))
    
    if not validar_senha(nova_senha):
        flash('A nova senha deve ter pelo menos 6 caracteres', 'error')
        return redirect(url_for('perfil'))
    
    if nova_senha != confirmar_senha:
        flash('As novas senhas não coincidem', 'error')
        return redirect(url_for('perfil'))
    
    current_user.set_password(nova_senha)
    db.session.commit()
    
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('perfil'))

@app.route('/meus-enderecos')
@login_required
def meus_enderecos():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    enderecos = Endereco.query.filter_by(user_id=current_user.id).order_by(Endereco.principal.desc()).all()
    return render_template('meus_enderecos.html', enderecos=enderecos)

@app.route('/adicionar-endereco', methods=['POST'])
@login_required
def adicionar_endereco():
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Administradores não podem adicionar endereços'})
    
    cep = request.form.get('cep', '').strip()
    logradouro = request.form.get('logradouro', '').strip()
    numero = request.form.get('numero', '').strip()
    complemento = request.form.get('complemento', '').strip()
    bairro = request.form.get('bairro', '').strip()
    
    if not all([cep, logradouro, numero, bairro]):
        return jsonify({'success': False, 'message': 'Todos os campos obrigatórios são necessários'})
    
    try:
        principal = Endereco.query.filter_by(user_id=current_user.id).count() == 0
        
        endereco = Endereco(
            user_id=current_user.id,
            cep=cep,
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade='Ubarana',
            estado='SP',
            principal=principal
        )
        
        db.session.add(endereco)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Endereço adicionado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao adicionar endereço: {str(e)}'})

@app.route('/definir-endereco-principal/<int:endereco_id>', methods=['POST'])
@login_required
def definir_endereco_principal(endereco_id):
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        Endereco.query.filter_by(user_id=current_user.id).update({'principal': False})
        
        endereco = Endereco.query.filter_by(id=endereco_id, user_id=current_user.id).first()
        if endereco:
            endereco.principal = True
            db.session.commit()
            return jsonify({'success': True, 'message': 'Endereço principal definido com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Endereço não encontrado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao definir endereço principal: {str(e)}'})

@app.route('/excluir-endereco/<int:endereco_id>', methods=['POST'])
@login_required
def excluir_endereco(endereco_id):
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        endereco = Endereco.query.filter_by(id=endereco_id, user_id=current_user.id).first()
        if endereco:
            db.session.delete(endereco)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Endereço excluído com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Endereço não encontrado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir endereço: {str(e)}'})

# Rotas administrativas
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Acesso negado', 'error')
        return redirect(url_for('cardapio'))
    
    total_pedidos = Pedido.query.count()
    pedidos_pendentes = Pedido.query.filter_by(status='pendente').count()
    pedidos_preparando = Pedido.query.filter_by(status='preparando').count()
    total_usuarios = User.query.count()
    pedidos_recentes = Pedido.query.order_by(Pedido.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_pedidos=total_pedidos,
                         pedidos_pendentes=pedidos_pendentes,
                         pedidos_preparando=pedidos_preparando,
                         total_usuarios=total_usuarios,
                         pedidos_recentes=pedidos_recentes)  # Esssa variiavel tava faltando

@app.route('/admin/criar-pedidos-teste', methods=['GET', 'POST'])
@login_required
def admin_criar_pedidos_teste():
    if not current_user.is_admin:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Acesso negado'})
        flash('Acesso negado', 'error')
        return redirect(url_for('cardapio'))
    
    if request.method == 'GET':
        return render_template('admin_criar_pedidos_teste.html')
    
    # Método POST - pra criar os pedidos
    try:
        usuarios = User.query.filter_by(is_admin=False).limit(5).all()
        if not usuarios:
            return jsonify({'success': False, 'message': 'É necessário ter usuários não-admin no sistema'})
        
        produtos = Produto.query.filter_by(ativo=True).all()
        if not produtos:
            return jsonify({'success': False, 'message': 'É necessário ter produtos ativos no sistema'})
        
        # Status possíveis para os pedidos
        status_list = ['pendente', 'preparando', 'pronto', 'entregue', 'cancelado']
        formas_pagamento = ['dinheiro', 'cartao', 'pix']
        
        from datetime import datetime, timedelta
        import random
        
        pedidos_criados = 0
        
        for i in range(30):
            usuario = random.choice(usuarios)
            
            dias_atras = random.randint(0, 30)
            horas_atras = random.randint(0, 23)
            minutos_atras = random.randint(0, 59)
            data_pedido = datetime.now() - timedelta(days=dias_atras, hours=horas_atras, minutes=minutos_atras)
            
            pesos_status = [0.3, 0.3, 0.2, 0.15, 0.05]
            status = random.choices(status_list, weights=pesos_status)[0]
            
            forma_pagamento = random.choice(formas_pagamento)
            

            troco_para = 0.0
            if forma_pagamento == 'dinheiro' and random.random() > 0.5:  
                troco_para = float(random.randint(50, 100))
            
            observacao = ""
            if random.random() < 0.3:
                observacoes = [
                    "Sem cebola por favor",
                    "Entregar na portaria",
                    "Embalar para viagem",
                    "Adicionar ketchup e mostarda",
                    "Quero o lanche bem passado",
                    "Entregar o mais rápido possível",
                    "Favor não incluir maionese",
                    "Trocar batata por onion rings"
                ]
                observacao = random.choice(observacoes)
            
            # PRIMEIRO calcular o total antes de criar o pedido
            total_pedido = 0.0
            
            num_itens = random.randint(1, 4)
            itens_simulados = []
            
            for j in range(num_itens):
                produto = random.choice(produtos)
                quantidade = random.randint(1, 3)
                subtotal = produto.preco * quantidade
                total_pedido += subtotal
                
                itens_simulados.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'subtotal': subtotal
                })
            
            # AGORA criar o pedido com o total calculado
            pedido = Pedido(
                user_id=usuario.id,
                forma_pagamento=forma_pagamento,
                troco_para=troco_para,
                observacao=observacao,
                status=status,
                total=total_pedido,  
                created_at=data_pedido
            )
            
            db.session.add(pedido)
            db.session.flush()  
            
            # Agora criar os itens reais do pedido
            for item_simulado in itens_simulados:
                pedido_item = PedidoItem(
                    pedido_id=pedido.id,
                    produto_id=item_simulado['produto'].id,
                    quantidade=item_simulado['quantidade'],
                    observacao=f"Observação do item" if random.random() < 0.2 else "",
                    preco_unitario=item_simulado['produto'].preco
                )
                db.session.add(pedido_item)
            
            pedidos_criados += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'{pedidos_criados} pedidos de teste criados com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar pedidos de teste: {str(e)}'}), 500

@app.route('/admin/pedidos')
@login_required
def admin_pedidos():
    if not current_user.is_admin:
        flash('Acesso negado', 'error')
        return redirect(url_for('cardapio'))
    
    page = request.args.get('page', 1, type=int)
    ordenacao = request.args.get('ordenacao', 'mais_novos')
    
    if ordenacao == 'mais_antigos':
        order_by = Pedido.created_at.asc()
    else:  
        order_by = Pedido.created_at.desc()
    
    pedidos_query = Pedido.query.order_by(order_by)
    pagination = pedidos_query.paginate(page=page, per_page=10, error_out=False)
    pedidos = pagination.items
    
    return render_template('admin_pedidos.html', 
                         pedidos=pedidos, 
                         pagination=pagination,
                         ordenacao=ordenacao)

@app.route('/admin/pedido/<int:pedido_id>')
@login_required
def admin_detalhes_pedido(pedido_id):
    if not current_user.is_admin:
        flash('Acesso negado', 'error')
        return redirect(url_for('cardapio'))
    
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin_detalhes_pedido.html', pedido=pedido)

@app.route('/admin/pedido/<int:pedido_id>/status', methods=['POST'])
@login_required
def admin_atualizar_status(pedido_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    pedido = Pedido.query.get_or_404(pedido_id)
    novo_status = request.json.get('status')
    
    if novo_status in ['pendente', 'preparando', 'pronto', 'entregue', 'cancelado']:
        pedido.status = novo_status
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status atualizado'})
    
    return jsonify({'success': False, 'message': 'Status inválido'})

@app.route('/admin/pedido/<int:pedido_id>/excluir', methods=['POST'])
@login_required
def admin_excluir_pedido(pedido_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        for item in pedido.itens:
            db.session.delete(item)
        
        db.session.delete(pedido)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pedido excluído com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir pedido: {str(e)}'}), 500

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.is_admin:
        flash('Acesso negado', 'error')
        return redirect(url_for('cardapio'))
    
    usuarios = User.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/produtos')
@login_required
def admin_produtos():
    if not current_user.is_admin:
        flash('Acesso negado', 'error')
        return redirect(url_for('cardapio'))
    
    categorias = Categoria.query.all()
    produtos = Produto.query.all()
    return render_template('admin_produtos.html', categorias=categorias, produtos=produtos)

@app.route('/admin/produto/adicionar', methods=['POST'])
@login_required
def admin_adicionar_produto():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    preco = request.form.get('preco')
    categoria_id = request.form.get('categoria_id')
    imagem = request.files.get('imagem')
    
    if not all([nome, preco, categoria_id]):
        return jsonify({'success': False, 'message': 'Todos os campos obrigatórios são necessários'})
    
    if not validar_preco(preco):
        return jsonify({'success': False, 'message': 'Preço inválido'})
    
    try:
        imagem_filename = None
        if imagem and imagem.filename:
            imagem_filename = save_image(imagem)
        
        produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=float(preco),
            categoria_id=int(categoria_id),
            imagem=imagem_filename
        )
        db.session.add(produto)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Produto adicionado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao adicionar produto: {str(e)}'})

@app.route('/admin/produto/<int:produto_id>/editar', methods=['POST'])
@login_required
def admin_editar_produto(produto_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    produto = Produto.query.get_or_404(produto_id)
    
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    preco = request.form.get('preco')
    categoria_id = request.form.get('categoria_id')
    imagem = request.files.get('imagem')
    remover_imagem = request.form.get('remover_imagem') == 'true'
    
    if not all([nome, preco, categoria_id]):
        return jsonify({'success': False, 'message': 'Todos os campos obrigatórios são necessários'})
    
    if not validar_preco(preco):
        return jsonify({'success': False, 'message': 'Preço inválido'})
    
    try:
        produto.nome = nome
        produto.descricao = descricao
        produto.preco = float(preco)
        produto.categoria_id = int(categoria_id)
        
        if remover_imagem and produto.imagem:
            old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], produto.imagem)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
            produto.imagem = None
        elif imagem and imagem.filename:
            if produto.imagem:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], produto.imagem)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            imagem_filename = save_image(imagem)
            produto.imagem = imagem_filename
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Produto atualizado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar produto: {str(e)}'})

@app.route('/admin/produto/<int:produto_id>/toggle', methods=['POST'])
@login_required
def admin_toggle_produto(produto_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    produto = Produto.query.get_or_404(produto_id)
    produto.ativo = not produto.ativo
    db.session.commit()
    
    status = 'ativado' if produto.ativo else 'desativado'
    return jsonify({'success': True, 'message': f'Produto {status} com sucesso'})

@app.route('/admin/categorias')
@login_required
def admin_categorias():
    if not current_user.is_admin:
        flash('Acesso negado', 'error')
        return redirect(url_for('cardapio'))
    
    categorias = Categoria.query.all()
    return render_template('admin_categorias.html', categorias=categorias)

@app.route('/admin/categoria/adicionar', methods=['POST'])
@login_required
def admin_adicionar_categoria():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    
    if not nome:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'})
    
    if len(nome) < 2:
        return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 2 caracteres'})
    
    try:
        categoria = Categoria(nome=nome, descricao=descricao)
        db.session.add(categoria)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Categoria adicionada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao adicionar categoria: {str(e)}'})

@app.route('/admin/categoria/<int:categoria_id>/editar', methods=['POST'])
@login_required
def admin_editar_categoria(categoria_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    categoria = Categoria.query.get_or_404(categoria_id)
    
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    
    if not nome:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'})
    
    if len(nome) < 2:
        return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 2 caracteres'})
    
    try:
        categoria.nome = nome
        categoria.descricao = descricao
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Categoria atualizada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar categoria: {str(e)}'})

@app.route('/admin/categoria/<int:categoria_id>/toggle', methods=['POST'])
@login_required
def admin_toggle_categoria(categoria_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    categoria = Categoria.query.get_or_404(categoria_id)

    if categoria.ativo:
        produtos_ativos = Produto.query.filter_by(categoria_id=categoria_id, ativo=True).count()
        if produtos_ativos > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível desativar categoria com {produtos_ativos} produto(s) ativo(s)'
            })
    
    categoria.ativo = not categoria.ativo
    db.session.commit()
    
    status = 'ativada' if categoria.ativo else 'desativada'
    return jsonify({'success': True, 'message': f'Categoria {status} com sucesso'})

# API endpoints
@app.route('/api/carrinho_count')
@login_required
def api_carrinho_count():
    carrinho_itens = session.get('carrinho', [])
    return jsonify({'count': len(carrinho_itens)})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Inicialização do banco de dados
def init_db():
    with app.app_context():
        db.drop_all()  
        db.create_all()  
        
        # Criar usuário admin padrão se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@juniorfood.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            categorias = [
                Categoria(nome='Lanches', descricao='Deliciosos lanches artesanais'),
                Categoria(nome='Pizzas', descricao='Pizzas saborosas de diversos sabores'),
                Categoria(nome='Bebidas', descricao='Bebidas geladas e refrescantes'),
                Categoria(nome='Sobremesas', descricao='Doces e sobremesas irresistíveis'),
                Categoria(nome='Porções', descricao='Porções para compartilhar')
            ]
            
            for categoria in categorias:
                db.session.add(categoria)
            
            produtos = [
                Produto(nome='X-Burger', descricao='Pão, hambúrguer, queijo, alface, tomate', preco=15.90, categoria_id=1),
                Produto(nome='X-Bacon', descricao='Pão, hambúrguer, queijo, bacon, alface, tomate', preco=18.90, categoria_id=1),
                Produto(nome='X-Tudo', descricao='Pão, 2 hambúrgueres, queijo, presunto, bacon, ovo, alface, tomate', preco=22.90, categoria_id=1),
                Produto(nome='Pizza Calabresa', descricao='Molho, queijo, calabresa, cebola, azeitonas', preco=35.90, categoria_id=2),
                Produto(nome='Pizza Frango Catupiry', descricao='Molho, queijo, frango desfiado, catupiry', preco=38.90, categoria_id=2),
                Produto(nome='Coca-Cola', descricao='Lata 350ml', preco=5.90, categoria_id=3),
                Produto(nome='Suco Natural', descricao='Laranja, limão ou abacaxi 500ml', preco=8.90, categoria_id=3),
                Produto(nome='Sorvete', descricao='Casquinha com 2 bolas', preco=8.90, categoria_id=4),
                Produto(nome='Brownie', descricao='Brownie com sorvete e calda de chocolate', preco=12.90, categoria_id=4),
                Produto(nome='Batata Frita', descricao='Porção de batata frita crocante', preco=15.90, categoria_id=5),
                Produto(nome='Onion Rings', descricao='Anéis de cebola empanados', preco=14.90, categoria_id=5),
            ]
            
            for produto in produtos:
                db.session.add(produto)
            
            db.session.commit()
            print("Banco de dados JUNIOR'S FOOD inicializado com dados de exemplo!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)