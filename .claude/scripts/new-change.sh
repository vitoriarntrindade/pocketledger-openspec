#!/bin/bash
# Script para criar uma nova mudança seguindo o padrão de desenvolvimento

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para mostrar erro
error() {
    echo -e "${RED}✗ Erro: $1${NC}" >&2
    exit 1
}

# Função para mostrar sucesso
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Função para mostrar info
info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Verificações iniciais
if [ ! -f "README.md" ]; then
    error "Não está no diretório root do projeto"
fi

if ! command -v git &> /dev/null; then
    error "Git não está instalado"
fi

# Solicitar entrada do usuário
echo ""
echo "=== Criar Nova Mudança ==="
echo ""

# Tipo de mudança
echo "Tipo de mudança:"
echo "  1. feature    - Nova funcionalidade"
echo "  2. bugfix     - Correção de bug"
echo "  3. security   - Patch de segurança"
echo "  4. refactor   - Refatoração técnica"
echo "  5. perf       - Otimização de performance"
echo "  6. docs       - Documentação"
echo "  7. chore      - Tarefas administrativas"
read -p "Escolha (1-7): " type_choice

case $type_choice in
    1) CHANGE_TYPE="feature" ;;
    2) CHANGE_TYPE="bugfix" ;;
    3) CHANGE_TYPE="security" ;;
    4) CHANGE_TYPE="refactor" ;;
    5) CHANGE_TYPE="perf" ;;
    6) CHANGE_TYPE="docs" ;;
    7) CHANGE_TYPE="chore" ;;
    *) error "Opção inválida" ;;
esac

# Slug descritivo
read -p "Slug (ex: audit-logging): " slug
slug=$(echo "$slug" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

if [ -z "$slug" ]; then
    error "Slug não pode estar vazio"
fi

# Data
DATE=$(date +%Y-%m-%d)
CHANGE_NAME="${DATE}-${CHANGE_TYPE}-${slug}"
CHANGE_DIR="openspec/changes/active/${CHANGE_NAME}"

# Verificar se já existe
if [ -d "$CHANGE_DIR" ]; then
    error "Mudança '$CHANGE_NAME' já existe em $CHANGE_DIR"
fi

# Criar diretório
mkdir -p "$CHANGE_DIR"
success "Diretório criado: $CHANGE_DIR"

# Copiar templates
TEMPLATE_DIR=".claude/templates"

if [ ! -f "$TEMPLATE_DIR/change-proposal.md" ]; then
    error "Template 'change-proposal.md' não encontrado em $TEMPLATE_DIR"
fi

# proposal.md é sempre necessário
cp "$TEMPLATE_DIR/change-proposal.md" "$CHANGE_DIR/proposal.md"
success "Criado: proposal.md"

# design.md se não for docs
if [ "$CHANGE_TYPE" != "docs" ]; then
    cp "$TEMPLATE_DIR/change-design.md" "$CHANGE_DIR/design.md"
    success "Criado: design.md"
fi

# tasks.md é sempre necessário
cp "$TEMPLATE_DIR/change-tasks.md" "$CHANGE_DIR/tasks.md"
success "Criado: tasks.md"

# Criar branch git
BRANCH="${CHANGE_TYPE}/${slug}"
git checkout -b "$BRANCH" 2>/dev/null || error "Não foi possível criar branch '$BRANCH'"
success "Branch criada: $BRANCH"

# Adicionar ao git (arquivos criados)
git add "$CHANGE_DIR"
success "Mudança adicionada ao git staging area"

echo ""
echo "=== Próximos Passos ==="
echo ""
echo "1. Editar os arquivos de documentação:"
echo "   - $CHANGE_DIR/proposal.md     (Por quê?)"
if [ "$CHANGE_TYPE" != "docs" ]; then
    echo "   - $CHANGE_DIR/design.md        (Como?)"
fi
echo "   - $CHANGE_DIR/tasks.md         (O quê?)"
echo ""
echo "2. Fazer commit da documentação:"
echo "   git commit -m \"docs: initialize $CHANGE_TYPE/$slug change\""
echo ""
echo "3. Editar o código conforme necessário"
echo ""
echo "4. Fazer commits frequentes:"
echo "   git commit -m \"${CHANGE_TYPE}: descrição da mudança\""
echo ""
echo "5. Atualizar tasks.md conforme completa as tarefas"
echo ""
echo "6. Quando pronto, abrir um PR:"
echo "   gh pr create --draft --title \"$CHANGE_TYPE: $(echo $slug | sed 's/-/ /g')\" --body \$(cat $CHANGE_DIR/proposal.md)"
echo ""
echo "7. Após aprovação, mesclar:"
echo "   gh pr merge --squash"
echo ""
echo "8. Arquivar a mudança:"
echo "   mv openspec/changes/active/$CHANGE_NAME openspec/changes/archive/$CHANGE_NAME"
echo ""
echo "Happy coding! 🚀"
