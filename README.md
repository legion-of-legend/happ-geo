# happ-geo

Урезанные `geosite.dat` и `geoip.dat` для профиля маршрутизации Happ «GeoRU», который отдаёт подписка 3x-ui.

Источник — полные базы [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat). Из них оставлены только категории, которые использует профиль, поэтому файлы весят сотни килобайт вместо десятков мегабайт.

| Файл | Категории |
|---|---|
| `geosite.dat` | `category-ads`, российские категории (`category-ru`, `category-bank-ru`, `category-gov-ru` и др.), `yandex`, `mailru-group`, `mts-ru`, `apple*` |
| `geoip.dat` | `ru` |

## Обновление

Файлы обновляются автоматически каждый понедельник в 03:00 UTC: workflow [`update-geo.yml`](.github/workflows/update-geo.yml) запускает `build.py`, проверяет, что Xray загружает новые файлы со всеми категориями, и коммитит их, только если данные изменились. Запустить вручную можно на вкладке Actions → Update geo files → Run workflow.

Вручную:

```bash
python3 build.py
git commit -am "Update geo files" && git push
```

`build.py` скачивает свежие базы и оставляет нужные категории. Если в профиль GeoRU добавляется новая категория, её нужно дописать в `GEOSITE_TAGS` или `GEOIP_TAGS` в `build.py`.

После обновления файлов в настройке подписки 3x-ui (`subRoutingRules`) нужно поменять поле `LastUpdated`, чтобы Happ заново скачал профиль и файлы.
