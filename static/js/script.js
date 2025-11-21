class JuniorsLanchesSystem {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.updateCartBadgeCount(); // Nome corrigido
    }

    setupEventListeners() {
        console.log('Sistema Juniors Food inicializado');
    }

    initializeComponents() {
        this.initializeTooltips();
        this.initializeFormValidations();
    }

    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initializeFormValidations() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    async updateCartBadgeCount() {
        try {
            const response = await fetch('/api/carrinho_count');
            const data = await response.json();
            
            const badges = document.querySelectorAll('#carrinho-badge, #carrinho-badge-header, #carrinho-badge-floating');
            badges.forEach(badge => {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline';
                } else {
                    badge.style.display = 'none';
                }
            });
        } catch (error) {
            console.error('Erro ao atualizar badge:', error);
        }
    }
}

class CarrinhoManager {
    constructor() {
        this.carrinhoCount = 0;
    }

    async adicionarItem(produtoId, observacao = '') {
        try {
            const formData = new FormData();
            formData.append('produto_id', produtoId);
            formData.append('observacao', observacao);

            const response = await fetch('/adicionar_carrinho', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.mostrarMensagem('Sucesso!', 'Produto adicionado ao carrinho.', 'success');
                this.updateCartBadgeCount(data.carrinho_count);
                return true;
            } else {
                this.mostrarMensagem('Erro!', data.message, 'error');
                return false;
            }
        } catch (error) {
            console.error('Erro ao adicionar item:', error);
            this.mostrarMensagem('Erro!', 'Erro ao adicionar produto ao carrinho.', 'error');
            return false;
        }
    }

    async updateCartBadgeCount(count = null) {
        try {
            if (count === null) {
                const response = await fetch('/api/carrinho_count');
                const data = await response.json();
                count = data.count;
            }

            this.carrinhoCount = count;
            
            const badges = document.querySelectorAll('#carrinho-badge, #carrinho-badge-header, #carrinho-badge-floating');
            badges.forEach(badge => {
                if (count > 0) {
                    badge.textContent = count;
                    badge.style.display = 'inline';
                } else {
                    badge.style.display = 'none';
                }
            });

            const carrinhoResumo = document.getElementById('carrinho-resumo');
            if (carrinhoResumo) {
                if (count > 0) {
                    carrinhoResumo.innerHTML = `<span class="badge bg-warning text-dark fs-6">${count} itens</span>`;
                } else {
                    carrinhoResumo.innerHTML = `<span class="text-muted">Vazio</span>`;
                }
            }
        } catch (error) {
            console.error('Erro ao atualizar badge:', error);
        }
    }

    mostrarMensagem(titulo, mensagem, tipo = 'info') {
        // CTentiva de criar essa bosta de alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${tipo === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <strong>${titulo}</strong> ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 5000);
        }
    }
}

// Funções globais
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validarSenha(senha) {
    return senha.length >= 6;
}

// Inicialização do sistema quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    window.juniorsSystem = new JuniorsLanchesSystem();
    
    window.carrinhoManager = new CarrinhoManager();
    
    const formaPagamentoSelect = document.querySelector('select[name="forma_pagamento"]');
    if (formaPagamentoSelect) {
        formaPagamentoSelect.addEventListener('change', function() {
            const trocoField = document.getElementById('troco-field');
            if (this.value === 'dinheiro') {
                if (trocoField) trocoField.style.display = 'block';
            } else {
                if (trocoField) trocoField.style.display = 'none';
            }
        });
    }

    console.log('Sistema Juniors Food carregado com sucesso!');
});


function atualizarContadorCarrinho() {
    if (window.carrinhoManager) {
        window.carrinhoManager.updateCartBadgeCount();
    }
}