from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True, cascade='all, delete-orphan')
    enderecos = db.relationship('Endereco', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Endereco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    logradouro = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False, default='Ubarana')
    estado = db.Column(db.String(2), nullable=False, default='SP')
    principal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pedidos = db.relationship('Pedido', backref='endereco_entrega', lazy=True)
    
    def __repr__(self):
        return f'<Endereco {self.logradouro}, {self.numero}>'

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    produtos = db.relationship('Produto', backref='categoria', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200))  
    ativo = db.Column(db.Boolean, default=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pedido_itens = db.relationship('PedidoItem', backref='produto', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Produto {self.nome}>'

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    endereco_entrega_id = db.Column(db.Integer, db.ForeignKey('endereco.id'))  
    status = db.Column(db.String(20), default='pendente')  # pendente, preparando, pronto, entregue, cancelado
    forma_pagamento = db.Column(db.String(20), nullable=False)  # cartao, dinheiro, pix
    troco_para = db.Column(db.Float, default=0)
    observacao = db.Column(db.Text)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    itens = db.relationship('PedidoItem', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pedido {self.id} - {self.status}>'

class PedidoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    observacao = db.Column(db.Text)
    preco_unitario = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PedidoItem {self.id} - {self.quantidade}x {self.produto.nome}>'