# 🍔 Junior's Food - Sistema de Delivery e Pedidos Online

[![Licença](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Ativo-brightgreen.svg)]()

## 📋 Sobre o Projeto

O **Junior's Food** é um sistema completo de cardapio e pedidos online desenvolvido especificamente para uma lanchonete da minha cidade. O projeto oferece uma solução integrada que permite aos clientes navegar pelo cardápio, realizar pedidos e fazer o acompanhamento em tempo real, enquanto oferece aos administradores ferramentas eficientes para gerenciar pedidos, produtos e usuários.

## ✨ Funcionalidades Principais

### 👥 **Para Clientes**
- 🔐 **Sistema de Login/Cadastro** - Autenticação segura com validação
- 📱 **Cardápio Digital Interativo** - Navegação por categorias (Lanches, Pizzas, Bebidas, Sobremesas, Porções)
- 🛒 **Carrinho de Compras Inteligente** - Adição/remoção de itens com cálculo automático
- 📊 **Acompanhamento de Pedidos** - Visualização do status em tempo real
- 👤 **Perfil do Usuário** - Gestão de dados pessoais e histórico de pedidos
- 📍 **Gestão de Endereços** - Múltiplos endereços de entrega
- 💳 **Múltiplas Formas de Pagamento** - PIX e outras opções
- 🔍 **Busca de Produtos** - Sistema de busca integrada

### 🛠️ **Para Administradores**
- 📋 **Gestão Completa de Pedidos** - Visualização e controle de todos os pedidos
- 🔄 **Sistema de Status** - Atualização de status (Pendente → Em Preparação → Em Entrega → Concluído)
- 📊 **Dashboard Administrativo** - Interface intuitiva para gestão
- 🗂️ **Organização Temporal** - Filtragem por pedidos mais recentes/antigos
- ❌ **Gestão de Produtos** - Controle completo do cardápio
- 👥 **Gestão de Usuários** - Administração de contas e dados

## 🛠️ Tecnologias Utilizadas

- **Backend**: [Python](https://python.org/) com framework web
- **Banco de Dados**: [SQLite](https://sqlite.org/) - Banco de dados leve e eficiente
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Design**: Interface responsiva e intuitiva
- **Autenticação**: Sistema de login seguro com sessões
- **Validação**: Sistema de validação de formulários em tempo real

## 🚀 Getting Started

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.8 ou superior
- Navegador web moderno
- Servidor web local (opcional para desenvolvimento)

### Instalação e Configuração

1. **Clone o repositório**
   ```bash
   git clone https://github.com/RyanMarcelinos/juniorsfood.git
   cd juniorsfood
   ```

2. **Configure o ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados**
   ```bash
   python models.py 
   ```

5. **Execute a aplicação**
   ```bash
   python app.py 
   ```

6. **Acesse o sistema**
   Abra seu navegador e acesse: `http://localhost:8000`

## 🎮 Conta de Teste

Para testar o sistema, utilize as credenciais de administrador:

- **Email**: admin@juniorfood.com
- **Senha**: admin123

*Use estas credenciais para explorar todas as funcionalidades administrativas do sistema.*

## 📂 Estrutura do Projeto

```
juniorsfood/
├── static/              # Arquivos estáticos (CSS, JS, imagens)
├── templates/           # Templates HTML
├── instance/            # Banco de dados SQLite
├── models/              # Modelos de dados
└── requirements.txt     # Dependências do projeto
```

## 🔧 Configuração Avançada

### Personalização do Cardápio
- Adicione novos produtos através da interface administrativa
- Configure categorias personalizadas
- Defina preços e descrições
- Upload de imagens dos produtos

### Configuração de Pagamento
- Integração com PIX
- Configuração de outras formas de pagamento
- Definição de taxas de entrega

### Gestão de Entrega
- Configuração de zonas de entrega
- Definição de taxas por região
- Horários de funcionamento

## 🗄️ Modelo de Dados

O sistema utiliza SQLite com as seguintes tabelas principais:

- **Usuários**: Dados de clientes e administradores
- **Produtos**: Catálogo completo de itens
- **Categorias**: Organização de produtos
- **Pedidos**: Histórico e status de pedidos
- **Itens_Pedido**: Detalhamento de cada pedido
- **Endereços**: Endereços de entrega dos usuários

## 🎯 Funcionalidades Avançadas

### Sistema de Notificações
- Confirmação automática de pedidos
- Atualizações de status em tempo real
- Notificações por email (configurável)

### Relatórios e Analytics
- Relatórios de vendas
- Produtos mais pedidos
- Análise de clientes
- Performance de entrega

### Segurança
- Validação de dados no frontend e backend
- Proteção contra SQL injection
- Sessões seguras
- Senhas criptografadas

## 🤝 Contribuição

Contribuições são sempre bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte e Contato

Para suporte técnico ou dúvidas sobre o projeto:

- **Desenvolvedor**: Ryan Marcelinos
- **GitHub**: [@RyanMarcelinos](https://github.com/RyanMarcelinos)

## 🏆 Demonstração

### Funcionalidades em Ação

O Junior's Food oferece uma experiência completa de delivery:

1. **Cliente faz login** → **Navega pelo cardápio** → **Adiciona produtos ao carrinho** → **Finaliza o pedido**
2. **Admin recebe notificação** → **Atualiza status do pedido** → **Cliente acompanha progresso**
3. **Entrega realizada** → **Pedido concluído** → **Feedback coletado**

### Benefícios para o Negócio

- ✅ **Aumento das vendas** através de canal digital
- ✅ **Melhoria da experiência do cliente**
- ✅ **Otimização dos processos operacionais**
- ✅ **Controle completo de pedidos e estoque**
- ✅ **Relatórios para tomada de decisões**

---

<div align="center">

**🍔 Junior's Food - Os melhores lanches da cidade! 🍔**

*Desenvolvido com ❤️ para lanchonetes locais*

[⭐ Star no GitHub](https://github.com/RyanMarcelinos) | [🐛 Reportar Bug](https://github.com/RyanMarcelinos/juniorsfood/issues) | [💡 Solicitar Feature](https://github.com/RyanMarcelinos/juniorsfood/issues)

</div>
