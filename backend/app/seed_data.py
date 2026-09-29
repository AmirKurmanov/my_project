"""Начальные данные для демонстрации платформы."""
from datetime import datetime
from app.models import User, ObjectType, RobotCategory, RobotSolution, Project, Scenario
from app.auth import get_password_hash


def seed_database(db):
    # Check if already seeded
    if db.query(User).first():
        return

    #  Users  
    admin = User(
        email="admin@robopodbor.ru",
        hashed_password=get_password_hash("admin123"),
        full_name="Администратор Системы",
        role="admin",
    )
    demo_user = User(
        email="demo@robopodbor.ru",
        hashed_password=get_password_hash("demo123"),
        full_name="Демо Пользователь",
        role="user",
    )
    db.add_all([admin, demo_user])
    db.flush()

    # Object Types  
    warehouse = ObjectType(
        name="Склад",
        slug="warehouse",
        description="Складские комплексы, распределительные центры, логистические хабы",
        icon="Warehouse",
        parameters_schema={
            "fields": [
                {"name": "area_sqm", "label": "Площадь склада", "type": "number", "unit": "м²", "required": True, "min": 100, "max": 500000, "default": 5000},
                {"name": "zones_count", "label": "Количество рабочих зон", "type": "number", "unit": "шт.", "required": True, "min": 1, "max": 50, "default": 4},
                {"name": "work_shifts", "label": "Количество смен", "type": "number", "unit": "смен/сут.", "required": True, "min": 1, "max": 3, "default": 2},
                {"name": "incoming_operations_per_day", "label": "Входящие операции", "type": "number", "unit": "оп./сут.", "required": True, "min": 10, "max": 100000, "default": 500},
                {"name": "internal_operations_per_day", "label": "Внутрискладские операции", "type": "number", "unit": "оп./сут.", "required": True, "min": 10, "max": 200000, "default": 1200},
                {"name": "outgoing_operations_per_day", "label": "Исходящие операции", "type": "number", "unit": "оп./сут.", "required": True, "min": 10, "max": 100000, "default": 600},
                {"name": "storage_type", "label": "Тип хранения", "type": "select", "options": ["Паллетное", "Полочное", "Напольное", "Мезонинное", "Комбинированное"], "required": True, "default": "Паллетное"},
                {"name": "sku_count", "label": "Количество SKU", "type": "number", "unit": "шт.", "required": True, "min": 10, "max": 1000000, "default": 5000},
                {"name": "avg_cargo_weight_kg", "label": "Средняя масса грузовой единицы", "type": "number", "unit": "кг", "required": True, "min": 0.1, "max": 5000, "default": 25},
                {"name": "avg_cargo_length_mm", "label": "Длина грузовой единицы", "type": "number", "unit": "мм", "required": False, "default": 600},
                {"name": "avg_cargo_width_mm", "label": "Ширина грузовой единицы", "type": "number", "unit": "мм", "required": False, "default": 400},
                {"name": "avg_cargo_height_mm", "label": "Высота грузовой единицы", "type": "number", "unit": "мм", "required": False, "default": 400},
                {"name": "staff_count", "label": "Численность персонала", "type": "number", "unit": "чел.", "required": True, "min": 1, "max": 10000, "default": 30},
                {"name": "avg_salary_rub", "label": "Средняя зарплата", "type": "number", "unit": "руб./мес.", "required": True, "min": 20000, "max": 500000, "default": 65000},
                {"name": "current_productivity", "label": "Текущая производительность", "type": "number", "unit": "оп./чел./ч.", "required": False, "default": 15},
                {"name": "route_length_m", "label": "Протяжённость маршрутов", "type": "number", "unit": "м", "required": False, "default": 200},
                {"name": "available_aisle_width_mm", "label": "Ширина проходов", "type": "number", "unit": "мм", "required": False, "default": 3000},
                {"name": "peak_operations_per_hour", "label": "Пиковые операции в час", "type": "number", "unit": "оп./ч.", "required": False, "default": 120},
            ]
        },
        demo_parameters={
            "area_sqm": 20000,
            "zones_count": 4,
            "work_shifts": 2,
            "incoming_operations_per_day": 1000,
            "internal_operations_per_day": 100000,
            "outgoing_operations_per_day": 1000,
            "storage_type": "Паллетное",
            "sku_count": 2000,
            "avg_cargo_weight_kg": 800,
            "avg_cargo_length_mm": 1200,
            "avg_cargo_width_mm": 800,
            "avg_cargo_height_mm": 1600,
            "staff_count": 180,
            "avg_salary_rub": 100000,
            "current_productivity": 150,
            "route_length_m": 25,
            "available_aisle_width_mm": 2800,
            "peak_operations_per_hour": 1500,
        },
    )

    airport = ObjectType(
        name="Аэропорт",
        slug="airport",
        description="Аэропорты, авиатерминалы, грузовые терминалы",
        icon="Plane",
        parameters_schema={
            "fields": [
                {"name": "operation_zone", "label": "Зона операции", "type": "select", "options": ["Терминал", "Багажное отделение", "Грузовой терминал", "Перрон"], "required": True, "default": "Терминал"},
                {"name": "work_mode", "label": "Режим работы", "type": "select", "options": ["Круглосуточный", "16 часов", "12 часов"], "required": True, "default": "Круглосуточный"},
                {"name": "passenger_flow_per_day", "label": "Пассажиропоток", "type": "number", "unit": "чел./сут.", "required": True, "min": 100, "max": 500000, "default": 15000},
                {"name": "cargo_flow_kg_per_day", "label": "Грузопоток", "type": "number", "unit": "кг/сут.", "required": False, "default": 50000},
                {"name": "peak_operations_per_hour", "label": "Пиковые операции в час", "type": "number", "unit": "оп./ч.", "required": True, "min": 5, "max": 10000, "default": 80},
                {"name": "route_length_m", "label": "Протяжённость маршрутов", "type": "number", "unit": "м", "required": False, "default": 500},
                {"name": "avg_object_weight_kg", "label": "Средняя масса объекта", "type": "number", "unit": "кг", "required": True, "default": 20},
                {"name": "staff_count", "label": "Численность персонала", "type": "number", "unit": "чел.", "required": True, "min": 1, "max": 5000, "default": 25},
                {"name": "avg_salary_rub", "label": "Средняя зарплата", "type": "number", "unit": "руб./мес.", "required": True, "default": 70000},
                {"name": "security_requirements", "label": "Требования безопасности", "type": "select", "options": ["Стандартные", "Повышенные", "Максимальные"], "required": True, "default": "Повышенные"},
                {"name": "has_closed_zones", "label": "Наличие закрытых зон", "type": "select", "options": ["Да", "Нет"], "required": True, "default": "Да"},
                {"name": "area_sqm", "label": "Площадь", "type": "number", "unit": "м²", "required": False, "default": 10000},
            ]
        },
        demo_parameters={
            "operation_zone": "Терминал",
            "work_mode": "Круглосуточный",
            "passenger_flow_per_day": 23300,
            "cargo_flow_kg_per_day": 35000,
            "peak_operations_per_hour": 3200,
            "route_length_m": 500,
            "avg_object_weight_kg": 18,
            "staff_count": 320,
            "avg_salary_rub": 100000,
            "security_requirements": "Повышенные",
            "has_closed_zones": "Да",
            "area_sqm": 85000,
        },
    )

    medical = ObjectType(
        name="Медицинское учреждение",
        slug="medical",
        description="Больницы, поликлиники, медицинские центры",
        icon="Hospital",
        parameters_schema={
            "fields": [
                {"name": "facility_type", "label": "Тип учреждения", "type": "select", "options": ["Больница", "Поликлиника", "Медицинский центр", "Реабилитационный центр"], "required": True, "default": "Больница"},
                {"name": "area_sqm", "label": "Площадь", "type": "number", "unit": "м²", "required": True, "min": 100, "max": 100000, "default": 8000},
                {"name": "floors_count", "label": "Этажность", "type": "number", "unit": "этажей", "required": True, "min": 1, "max": 30, "default": 5},
                {"name": "work_mode", "label": "Режим работы", "type": "select", "options": ["Круглосуточный", "Дневной"], "required": True, "default": "Круглосуточный"},
                {"name": "daily_cargo_trips", "label": "Перевозки грузов", "type": "number", "unit": "рейсов/сут.", "required": True, "min": 0, "max": 1000, "default": 40},
                {"name": "daily_linen_trips", "label": "Перевозки белья", "type": "number", "unit": "рейсов/сут.", "required": False, "default": 15},
                {"name": "daily_food_trips", "label": "Перевозки питания", "type": "number", "unit": "рейсов/сут.", "required": False, "default": 20},
                {"name": "daily_medicine_trips", "label": "Перевозки медикаментов", "type": "number", "unit": "рейсов/сут.", "required": False, "default": 30},
                {"name": "daily_waste_trips", "label": "Перевозки отходов", "type": "number", "unit": "рейсов/сут.", "required": False, "default": 10},
                {"name": "route_length_m", "label": "Протяжённость маршрутов", "type": "number", "unit": "м", "required": False, "default": 300},
                {"name": "has_elevators", "label": "Наличие лифтов", "type": "select", "options": ["Да", "Нет"], "required": True, "default": "Да"},
                {"name": "sanitization_requirements", "label": "Требования к дезинфекции", "type": "select", "options": ["Стандартные", "Повышенные", "Максимальные"], "required": True, "default": "Повышенные"},
                {"name": "staff_count", "label": "Численность логистического персонала", "type": "number", "unit": "чел.", "required": True, "min": 1, "max": 500, "default": 15},
                {"name": "avg_salary_rub", "label": "Средняя зарплата", "type": "number", "unit": "руб./мес.", "required": True, "default": 55000},
                {"name": "avg_cargo_weight_kg", "label": "Средняя масса груза", "type": "number", "unit": "кг", "required": False, "default": 15},
                {"name": "peak_operations_per_hour", "label": "Пиковые операции в час", "type": "number", "unit": "оп./ч.", "required": False, "default": 25},
            ]
        },
        demo_parameters={
            "facility_type": "Многопрофильная больница",
            "area_sqm": 45000,
            "floors_count": 9,
            "work_mode": "Круглосуточный",
            "daily_cargo_trips": 45,
            "daily_linen_trips": 18,
            "daily_food_trips": 18,
            "daily_medicine_trips": 340,
            "daily_waste_trips": 20,
            "route_length_m": 180,
            "has_elevators": "Да",
            "sanitization_requirements": "Максимальные",
            "staff_count": 65,
            "avg_salary_rub": 55000,
            "avg_cargo_weight_kg": 120,
            "peak_operations_per_hour": 50,
        },
    )
    db.add_all([warehouse, airport, medical])
    db.flush()

    # ──── Robot Categories ────
    cat_amr = RobotCategory(name="AMR (Автономный мобильный робот)", slug="amr", description="Автономные мобильные роботы для транспортировки грузов")
    cat_fmr = RobotCategory(name="FMR (Автономный вилочный погрузчик)", slug="fmr", description="Автономные вилочные погрузчики и штабелеры")
    cat_stacker = RobotCategory(name="Робот-штабелер", slug="stacker", description="Мобильные роботы с вилочным подъёмным устройством")
    cat_tugger = RobotCategory(name="Робот-тягач", slug="tugger", description="Автономные транспортные роботы для буксировки тележек")
    cat_cleaner = RobotCategory(name="Робот-уборщик", slug="cleaner", description="Мобильные клининговые роботы")
    cat_forklift = RobotCategory(name="Беспилотный погрузчик", slug="forklift", description="Беспилотные погрузчики для логистических центров")
    cat_cubic = RobotCategory(name="Система кубического хранения", slug="cubic-storage", description="Стационарные роботизированные системы умного хранения")
    db.add_all([cat_amr, cat_fmr, cat_stacker, cat_tugger, cat_cleaner, cat_forklift, cat_cubic])
    db.flush()

    # Load from CSV
    import csv
    import os
    import re
    
    csv_path = os.path.join(os.path.dirname(__file__), "catalog_export_v4.csv")
    csv_solutions = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader) # skip header
            for row in reader:
                if len(row) < 15: continue
                name_full = row[1].strip()
                company = row[4].strip()
                desc = row[5].strip()
                price_str = row[14].strip().replace(' ', '').replace(',', '.')
                price = float(price_str) if price_str else None
                
                # Extract payload from name if present
                payload = None
                m = re.search(r'до ([\d\s]+) кг', name_full)
                if m:
                    payload = float(m.group(1).replace(' ', ''))
                
                cat_id = cat_amr.id # default
                subtype = row[7].lower()
                if 'fmr' in subtype: cat_id = cat_fmr.id
                elif 'штабелер' in subtype: cat_id = cat_stacker.id
                elif 'тягач' in subtype: cat_id = cat_tugger.id
                elif 'уборщ' in subtype: cat_id = cat_cleaner.id
                elif 'погрузчик' in subtype: cat_id = cat_forklift.id
                elif 'хранени' in subtype: cat_id = cat_cubic.id
                
                sol = RobotSolution(
                    name=name_full.split('(')[0].strip(),
                    manufacturer=company,
                    category_id=cat_id,
                    country="Россия",
                    availability_status="В каталоге",
                    description=desc,
                    payload_capacity_kg=payload,
                    equipment_cost_rub=price,
                    acquisition_model="purchase",
                    service_life_years=7,
                    supported_processes=[row[8]] if row[8] else [],
                    supported_object_types=["warehouse", "airport", "medical"],
                    data_source="Каталог ФЦ БАС",
                    data_completeness="partial",
                )
                csv_solutions.append(sol)
        
        db.add_all(csv_solutions)
        db.flush()


    #  Robot Solutions 
    solutions = [
        RobotSolution(
            name="Ronavi H1500",
            manufacturer="Ronavi Robotics",
            category_id=cat_amr.id,
            country="Россия",
            availability_status="В наличии",
            description="Автономный мобильный робот для транспортировки паллет до 1500 кг. QR-метки и SLAM навигация.",
            payload_capacity_kg=1500,
            length_mm=1044, width_mm=654, height_mm=380,
            max_speed_ms=1.5,
            productivity_per_hour=90,
            battery_life_hours=6,
            positioning_accuracy_mm=3,
            navigation_type="QR-метки и SLAM",
            operating_conditions="Температура +5…+25 °C, ровный промышленный пол",
            min_aisle_width_mm=1500,
            charging_stations_required=True,
            equipment_cost_rub=3500000,
            software_cost_rub=500000,
            implementation_cost_rub=700000,
            annual_maintenance_cost_rub=200000,
            acquisition_model="both",
            service_life_years=7,
            supported_processes=["Транспортировка", "Перемещение паллет"],
            supported_object_types=["warehouse", "airport"],
            data_source="Сайт производителя (Ronavi Robotics)",
            data_completeness="full",
        ),
        RobotSolution(
            name="DMR Carrier P",
            manufacturer="ДиКом-Сервис",
            category_id=cat_fmr.id,
            country="Россия",
            availability_status="В наличии",
            description="Мобильный вилочный робот, высота подъема вил до 1600 мм, навигация SLAM на базе лидаров.",
            payload_capacity_kg=1500,
            length_mm=2050, width_mm=1000, height_mm=1975,
            max_speed_ms=1.5,
            productivity_per_hour=50,
            battery_life_hours=10,
            positioning_accuracy_mm=10,
            navigation_type="SLAM на базе лидаров",
            operating_conditions="Стандартный склад и производственный цех с ровным бетонным покрытием",
            min_aisle_width_mm=3000,
            charging_stations_required=True,
            equipment_cost_rub=4500000,
            software_cost_rub=600000,
            implementation_cost_rub=900000,
            annual_maintenance_cost_rub=300000,
            acquisition_model="purchase",
            service_life_years=10,
            supported_processes=["Перемещение паллет", "Штабелирование", "Транспортировка грузов"],
            supported_object_types=["warehouse", "airport"],
            data_source="ДиКом-Сервис (DMR Carrier P)",
            data_completeness="full",
        ),
        RobotSolution(
            name="MARK 2 SE",
            manufacturer="R2B",
            category_id=cat_cleaner.id,
            country="Россия",
            availability_status="В наличии",
            description="Робот-уборщик помещений, бак 40 л, эффективность до 1000 м2/ч.",
            payload_capacity_kg=0,
            length_mm=860, width_mm=610, height_mm=980,
            max_speed_ms=1.1,
            productivity_per_hour=1000,
            battery_life_hours=3,
            positioning_accuracy_mm=50,
            navigation_type="Лидар + камеры",
            operating_conditions="Внутри помещений",
            min_aisle_width_mm=1000,
            charging_stations_required=True,
            equipment_cost_rub=1500000,
            software_cost_rub=100000,
            implementation_cost_rub=200000,
            annual_maintenance_cost_rub=120000,
            acquisition_model="both",
            service_life_years=5,
            supported_processes=["Уборка", "Клининг"],
            supported_object_types=["warehouse", "airport", "medical"],
            data_source="R2B (MARK 2 SE)",
            data_completeness="full",
        ),
        RobotSolution(
            name="Pallet Shuttle",
            manufacturer="Stelkon",
            category_id=cat_cubic.id,
            country="Россия",
            availability_status="Под заказ",
            description="Шаттл-система для работы в канальных стеллажах до 12-15 метров.",
            payload_capacity_kg=1500,
            length_mm=1200, width_mm=800, height_mm=200,
            max_speed_ms=1.0,
            productivity_per_hour=100,
            battery_life_hours=9,
            positioning_accuracy_mm=5,
            navigation_type="Рельсовая система",
            operating_conditions="Канальные стеллажи, возможны исполнения для холодильных складов",
            min_aisle_width_mm=0,
            charging_stations_required=True,
            equipment_cost_rub=5000000,
            software_cost_rub=800000,
            implementation_cost_rub=1500000,
            annual_maintenance_cost_rub=400000,
            acquisition_model="purchase",
            service_life_years=12,
            supported_processes=["Хранение", "Перемещение паллет"],
            supported_object_types=["warehouse"],
            data_source="Stelkon",
            data_completeness="full",
        ),
        RobotSolution(
            name="Cognitive Pilot Тягач",
            manufacturer="Cognitive Pilot",
            category_id=cat_tugger.id,
            country="Россия",
            availability_status="Под заказ",
            description="Беспилотный багажный тягач (гибрид), 70 л бак.",
            payload_capacity_kg=3000,
            length_mm=2300, width_mm=1400, height_mm=1500,
            max_speed_ms=6.9,
            productivity_per_hour=30,
            battery_life_hours=24,
            positioning_accuracy_mm=100,
            navigation_type="Мультисенсорный автопилот",
            operating_conditions="Круглогодичная работа на перроне и в багажных зонах",
            min_aisle_width_mm=3000,
            charging_stations_required=False,
            equipment_cost_rub=6000000,
            software_cost_rub=1000000,
            implementation_cost_rub=1200000,
            annual_maintenance_cost_rub=500000,
            acquisition_model="purchase",
            service_life_years=10,
            supported_processes=["Транспортировка багажа"],
            supported_object_types=["airport"],
            data_source="Cognitive Pilot",
            data_completeness="partial",
        ),
        RobotSolution(
            name="EVOCARGO N1",
            manufacturer="Evocargo",
            category_id=cat_tugger.id,
            country="Россия",
            availability_status="Под заказ",
            description="Беспилотный грузовик, вместимость до 6 европаллет, запас хода 150-200 км.",
            payload_capacity_kg=2000,
            length_mm=5000, width_mm=1800, height_mm=2200,
            max_speed_ms=6.9,
            productivity_per_hour=40,
            battery_life_hours=15,
            positioning_accuracy_mm=100,
            navigation_type="Автономный автопилот 4-5 уровня",
            operating_conditions="Работа 24/7 при -40…+50 °C",
            min_aisle_width_mm=4000,
            charging_stations_required=True,
            equipment_cost_rub=9000000,
            software_cost_rub=2000000,
            implementation_cost_rub=1500000,
            annual_maintenance_cost_rub=800000,
            acquisition_model="purchase",
            service_life_years=10,
            supported_processes=["Транспортировка грузов"],
            supported_object_types=["airport", "warehouse"],
            data_source="Evocargo",
            data_completeness="partial",
        ),
        RobotSolution(
            name="Ronavi SD",
            manufacturer="Ronavi Robotics",
            category_id=cat_amr.id,
            country="Россия",
            availability_status="В наличии",
            description="Сортировочный робот с откидной крышкой, до 10 кг.",
            payload_capacity_kg=10,
            length_mm=420, width_mm=400, height_mm=200,
            max_speed_ms=2.5,
            productivity_per_hour=200,
            battery_life_hours=10,
            positioning_accuracy_mm=3,
            navigation_type="QR-метки",
            operating_conditions="Внутри помещений",
            min_aisle_width_mm=700,
            charging_stations_required=True,
            equipment_cost_rub=800000,
            software_cost_rub=200000,
            implementation_cost_rub=300000,
            annual_maintenance_cost_rub=100000,
            acquisition_model="both",
            service_life_years=5,
            supported_processes=["Транспортировка медикаментов", "Сортировка", "Транспортировка белья"],
            supported_object_types=["medical", "warehouse"],
            data_source="Ronavi Robotics",
            data_completeness="full",
        ),
        RobotSolution(
            name="PuduBot 2",
            manufacturer="Pudu Robotics",
            category_id=cat_amr.id,
            country="Китай",
            availability_status="В наличии",
            description="Робот-доставщик, 10 кг на полку, VSLAM.",
            payload_capacity_kg=40,
            length_mm=580, width_mm=535, height_mm=1290,
            max_speed_ms=1.2,
            productivity_per_hour=30,
            battery_life_hours=12,
            positioning_accuracy_mm=20,
            navigation_type="VSLAM + лазерный SLAM",
            operating_conditions="Внутри помещений",
            min_aisle_width_mm=800,
            charging_stations_required=True,
            equipment_cost_rub=1200000,
            software_cost_rub=150000,
            implementation_cost_rub=200000,
            annual_maintenance_cost_rub=150000,
            acquisition_model="both",
            service_life_years=5,
            supported_processes=["Транспортировка питания", "Транспортировка белья"],
            supported_object_types=["medical"],
            data_source="Pudu Robotics",
            data_completeness="full",
        ),
        ]
    db.add_all(solutions)
    db.flush()

    # Demo Project  
    demo_project = Project(
        user_id=demo_user.id,
        name="Демо: Складской комплекс «Логистик-Центр»",
        object_type_id=warehouse.id,
        parameters=warehouse.demo_parameters,
        status="calculated",
    )
    db.add(demo_project)
    db.flush()

    # Baseline scenario
    baseline = Scenario(
        project_id=demo_project.id,
        name="Базовый (без роботизации)",
        scenario_type="baseline",
        parameters=warehouse.demo_parameters,
        results={
            "robot_count": 0,
            "capex_total": 0,
            "capex_breakdown": {},
            "opex_annual": 23400000,
            "opex_breakdown": {"Фонд оплаты труда": 23400000},
            "current_costs_annual": 23400000,
            "annual_effect": 0,
            "payback_years": None,
            "roi_pct": 0,
            "tco_5years": 117000000,
            "tco_yearly": [23400000, 46800000, 70200000, 93600000, 117000000],
            "sensitivity": {},
            "assumptions": ["Текущий процесс без изменений"],
            "formulas": ["Годовые затраты = 30 × 65000 × 12 = 23 400 000 руб."],
        },
    )
    # Purchase scenario
    purchase = Scenario(
        project_id=demo_project.id,
        name="Покупка AMR Ronavi H1500",
        scenario_type="purchase",
        robot_solution_id=solutions[0].id,  # Ronavi H1500
        parameters={**warehouse.demo_parameters, "staff_reduction_pct": 0.40},
        results={
            "robot_count": 6,
            "capex_total": 33990000,
            "capex_breakdown": {
                "Оборудование": 25200000,
                "Программное обеспечение": 1260000,
                "Внедрение и интеграция": 2520000,
                "Инфраструктура": 900000,
                "Обучение персонала": 200000,
                "Резерв (10%)": 3010800,
            },
            "opex_annual": 3780000,
            "opex_breakdown": {
                "Сервисное обслуживание": 1500000,
                "Электроэнергия": 216000,
                "Связь и коммуникации": 60000,
                "Расходные материалы": 50000,
                "Персонал эксплуатации": 1680000,
                "Лицензии ПО": 0,
            },
            "current_costs_annual": 23400000,
            "annual_effect": 5580000,
            "payback_years": 6.09,
            "roi_pct": 82.1,
            "tco_5years": 52890000,
            "tco_yearly": [37770000, 41550000, 45330000, 49110000, 52890000],
            "sensitivity": {},
            "assumptions": [
                "Количество персонала: 30 чел.",
                "Средняя зарплата: 65 000 руб./мес.",
                "Коэффициент сокращения персонала: 40%",
            ],
            "formulas": ["N_роботов = ⌈120 / (30 × 0.85 × 0.95)⌉ × 1.1 ≈ 6"],
        },
    )
    db.add_all([baseline, purchase])
    db.commit()
