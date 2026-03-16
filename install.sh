#!/data/data/com.termux/files/usr/bin/bash
echo "Установка HackLang в Termux..."
cd ~
if [ -d "hacklang" ]; then
    echo "Папка hacklang уже существует. Обновляем..."
    cp -r hacklang hacklang_backup
    rm -rf hacklang
fi
# Предполагается, что архив распакован в текущую папку
# Если вы запускаете install.sh из папки с проектом, то копируем
if [ -d "hacklang" ]; then
    mv hacklang ~/
else
    echo "Ошибка: папка hacklang не найдена."
    exit 1
fi
# Создаём симлинк в bin
ln -sf ~/hacklang/hacklang.py $PREFIX/bin/hacklang
chmod +x $PREFIX/bin/hacklang
# Создаём папку для библиотек
mkdir -p ~/.hacklang/lib
# Копируем стандартные библиотеки
cp -r ~/hacklang/lib/* ~/.hacklang/lib/ 2>/dev/null
echo "Установка завершена! Запустите 'hacklang' для входа в REPL."