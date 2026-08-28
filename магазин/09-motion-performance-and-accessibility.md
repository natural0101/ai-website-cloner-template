# Motion, производительность и доступность

## Роль motion

Motion разрешён, когда объясняет изменение состояния:

- строка физически переходит в корзину или счётчик обновляется;
- drawer товара открывается из выбранной карточки и возвращает фокус;
- фильтрация перестраивает список без потери ориентации;
- ошибка, repricing или подтверждение заметны без мигания;
- прогресс заказа показывает фактический переход статуса.

Motion не должен задерживать добавление, оплату, появление ошибки, работу формы или навигацию. Декоративные scroll scenes не используются в каталоге, корзине и checkout.

Motion for React поддерживает layout animations и exit states через `layout` и `AnimatePresence`; использовать только при уже установленной зависимости и с короткими переходами, не добавлять библиотеку ради одного fade.

Источники:

- https://motion.dev/docs/react-layout-animations
- https://motion.dev/docs/react-animate-presence

## Reduced motion

- `prefers-reduced-motion: reduce` отключает параллакс, автоплей и масштабные перемещения;
- функциональная обратная связь остаётся через текст, цвет с достаточным контрастом, иконку и ARIA live region;
- исчезновение элемента не блокирует следующий ввод ожиданием анимации;
- видео имеет controls, captions при речи и poster; автоплей со звуком запрещён.

## Core Web Vitals budget

Цели для 75-го перцентиля mobile и desktop:

- LCP ≤ 2.5 s;
- INP ≤ 200 ms;
- CLS ≤ 0.1.

Это актуальные «good» thresholds Core Web Vitals по web.dev. Лабораторная проверка не заменяет field RUM после запуска.

Источник: https://web.dev/articles/vitals

## Commerce performance rules

- hero не блокирует поиск, категории и CTA ожиданием video/3D;
- главное изображение имеет responsive sources, правильный размер и приоритет только для реального LCP candidate;
- карточки ниже fold lazy-load, но первая видимая сетка не мигает placeholders без зарезервированных размеров;
- шрифты self-hosted/разрешённые, subset и без длинной невидимости текста;
- third-party chat, maps, reviews, A/B и analytics грузятся по budget и consent;
- catalog filtering не рендерит тысячи DOM nodes; применять pagination/virtualization по измерению;
- cart/checkout JS отделён от декоративного marketing bundle;
- server responses для цены/availability имеют timeout, retry policy и явную ошибку;
- performance проверяется на реальном мобильном профиле и плохой сети.

## Accessibility baseline

WCAG 2.2 AA — минимальная цель, если рынок не требует большего. Обязательные сценарии:

- весь выбор товара, модификаторов, даты, слота, корзины и checkout доступен с клавиатуры;
- фокус видим и не закрыт sticky header/footer;
- tap targets соответствуют минимуму WCAG 2.2 или имеют достаточное spacing;
- у полей постоянные labels; placeholder не заменяет label;
- связанные группы radio/checkbox используют `fieldset`/`legend`;
- ошибки идентифицируют поле, причину и исправление; после submit есть summary;
- изменение total, cart count и статуса объявляется без захвата фокуса;
- color не единственный носитель наличия, ошибки, выбранности и скидки;
- product images имеют осмысленный alt, декоративные — пустой alt;
- zoom до 200% и reflow не создают горизонтальный checkout;
- password manager и paste не блокируются;
- timeout slot/cart предупреждает заранее и даёт продлить, если backend разрешает.

Источники:

- https://www.w3.org/TR/WCAG22/
- https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- https://www.w3.org/WAI/tutorials/forms/

## Визуальное направление

Выразительность строится вокруг товара/услуги: съёмка, материал, процесс, кухня, интерьер, работа специалиста, упаковка. Не использовать generic purple gradient, бесконечные glass cards и случайный 3D. Каталог сохраняет постоянный порядок атрибутов и спокойную плотность; брендовые моменты концентрируются в hero, campaign block и editorial story.
