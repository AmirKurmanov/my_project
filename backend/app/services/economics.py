"""
Сервис экономических расчётов.

Формулы согласно ТЗ:
- Количество роботов = пиковая потребность / (производительность × загрузка × доступность) × резерв
- CAPEX = оборудование + инфраструктура + ПО + интеграция + пусконаладка + обучение + резерв
- OPEX = сервис + лицензии + электроэнергия + связь + расходные + ремонт + персонал
- Годовой эффект = сокращение затрат + доп.доход − доп.OPEX
- Срок окупаемости = CAPEX / годовой эффект
- ROI = накопленный эффект / CAPEX × 100%
- TCO = CAPEX + сумма OPEX за горизонт + замена компонентов
"""
import math
from typing import Dict, Any, Optional


# ──────────────────────────────────────────────────────────────
#  1. Количество роботов
# ──────────────────────────────────────────────────────────────

def calculate_robot_count(
    peak_operations_per_hour: float,
    robot_productivity_per_hour: float,
    utilization_factor: float = 0.85,
    availability: float = 0.95,
    reserve_factor: float = 1.1,
) -> int:
    """
    N = ⌈ peak_ops / (prod × utilization × availability) ⌉ × reserve
    """
    if robot_productivity_per_hour <= 0:
        return 1
    effective = robot_productivity_per_hour * utilization_factor * availability
    return max(1, math.ceil(peak_operations_per_hour / effective * reserve_factor))


# ──────────────────────────────────────────────────────────────
#  2. CAPEX — капитальные затраты
# ──────────────────────────────────────────────────────────────

def calculate_capex(
    robot_count: int,
    equipment_cost: float,
    software_cost: float = 0,
    implementation_cost: float = 0,
    training_cost: float = 200_000,
    infrastructure_cost: float = 0,
    reserve_pct: float = 0.10,
) -> Dict[str, Any]:
    """
    CAPEX = (N × Цена_ед) + ПО + Внедрение + Инфраструктура + Обучение + Резерв
    """
    equipment_total = robot_count * equipment_cost

    # Авто-оценки если не заданы
    if infrastructure_cost == 0:
        # Зарядные станции: 1 на 3 робота, ~150 000 ₽ за станцию
        infrastructure_cost = max(1, math.ceil(robot_count / 3)) * 150_000
    if software_cost == 0:
        software_cost = equipment_total * 0.05
    if implementation_cost == 0:
        implementation_cost = equipment_total * 0.10

    subtotal = (
        equipment_total
        + software_cost
        + implementation_cost
        + training_cost
        + infrastructure_cost
    )
    reserve = subtotal * reserve_pct
    total = subtotal + reserve

    return {
        "total": round(total, 2),
        "breakdown": {
            "Оборудование": round(equipment_total, 2),
            "Программное обеспечение": round(software_cost, 2),
            "Внедрение и интеграция": round(implementation_cost, 2),
            "Инфраструктура (зарядные станции и др.)": round(infrastructure_cost, 2),
            "Обучение персонала": round(training_cost, 2),
            "Резерв (10%)": round(reserve, 2),
        },
    }


# ──────────────────────────────────────────────────────────────
#  3. OPEX — ежегодные операционные расходы
# ──────────────────────────────────────────────────────────────

def calculate_opex(
    robot_count: int,
    annual_maintenance_per_robot: float,
    energy_cost_annual: float = 0,
    connectivity_cost_annual: float = 60_000,
    consumables_annual: float = 50_000,
    operating_staff_cost: float = 0,
    software_license_annual: float = 0,
) -> Dict[str, Any]:
    """
    OPEX = Обслуживание + Энергия + Связь + Расходники + Персонал + Лицензии
    """
    maintenance_total = robot_count * annual_maintenance_per_robot

    if energy_cost_annual == 0:
        # ~3 кВт·ч на робота × 24 ч × 365 дн × 7 ₽/кВт·ч ≈ 36 500 ₽/год
        energy_cost_annual = robot_count * 36_500

    if operating_staff_cost == 0:
        # 1 оператор на 5 роботов, з/п 70 000 ₽/мес
        operators = max(1, math.ceil(robot_count / 5))
        operating_staff_cost = operators * 70_000 * 12

    total = (
        maintenance_total
        + energy_cost_annual
        + connectivity_cost_annual
        + consumables_annual
        + operating_staff_cost
        + software_license_annual
    )

    return {
        "total": round(total, 2),
        "breakdown": {
            "Сервисное обслуживание": round(maintenance_total, 2),
            "Электроэнергия": round(energy_cost_annual, 2),
            "Связь и коммуникации": round(connectivity_cost_annual, 2),
            "Расходные материалы": round(consumables_annual, 2),
            "Персонал эксплуатации": round(operating_staff_cost, 2),
            "Лицензии ПО": round(software_license_annual, 2),
        },
    }


# ──────────────────────────────────────────────────────────────
#  4. Годовой эффект
# ──────────────────────────────────────────────────────────────

def calculate_annual_effect(
    current_labor_cost: float,
    staff_reduction_pct: float,
    additional_savings: float = 0,
    new_opex: float = 0,
) -> float:
    """
    Эффект = ФОТ_текущий × % сокращения + доп.экономия − OPEX_роботов
    """
    labor_savings = current_labor_cost * staff_reduction_pct
    return round(labor_savings + additional_savings - new_opex, 2)


# ──────────────────────────────────────────────────────────────
#  5. Окупаемость
# ──────────────────────────────────────────────────────────────

def calculate_payback(capex: float, annual_effect: float) -> Optional[float]:
    """Простой срок окупаемости (лет). None если эффект ≤ 0."""
    if annual_effect <= 0:
        return None
    return round(capex / annual_effect, 1)


# ──────────────────────────────────────────────────────────────
#  6. ROI
# ──────────────────────────────────────────────────────────────

def calculate_roi(annual_effect: float, capex: float, years: int = 5) -> float:
    """ROI = (Эффект × T) / CAPEX × 100%."""
    if capex <= 0:
        return 0
    return round((annual_effect * years) / capex * 100, 1)


# ──────────────────────────────────────────────────────────────
#  7. TCO
# ──────────────────────────────────────────────────────────────

def calculate_tco(
    capex: float,
    annual_opex: float,
    years: int = 5,
    replacement_cost: float = 0,
    replacement_year: int = 7,
) -> Dict[str, Any]:
    """TCO = CAPEX + Σ(OPEX) + замена компонентов (если горизонт >= срока службы)."""
    yearly = []
    cumulative = capex
    for y in range(1, years + 1):
        cumulative += annual_opex
        if y == replacement_year and replacement_cost > 0:
            cumulative += replacement_cost
        yearly.append(round(cumulative, 2))

    return {"total": round(cumulative, 2), "yearly": yearly}


# ──────────────────────────────────────────────────────────────
#  8. Анализ чувствительности
# ──────────────────────────────────────────────────────────────

def calculate_sensitivity(
    base_result: Dict[str, Any],
    base_params: Dict[str, Any],
    robot,
    scenario_type: str,
    param_names: list = None,
    variations: list = None,
) -> Dict[str, Any]:
    """Пересчёт экономики при изменении параметра на ±10–20%."""
    if param_names is None:
        param_names = ["equipment_cost_rub", "staff_count", "avg_salary_rub"]
    if variations is None:
        variations = [-20, -10, 0, 10, 20]

    sensitivity = {}
    labels_map = {
        "equipment_cost_rub": "Стоимость оборудования",
        "staff_count": "Численность персонала",
        "avg_salary_rub": "Средняя зарплата",
        "peak_operations_per_hour": "Пиковые операции в час",
    }

    for param in param_names:
        results = []

        # Базовое значение
        if param == "equipment_cost_rub" and robot:
            base_value = robot.equipment_cost_rub or 2_500_000
        else:
            base_value = float(base_params.get(param, 0))

        if base_value == 0:
            continue

        for pct in variations:
            modified = base_params.copy()
            if param == "equipment_cost_rub":
                class MockRobot:
                    pass
                mr = MockRobot()
                for attr in dir(robot):
                    if not attr.startswith('_'):
                        try:
                            setattr(mr, attr, getattr(robot, attr))
                        except Exception:
                            pass
                mr.equipment_cost_rub = base_value * (1 + pct / 100)
                calc = full_calculation(modified, mr, scenario_type)
            else:
                modified[param] = base_value * (1 + pct / 100)
                calc = full_calculation(modified, robot, scenario_type)

            results.append({
                "variation_pct": pct,
                "payback_years": calc.get("payback_years"),
                "roi_pct": calc.get("roi_pct"),
                "annual_effect": calc.get("annual_effect"),
            })

        sensitivity[labels_map.get(param, param)] = results

    return sensitivity


# ──────────────────────────────────────────────────────────────
#  9. Полный расчёт (собирает всё вместе)
# ──────────────────────────────────────────────────────────────

def full_calculation(
    params: Dict[str, Any],
    robot,
    scenario_type: str,
) -> Dict[str, Any]:
    """Полный экономический расчёт для одного сценария."""

    # ── Параметры объекта ──────────────────────────────────
    staff_count = float(params.get("staff_count", 20))
    avg_salary = float(params.get("avg_salary_rub", 60_000))
    work_shifts = int(params.get("work_shifts", 2))
    hours_per_day = work_shifts * 8
    horizon_years = int(params.get("horizon_years", 5))

    # Пиковые операции в час
    if params.get("peak_operations_per_hour"):
        peak_ops = float(params["peak_operations_per_hour"])
    else:
        # Суммируем все потоки если есть
        daily_ops = 0
        for key in [
            "incoming_operations_per_day",
            "internal_operations_per_day",
            "outgoing_operations_per_day",
            "daily_cargo_trips",
            "daily_linen_trips",
            "daily_food_trips",
            "daily_medicine_trips",
            "daily_waste_trips",
            "cargo_flow_kg_per_day",
        ]:
            val = params.get(key)
            if val is not None:
                daily_ops += float(val)

        if daily_ops == 0:
            daily_ops = 500  # дефолт

        # Среднечасовая нагрузка × пиковый коэффициент 1.3
        peak_ops = daily_ops / hours_per_day * 1.3

    # ── Характеристики робота ──────────────────────────────
    robot_productivity = robot.productivity_per_hour or 30
    equipment_cost = robot.equipment_cost_rub or 2_500_000
    software_cost = robot.software_cost_rub or 0
    implementation_cost = robot.implementation_cost_rub or 0
    maintenance_cost = robot.annual_maintenance_cost_rub or (equipment_cost * 0.05)
    service_life = robot.service_life_years or 7

    # ── Текущие затраты (ФОТ) ──────────────────────────────
    # ФОТ = кол-во × з/п × 12 мес × 1.302 (страховые взносы 30.2%)
    current_labor_cost = staff_count * avg_salary * 12 * 1.302

    # ── Количество роботов ─────────────────────────────────
    robot_count = calculate_robot_count(
        peak_operations_per_hour=peak_ops,
        robot_productivity_per_hour=robot_productivity,
    )
    # Ограничение здравого смысла: не больше штата × 1.5
    max_robots = max(int(staff_count * 1.5), 5)
    robot_count = min(robot_count, max_robots)

    # ── Доля сокращения персонала ──────────────────────────
    staff_reduction_pct = float(params.get("staff_reduction_pct", 0.40))

    # ── Расчёт по типу сценария ────────────────────────────
    if scenario_type == "raas":
        # RaaS: нет CAPEX, повышенный OPEX (ежемесячная плата за робота)
        # Типовая аренда ≈ 2–4% стоимости в месяц
        monthly_fee_per_robot = equipment_cost * 0.025
        raas_annual = robot_count * monthly_fee_per_robot * 12

        capex_data = {
            "total": 0,
            "breakdown": {"Арендная модель — без капитальных затрат": 0},
        }

        opex_data = calculate_opex(
            robot_count=robot_count,
            annual_maintenance_per_robot=0,     # входит в аренду
            software_license_annual=0,          # входит в аренду
        )
        # Добавляем арендные платежи
        opex_data["total"] += raas_annual
        opex_data["breakdown"]["Арендные платежи (RaaS)"] = round(raas_annual, 2)

        annual_effect = calculate_annual_effect(
            current_labor_cost, staff_reduction_pct,
            new_opex=opex_data["total"],
        )
        capex_total = 0

    else:
        # Покупка
        capex_data = calculate_capex(
            robot_count=robot_count,
            equipment_cost=equipment_cost,
            software_cost=software_cost,
            implementation_cost=implementation_cost,
        )
        opex_data = calculate_opex(
            robot_count=robot_count,
            annual_maintenance_per_robot=maintenance_cost,
        )
        annual_effect = calculate_annual_effect(
            current_labor_cost, staff_reduction_pct,
            new_opex=opex_data["total"],
        )
        capex_total = capex_data["total"]

    # ── Окупаемость и ROI ──────────────────────────────────
    if capex_total > 0:
        payback = calculate_payback(capex_total, annual_effect)
        roi = calculate_roi(annual_effect, capex_total, horizon_years)
    else:
        # RaaS: окупаемость = 0 (нет капзатрат), ROI считаем от OPEX
        payback = 0
        roi = round(annual_effect / opex_data["total"] * 100, 1) if opex_data["total"] > 0 else 0

    # ── TCO ─────────────────────────────────────────────────
    replacement_cost = capex_data["total"] * 0.3 if service_life <= horizon_years else 0
    tco_data = calculate_tco(
        capex_total,
        opex_data["total"],
        horizon_years,
        replacement_cost=replacement_cost,
        replacement_year=service_life,
    )

    # ── Допущения ──────────────────────────────────────────
    assumptions = [
        f"Текущий персонал: {int(staff_count)} чел. × {avg_salary:,.0f} ₽/мес (с учётом взносов 30.2%)",
        f"Сокращение персонала: {staff_reduction_pct * 100:.0f}%",
        f"Пиковая нагрузка: {peak_ops:.0f} операций/час",
        f"Производительность робота: {robot_productivity} операций/час",
        f"Загрузка робота: 85%, доступность: 95%, резерв: 10%",
        f"Горизонт расчёта: {horizon_years} лет, срок службы: {service_life} лет",
    ]

    formulas = [
        "N_роботов = ⌈ Пик_опер / (Произв × 0.85 × 0.95) ⌉ × 1.1",
        "CAPEX = (N × Цена) + ПО + Внедрение + Инфра + Обучение + Резерв_10%",
        "OPEX = Обслуж. + Энергия + Связь + Расходники + Персонал + Лицензии",
        "Эффект = ФОТ × %_сокращения − OPEX_роботов",
        "Окупаемость = CAPEX / Эффект_год",
        "ROI = (Эффект × Т) / CAPEX × 100%",
        "TCO = CAPEX + Σ OPEX + Замена (если Т ≥ срок службы)",
    ]

    return {
        "robot_count": robot_count,
        "peak_ops_per_hour": round(peak_ops, 1),
        "capex_total": capex_total,
        "capex_breakdown": capex_data["breakdown"],
        "opex_annual": opex_data["total"],
        "opex_breakdown": opex_data["breakdown"],
        "current_costs_annual": round(current_labor_cost, 2),
        "annual_effect": annual_effect,
        "payback_years": payback,
        "roi_pct": roi,
        "tco_5years": tco_data["total"],
        "tco_yearly": tco_data["yearly"],
        "sensitivity": {},
        "assumptions": assumptions,
        "formulas": formulas,
    }
