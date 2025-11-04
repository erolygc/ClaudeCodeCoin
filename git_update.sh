#!/bin/bash
# ClaudeCodeCoin - GitHub Güncelleme Scripti

echo "======================================================================"
echo "🔄 ClaudeCodeCoin - GitHub Güncelleme"
echo "======================================================================"
echo ""

# Mevcut branch'i al
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Mevcut branch: $CURRENT_BRANCH"
echo ""

# Working tree temiz mi kontrol et
if [[ -n $(git status -s) ]]; then
    echo "⚠️  UYARI: Working tree'de değişiklikler var!"
    echo ""
    git status -s
    echo ""
    read -p "Devam etmek istiyor musunuz? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ İptal edildi"
        exit 1
    fi
fi

echo "📥 Remote'dan güncellemeler getiriliyor..."
git fetch origin

echo ""
echo "🔍 Yeni commit'ler kontrol ediliyor..."
NEW_COMMITS=$(git log HEAD..origin/$CURRENT_BRANCH --oneline)

if [ -z "$NEW_COMMITS" ]; then
    echo "✅ Yeni güncelleme yok - Her şey güncel!"
else
    echo "📋 Yeni commit'ler bulundu:"
    echo "$NEW_COMMITS"
    echo ""
    read -p "Güncellemeleri çekmek istiyor musunuz? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⬇️  Güncellemeler çekiliyor..."

        # Pull with retry logic
        MAX_RETRIES=4
        RETRY_COUNT=0
        DELAY=2

        while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
            if git pull origin $CURRENT_BRANCH; then
                echo "✅ Güncelleme başarılı!"
                exit 0
            else
                RETRY_COUNT=$((RETRY_COUNT+1))
                if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                    echo "⚠️  Hata oluştu, tekrar deneniyor ($RETRY_COUNT/$MAX_RETRIES)..."
                    sleep $DELAY
                    DELAY=$((DELAY*2))
                fi
            fi
        done

        echo "❌ Güncelleme başarısız! Manuel kontrol gerekli."
        exit 1
    else
        echo "❌ Güncelleme iptal edildi"
    fi
fi

echo ""
echo "======================================================================"
