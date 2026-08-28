# Prompt для агента

Скопировать текст ниже и заменить значения в квадратных скобках.

```text
Ты проектируешь и реализуешь коммерческий сайт в репозитории [PATH].

Обязательные источники проекта:
- магазин/README.md
- магазин/01-commerce-model-router.md
- магазин/02-conversion-and-information-architecture.md
- магазин/03-domain-and-state-model.md
- магазин/04-page-blueprints.md
- магазин/05-checkout-payments-and-fulfillment.md
- [магазин/06-pizzeria-blueprint.md | магазин/07-service-booking-blueprint.md]
- магазин/08-seo-legal-and-trust.md
- магазин/09-motion-performance-and-accessibility.md
- магазин/11-quality-gate.md
- магазин/projects/[SLUG]/

Режим: [catalog | pizzeria | booking | quote | hybrid].
Основная конверсия: [ACTION].
Рынок/валюта/часовой пояс: [MARKET].

Работай по этапам:
OBSERVE → PLAN → IMPLEMENT → VERIFY.

OBSERVE
1. Прочитай локальные AGENTS.md и фактический стек.
2. Проверь существующие маршруты, backend/API, модели, дизайн-токены, аналитику и незакоммиченные изменения.
3. Заполни 01-brief.md фактами; неизвестное пометь UNKNOWN, не выдумывай.

PLAN
1. Зафиксируй коммерческий режим и почему соседние режимы отклонены.
2. Опиши happy path и минимум 8 failure/recovery paths в 02-flow-map.md.
3. Опиши desktop/mobile routes и section order в 03-page-blueprint.md.
4. Зафиксируй источники цены, наличия/слотов, заказа и платежа в 04-commerce-state-model.md.
5. Свяжи каждый claim с evidence или удали claim.
6. В 06-implementation-plan.md перечисли точные файлы, интеграции, события аналитики и проверки.

IMPLEMENT
1. Сначала реализуй вертикальный поток от выбора до server-confirmed результата на реальных или явно помеченных fixture data.
2. Цена, скидка, availability и статус платежа подтверждаются сервером.
3. Добавь loading, empty, invalid, unavailable, payment pending/failed, success и recovery states.
4. Затем добавь визуальную выразительность без ухудшения каталога и checkout.
5. Не добавляй зависимости без проверки локального стека, лицензии, bundle impact и необходимости.

VERIFY
1. Запусти lint, typecheck, build и существующие тесты.
2. Проверь happy path и failure paths на mobile и desktop.
3. Проверь keyboard, focus, labels, errors, reduced motion, 200% zoom и reflow.
4. Проверь server recalculation, double-submit, refresh/back, webhook retry, expired cart/slot и payment pending.
5. Проверь structured data валидатором и соответствие видимому контенту.
6. Измерь LCP/INP/CLS в field после запуска или зафиксируй UNKNOWN; lab не называй field proof.
7. Заполни 07-qa-report.md командами, результатами и evidence.
8. Выполни node "магазин/scripts/check-project.mjs" [SLUG].

Запрещено:
- fake reviews/ratings/logos/scarcity/timers;
- клиентский total как источник истины;
- purchase event по клику;
- success только по redirect URL;
- скрытые сборы;
- регистрация без доказанной необходимости;
- декоративные motion/3D в checkout;
- изменение юридического текста без владельца и проверки.

Финальный отчёт:
- что реализовано;
- какие файлы изменены;
- команды и результаты;
- какие коммерческие состояния проверены;
- какие данные/интеграции реальные, fixture или UNKNOWN;
- remaining risks и точный следующий шаг.
```
