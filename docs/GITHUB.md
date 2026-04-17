# Публикация на GitHub

Каноническое имя репозитория: **figma-hmi-plugin**.  
URL: https://github.com/chuxitong/figma-hmi-plugin

## Переименование с hmi-code-gen

1. На GitHub: **Settings** → **General** → **Repository name** → ввести `figma-hmi-plugin` → **Rename**.
2. Локально обновить remote:

```bash
git remote set-url origin https://github.com/chuxitong/figma-hmi-plugin.git
git remote -v
```

## Полная выгрузка текущего состояния

Из корня репозитория:

```bash
git add -A
git status
git commit -m "Figma HMI Plugin: полное обновление прототипа и материалов ВКР"
git push origin master
```

Если история на сервере расходится и нужно заменить содержимое ветки текущим деревом (осторожно):

```bash
git push origin master --force
```

Требуются учётные данные GitHub (Personal Access Token или SSH).

Файл `REPOSITORY.txt` в корне содержит только канонический URL репозитория.
