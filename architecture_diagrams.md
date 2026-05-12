# Архітектурні діаграми системи "Їжачок" (C4 Model)

Цей файл містить код для візуалізації архітектури за допомогою інструменту Mermaid.
Ви можете скопіювати код нижче та вставити його в [Mermaid Live Editor](https://mermaid.live/).

---

## Рівень 1: Діаграма системного контексту (L1 - System Context)
Ця діаграма показує взаємодію системи із зовнішніми акторами та системами.

```mermaid
C4Context
    title Діаграма системного контексту (L1)

    Person(customer, "Клієнт", "Замовляє їжу через смартфон/сайт")
    Person(cashier, "Касир", "Обробляє замовлення на касі та видає їжу")
    Person(admin, "Адміністратор", "Керує асортиментом, персоналом та змінами")

    System(erp, "ERP Система 'Їжачок'", "Автоматизація процесів їдальні, облік продажів та залишків")

    System_Ext(payment, "Платіжна система", "Обробка безготівкових платежів (Card)")

    Rel(customer, erp, "Переглядає меню, робить замовлення")
    Rel(cashier, erp, "Керує чергою, приймає оплату")
    Rel(admin, erp, "Переглядає звіти, закриває зміни")
    Rel(erp, payment, "Запит на оплату карткою")
```

---

## Рівень 2: Діаграма контейнерів (L2 - Containers)
Показує основні програмні блоки системи та технології.

```mermaid
C4Container
    title Діаграма контейнерів (L2)

    Person(customer, "Клієнт")
    Person(cashier, "Касир")
    Person(admin, "Адміністратор")

    System_Boundary(erp_system, "ERP Система 'Їжачок'") {
        Container(web_app, "Web Application (Django)", "Python, Django, DRF", "Серверна логіка, API, адмін-панель")
        Container(client_ui, "Client UI", "HTML, Tailwind, Alpine.js", "Інтерфейс для онлайн-замовлень")
        Container(pos_ui, "POS UI", "HTML, Tailwind, Alpine.js", "Інтерфейс касового терміналу")
        ContainerDb(db, "Database", "PostgreSQL / SQLite", "Зберігання меню, замовлень та залишків")
    }

    System_Ext(payment, "Платіжна система")

    Rel(customer, client_ui, "Використовує")
    Rel(cashier, pos_ui, "Використовує")
    Rel(admin, web_app, "Використовує адмін-панель")

    Rel(client_ui, web_app, "JSON/HTTPS API")
    Rel(pos_ui, web_app, "JSON/HTTPS API")
    Rel(web_app, db, "Django ORM (SQL)")
    Rel(web_app, payment, "API запити")
```

---

## Рівень 3: Діаграма компонентів (L3 - Components)
Показує внутрішню структуру основного Django-додатка.

```mermaid
C4Component
    title Діаграма компонентів (L3) - Django Web Application

    Container_Boundary(frontend, "Frontend Interfaces") {
        Component(client_ui, "Client UI", "Alpine.js", "Логіка клієнтського кошика")
        Component(pos_ui, "POS UI", "Alpine.js", "Логіка касового терміналу")
    }

    Container_Boundary(django_app, "Django Web Application Container") {
        Component(auth, "User & Auth Manager", "users app", "Ролі (RBAC), автентифікація")
        Component(menu_mgr, "Menu & Combo Engine", "menu app", "Управління стравами та комбо-наборами")
        Component(inv_service, "Inventory Service", "menu/canteen service", "Розрахунок залишків та резервування")
        Component(order_proc, "Order Processor", "orders app", "Життєвий цикл замовлення, API")
        Component(analytics, "Analytics & Shift Mgr", "canteen app", "Фінансова звітність, закриття змін")
    }

    ContainerDb(db, "Database", "SQL", "Центральне сховище даних")

    Rel(client_ui, order_proc, "Створення замовлень", "JSON")
    Rel(pos_ui, order_proc, "Зміна статусів, оплата", "JSON")
    
    Rel(order_proc, inv_service, "Команда на списання", "Internal Call")
    Rel(order_proc, auth, "Перевірка прав", "Internal Call")
    Rel(inv_service, menu_mgr, "Дані про склад страв", "ORM")
    Rel(analytics, order_proc, "Дані для звітів", "ORM")

    Rel(auth, db, "Read/Write")
    Rel(menu_mgr, db, "Read/Write")
    Rel(inv_service, db, "Read/Write")
    Rel(order_proc, db, "Read/Write")
    Rel(analytics, db, "Read/Write")
```
