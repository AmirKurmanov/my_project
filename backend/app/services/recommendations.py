"""
Сервис подбора и ранжирования робототехнических решений.

Критерии подбора:
- Соответствие типу объекта
- Грузоподъёмность vs масса грузов
- Габариты vs ширина проходов
- Производительность vs потребность
- Тип навигации
- Условия эксплуатации
"""
from typing import List, Dict, Any
from app.schemas import RecommendationItem


def match_solutions(
    object_type_slug: str,
    parameters: Dict[str, Any],
    solutions: list,
) -> List[RecommendationItem]:
    """Подбор и ранжирование решений под параметры объекта."""
    results = []

    cargo_weight = float(parameters.get("avg_cargo_weight_kg", 0))
    aisle_width = float(parameters.get("min_aisle_width_mm",
                       parameters.get("available_aisle_width_mm", 3000)))
    peak_ops = float(parameters.get("peak_operations_per_hour",
                    parameters.get("incoming_operations_per_day", 500) / 8))

    for sol in solutions:
        score = 0
        reasons = []
        warnings = []
        excluded = False
        excluded_reasons = []

        # 1. Object type compatibility (weight: 30)
        supported_types = sol.supported_object_types or []
        if object_type_slug in supported_types:
            score += 30
            reasons.append(f"Поддерживает тип объекта: {object_type_slug}")
        elif len(supported_types) == 0:
            score += 10
            warnings.append("Нет данных о поддерживаемых типах объектов")
        else:
            excluded = True
            excluded_reasons.append(
                f"Не поддерживает данный тип объекта. Поддерживает: {', '.join(supported_types)}"
            )

        # 2. Payload capacity check (weight: 25)
        if sol.payload_capacity_kg and cargo_weight > 0:
            if sol.payload_capacity_kg >= cargo_weight:
                score += 25
                reasons.append(
                    f"Грузоподъёмность {sol.payload_capacity_kg} кг ≥ масса груза {cargo_weight} кг"
                )
            elif sol.payload_capacity_kg >= cargo_weight * 0.8:
                score += 10
                warnings.append(
                    f"Грузоподъёмность {sol.payload_capacity_kg} кг близка к пределу "
                    f"({cargo_weight} кг)"
                )
            else:
                excluded = True
                excluded_reasons.append(
                    f"Недостаточная грузоподъёмность: {sol.payload_capacity_kg} кг < {cargo_weight} кг"
                )
        elif sol.payload_capacity_kg:
            score += 15
            reasons.append(f"Грузоподъёмность: {sol.payload_capacity_kg} кг")

        # 3. Dimensional compatibility (weight: 15)
        if sol.min_aisle_width_mm and aisle_width > 0:
            if aisle_width >= sol.min_aisle_width_mm:
                score += 15
                reasons.append(f"Ширина проходов достаточна ({aisle_width} мм ≥ {sol.min_aisle_width_mm} мм)")
            else:
                excluded = True
                excluded_reasons.append(
                    f"Недостаточная ширина проходов: {aisle_width} мм < {sol.min_aisle_width_mm} мм"
                )
        else:
            score += 8

        # 4. Productivity match (weight: 15)
        if sol.productivity_per_hour and peak_ops > 0:
            capacity_ratio = sol.productivity_per_hour / peak_ops
            if capacity_ratio >= 0.1:
                score += 15
                reasons.append(
                    f"Производительность: {sol.productivity_per_hour} оп./ч"
                )
            else:
                warnings.append("Низкая производительность — потребуется много единиц")
                score += 5
        else:
            score += 7

        # 5. Navigation and conditions (weight: 10)
        if sol.navigation_type:
            score += 5
            reasons.append(f"Навигация: {sol.navigation_type}")
        if sol.operating_conditions:
            score += 5
            reasons.append(f"Условия: {sol.operating_conditions}")

        # 6. Cost attractiveness (weight: 5)
        if sol.equipment_cost_rub:
            if sol.equipment_cost_rub < 3000000:
                score += 5
                reasons.append("Относительно доступная стоимость")
            elif sol.equipment_cost_rub < 8000000:
                score += 3
            else:
                score += 1
                warnings.append("Высокая стоимость единицы оборудования")

        # Data quality notes
        if sol.data_completeness == "minimal":
            warnings.append("Низкая полнота данных — результаты требуют проверки")
        elif sol.data_completeness == "partial":
            warnings.append("Неполные данные — часть характеристик приблизительна")

        results.append(RecommendationItem(
            solution=sol,
            score=min(score, 100),
            reasons=reasons,
            warnings=warnings,
            excluded=excluded,
            excluded_reasons=excluded_reasons,
        ))

    # Sort: non-excluded first, then by score descending
    results.sort(key=lambda x: (-int(not x.excluded), -x.score))
    return results
