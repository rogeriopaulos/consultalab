# Sistema de Toasts - Bootstrap 5

## Implementação

O sistema de mensagens da aplicação foi migrado de alerts para toasts do Bootstrap 5, oferecendo uma experiência de usuário mais moderna e não-intrusiva.

## Funcionalidades

### 1. Toasts Automáticos
- Todas as mensagens Django são automaticamente convertidas em toasts
- Posicionados no canto superior direito da tela
- Auto-hide após 5 segundos
- Suporte a todos os tipos de mensagem: success, error/danger, warning, info

### 2. Ícones por Tipo
- **Success**: ✓ (check-circle-fill)
- **Error/Danger**: ⚠️ (exclamation-triangle-fill)
- **Warning**: ⚠️ (exclamation-circle-fill)
- **Info**: ℹ️ (info-circle-fill)
- **Default**: 🔔 (bell-fill)

### 3. API JavaScript

#### Criar toast dinamicamente:
```javascript
// Sintaxe básica
showToast('Mensagem aqui', 'success');

// Com duração customizada
showToast('Mensagem aqui', 'warning', 8000);

// Tipos disponíveis: 'success', 'danger', 'error', 'warning', 'info', 'primary'
```

#### Inicializar toasts manualmente:
```javascript
initializeToasts();
```

### 4. Estilos Customizados
- Cores personalizadas seguindo a paleta da aplicação
- Animações suaves de entrada e saída
- Responsivo em dispositivos móveis
- Z-index alto para garantir visibilidade

## Templates Modificados

1. **base.html**: Sistema principal de toasts
2. **entrance.html**: Toasts para páginas de autenticação
3. **alert.html**: Template de alert do allauth convertido para toast

## CSS Personalizado

Adicionados estilos específicos no `project.css`:
- `.toast-container`: Container principal
- `.toast`: Estilos base
- `.text-bg-*`: Variantes de cor
- Animações de entrada e saída

## JavaScript

O arquivo `project.js` contém:
- `initializeToasts()`: Inicializa todos os toasts na página
- `showToast()`: Cria toasts dinamicamente
- `createToastContainer()`: Cria container se não existir
- `getToastIcon()`: Retorna ícone apropriado por tipo

## Benefícios

1. **Não-Intrusivo**: Não bloqueia conteúdo da página
2. **Acessível**: Suporte a screen readers com ARIA
3. **Responsivo**: Funciona bem em todos os dispositivos
4. **Consistente**: Design unificado em toda aplicação
5. **Flexível**: API para criação dinâmica de toasts
