### Danov Music Studio — SEO/Метрики/Безопасность (краткое руководство)

Это описание текущей SEO‑инфры, как ей управлять, что проверять на локалке и что сделать при релизе.

### 1) Из чего состоит SEO у нас
- Система страниц:
  - Основные страницы (Home, About, Services, Equipment, Portfolio, Artists, Contact, Booking) — мультиязычно.
  - SEO‑лендинги (EN/RU/UK/DE): `/[lang]/landing/<slug>/` под ключевые запросы.
    - Примеры slug: `recording-studio-berlin`, `mixing-berlin`, `mastering-berlin`, `vocal-tuning-berlin`, `ukrainian-recording-studio-berlin`, и др.

- Тех. SEO:
  - Sitemap: `/sitemap.xml`
  - Robots: `/robots.txt`
  - Canonical link + hreflang для `en/ru/uk/de`
  - OG/Twitter теги (превью в соцсетях)
  - Структурированные данные (JSON‑LD):
    - LocalBusiness (на всех страницах через `base.html`)
    - Service (на страницах Services всех языков)
    - FAQPage (на Services и Booking, все языки)

- Панель управления в админке (минималистично, как в WP/Wix):
  - `Site SEO Settings` (глобально):
    - Defaults: `default_description`, `default_keywords`, `og_image_url`
    - Verification: `google_site_verification`, `bing_site_verification`
    - Social Links: `instagram_url`, `youtube_url`, `telegram_url`, `tiktok_url`
    - Analytics: `gtag_enabled`, `ga4_measurement_id`
  - `Page SEO` (точечно для пути и языка):
    - `path` (например `/en/services/`), `language` (en/ru/uk/de)
    - `title`, `description`, `keywords`, `og_title`, `og_description`, `og_image_url`, `canonical_override`

### 2) Как это всё рендерится
- Вьюхи пробрасывают `seo` (description/keywords/OG), ссылки `hreflang`. 
- Глобальные настройки подтягиваются через `Site SEO Settings` + переопределяются `Page SEO`.
- GA4 подключается автоматически, если в админке включён `gtag_enabled` и указан `ga4_measurement_id`.
- reCAPTCHA в Booking:
  - На локалке скрыта (чтобы не мешала).
  - На проде включится автоматически, если DEBUG=False и заданы реальные ключи.

### 3) Как управлять SEO без кода
1. Зайти в Django Admin → `Site SEO Settings` → создать единственный объект.
   - Заполнить по желанию глобальные meta, соцсети (можно позже), коды верификаций (к релизу), GA4 (к релизу).
2. В `Page SEO` добавить строки для ключевых страниц (по желанию) под нужные языки.
3. На проде в Search Console/Bing Webmaster указать домен и пройти верификацию (через meta, мы уже поддерживаем).

### 4) Как добавить ещё лендинг (доп. ключ)
- Быстро: добавить slug в маппинг в `booking/views.py` (функция `landing`, словарь `slug_to_service`) → 
  страница автоматически получит тексты/цену/CTA по услуге и мультиязычный рендер.
- Если нужен особый текст — создаём кастомный шаблон по аналогии, или добавим ветку в `landing()`.

### 5) Безопасность (dev vs prod)
- Уже включено:
  - CSRF, XSS filter, no‑sniff, X‑Frame‑Options: SAMEORIGIN
  - Антиспам/Rate limit на бронирования (middleware)
  - CSP (белые списки ресурсов) — мягкий режим в dev, можно ужесточить на проде.
- В проде дополнительно:
  - HSTS, secure cookies, Strict SameSite, `SECURE_PROXY_SSL_HEADER`
  - Рекомендуется: сменить `ADMIN_URL`, включить 2FA, reCAPTCHA, и ужесточить CSP (убрать inline, добавить nonce).

### 6) Что проверить сейчас на localhost
- Админка: 
  - `Site SEO Settings`/`Page SEO` доступны, поля понятные, сохраняются.
- Страницы/мета:
  - `/sitemap.xml`, `/robots.txt` открываются
  - Любая Services/Booking страница — в исходнике есть JSON‑LD (FAQ/Service)
  - Любой лендинг, например `/en/landing/recording-studio-berlin` — корректные заголовки, цена, CTA на бронирование с предвыбранной услугой
  - В `<head>` видны canonical, hreflang для `en/ru/uk/de`, OG/Twitter мета
- Валидация (при желании):
  - Google Rich Results Test (скопировать HTML страницы) — проверить FAQ/Service/LocalBusiness
  - OpenGraph/Twitter preview — мета присутствуют
  - Lighthouse (SEO вкладка) — базовые пункты зелёные

### 7) Чек‑лист к релизу (без кода)
- ENV/настройки:
  - `DEBUG=False`, `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
  - `SECRET_KEY` и почтовые пароли — только из окружения
  - `CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`
  - `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY` — реальные ключи
  - `ADMIN_URL` поменять на нестандартный путь
- Админка:
  - `Site SEO Settings`: вставить соцсети, верификации, GA4 ID и включить `gtag_enabled`
  - (опц.) `Page SEO`: точечные правки Title/Description для ключевых страниц
- Регистрация в каталогах:
  - Google Business Profile, Bing Places, Apple Maps, локальные каталоги Берлина
- Search Console:
  - Добавить домен, пройти верификацию, отправить `/sitemap.xml`

### 8) Частые вопросы
- Почему reCAPTCHA не видно локально?
  - Она намеренно выключена в dev, чтобы не мешать тесту. На проде с ключами включится автоматически.
- Как изменить мета у конкретной страницы?
  - Через `Page SEO`: укажи точный `path` и `language`, заполни поля.
- Как добавить новую услугу на лендинг?
  - Добавить slug в словарь `slug_to_service` → страница подтянет контент и цены услуги.

### 9) Контакты/правки
Хочешь, чтобы я ужесточил CSP, подключил GA4, Search Console, подготовил доп. лендинги — просто скажи. Всё уже подготовлено для быстрого релиза.



