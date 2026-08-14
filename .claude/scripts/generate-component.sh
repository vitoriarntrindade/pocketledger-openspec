#!/bin/bash

# Script para gerar novo componente com padrões de qualidade
# Uso: ./generate-component.sh router posts
#      ./generate-component.sh service posts
#      ./generate-component.sh schema post

set -e

COMPONENT_TYPE=$1
COMPONENT_NAME=$2

if [ -z "$COMPONENT_TYPE" ] || [ -z "$COMPONENT_NAME" ]; then
    echo "Uso: ./generate-component.sh <type> <name>"
    echo "Types: router, service, schema, model"
    echo "Example: ./generate-component.sh router posts"
    exit 1
fi

# Convert names
NAME_LOWER=$(echo $COMPONENT_NAME | tr '[:upper:]' '[:lower:]')
NAME_PASCAL=$(echo $NAME_LOWER | sed 's/_//g' | sed 's/^./\U&/')
NAME_PLURAL="${NAME_LOWER}s"

echo "📝 Generating $COMPONENT_TYPE: $NAME_LOWER"

case $COMPONENT_TYPE in
    router)
        DEST="app/api/routers/${NAME_LOWER}.py"
        if [ -f "$DEST" ]; then
            echo "❌ File already exists: $DEST"
            exit 1
        fi
        cp .claude/templates/router.py.template "$DEST"
        # Replace placeholders
        sed -i "s|{{model_name_lower}}|$NAME_LOWER|g" "$DEST"
        sed -i "s|{{model_name_plural_lower}}|$NAME_PLURAL|g" "$DEST"
        sed -i "s|{{ModelNamePascal}}|$NAME_PASCAL|g" "$DEST"
        echo "✅ Router created: $DEST"
        echo "📝 Edit the file and replace placeholder imports/logic"
        ;;

    service)
        DEST="app/services/${NAME_LOWER}_service.py"
        if [ -f "$DEST" ]; then
            echo "❌ File already exists: $DEST"
            exit 1
        fi
        cp .claude/templates/service.py.template "$DEST"
        # Replace placeholders
        sed -i "s|{{model_name_lower}}|$NAME_LOWER|g" "$DEST"
        sed -i "s|{{model_name_plural_lower}}|$NAME_PLURAL|g" "$DEST"
        sed -i "s|{{ModelNamePascal}}|$NAME_PASCAL|g" "$DEST"
        echo "✅ Service created: $DEST"
        echo "📝 Edit the file and replace placeholder imports/logic"
        ;;

    *)
        echo "❌ Unknown component type: $COMPONENT_TYPE"
        echo "Available types: router, service"
        exit 1
        ;;
esac

echo ""
echo "🔍 Next steps:"
echo "  1. Edit: $DEST"
echo "  2. Replace imports and logic"
echo "  3. Run: git add $DEST && git commit"
echo "  4. Pre-commit will validate automatically"
