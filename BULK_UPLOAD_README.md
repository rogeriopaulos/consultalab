# Funcionalidade de Upload em Lote para Consultas Pix

## Resumo da Implementação

Esta funcionalidade permite a submissão de um arquivo TXT para criação de múltiplas requisições de consulta Pix de forma automatizada e eficiente, conforme especificado na issue #31.

## Arquivos Modificados/Criados

### 1. Formulários (`consultalab/bacen/forms.py`)
- **Adicionado**: Classe `BulkRequestForm`
  - Validação de arquivo TXT
  - Processamento e parsing do conteúdo
  - Validação de CPF/CNPJ usando `validate_docbr`
  - Tratamento de erros linha por linha

### 2. Views (`consultalab/bacen/views.py`)
- **Adicionado**: `BulkRequestFormView` - Exibe o modal de upload
- **Adicionado**: `BulkRequestUploadView` - Processa o arquivo e cria as requisições

### 3. URLs (`consultalab/bacen/urls.py`)
- **Adicionado**: `/bulk-request/` - Rota para exibir o formulário
- **Adicionado**: `/bulk-request/upload/` - Rota para processar o upload

### 4. Templates
- **Criado**: `templates/bacen/partials/bulk_request_modal.html` - Modal de upload
- **Criado**: `templates/bacen/partials/bulk_request_result.html` - Resultado do processamento
- **Modificado**: `templates/pages/home.html` - Adicionado botão "Importar Lote"

### 5. Testes
- **Criado**: `consultalab/bacen/tests/test_bulk_request_form.py` - Testes unitários

## Como Usar

### 1. Acesso à Funcionalidade
1. Faça login na aplicação
2. Na página inicial, localize o card "Consulta Pix"
3. Clique no botão verde "Importar Lote"

### 2. Formato do Arquivo TXT

O arquivo deve seguir o seguinte formato:
```
tipo_requisicao,termo_busca,motivo,referencia
```

**Campos:**
- **tipo_requisicao**: `1` (Pix CPF/CNPJ) ou `2` (Pix Chave)
- **termo_busca**: CPF/CNPJ (apenas números) ou Chave Pix
- **motivo**: Descrição do motivo (obrigatório)
- **referencia**: Campo opcional para referência interna

**Separadores aceitos:**
- Vírgula (`,`)
- Ponto e vírgula (`;`)

### 3. Exemplos de Linhas Válidas

```txt
1,12345678901,BO 123/2023,REF001
1,12345678000199,IPL 456/2023
2,usuario@email.com,Caso LAB-LD 789,REF002
2,11987654321,RIF 101112
```

### 4. Restrições

- **Tamanho máximo**: 5MB
- **Extensão**: Apenas `.txt`
- **Codificação**: UTF-8 ou Latin-1
- **Permissões**: Usuário deve ter permissão `can_request_pix`

## Validações Implementadas

### 1. Validação de Arquivo
- Extensão deve ser `.txt`
- Tamanho máximo de 5MB
- Codificação válida (UTF-8/Latin-1)

### 2. Validação de Conteúdo
- Mínimo de 3 campos por linha (tipo_requisicao, termo_busca, motivo)
- `tipo_requisicao` deve ser `1` ou `2`
- `termo_busca` e `motivo` são obrigatórios
- Para tipo `1`: CPF/CNPJ deve ser válido (usando `validate_docbr`)

### 3. Validação de Permissões
- Usuário deve ter permissão `users.can_request_pix`

## Tratamento de Erros

### 1. Linhas Válidas
- São processadas e salvas como `RequisicaoBacen`
- Exibidas no resultado como "Requisições Criadas"

### 2. Linhas Inválidas
- São catalogadas com o número da linha e motivo do erro
- Exibidas em tabela no resultado
- Não interrompem o processamento das demais linhas

### 3. Tipos de Erro Detectados
- Campos insuficientes
- Tipo de requisição inválido
- CPF/CNPJ inválido
- Campos obrigatórios vazios
- Usuário sem permissão

## Tecnologias Utilizadas

- **Django Forms**: Para validação e processamento
- **HTMX**: Para interações dinâmicas sem reload
- **Bootstrap**: Para interface responsiva
- **validate_docbr**: Para validação de CPF/CNPJ
- **PostgreSQL**: Para persistência dos dados

## Segurança

- Validação de permissões por usuário
- Sanitização do conteúdo do arquivo
- Transações atômicas para consistência dos dados
- Tratamento de exceções para evitar crashes

## Performance

- Processamento em lote otimizado
- Transações atômicas para múltiplas inserções
- Validação em memória antes da persistência
- Feedback detalhado do progresso

## Exemplo de Arquivo para Teste

Foi criado um arquivo de exemplo em `/exemplo_upload.txt` com dados válidos para teste da funcionalidade.

## Próximos Passos

1. **Testes manuais**: Validar a interface e funcionalidade
2. **Testes de performance**: Com arquivos grandes
3. **Melhorias de UX**: Progresso em tempo real, preview do arquivo
4. **Logs de auditoria**: Rastreamento de uploads em lote
