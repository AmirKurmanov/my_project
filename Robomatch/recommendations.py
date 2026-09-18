from pydantic import BaseModel 
from robots import robots

class RecommendationRequest(BaseModel):
    object_type: str 
    area_m2: float
    workers: int
    shifts: int
    task: str
    load_kg: float

def calculate_roi(robot_price: float, workers: int, shifts: int):
    monthly_worker_cost = 60_000

    workers_replaced = min(workers, 5)

    monthly_saving = (
        workers_replaced * monthly_worker_cost * shifts
    )

    yearly_saving = monthly_saving * 12

    payback_months = robot_price / monthly_saving

    five_year_saving = (
        yearly_saving * 5
    ) - robot_price

    return {
        "robot_price": robot_price, 
        "workers_replaced": workers_replaced, 
        "monthly_saving": monthly_saving, 
        "yearly_saving": yearly_saving, 
        "payback_months": round(payback_months, 1), 
        "five_year_saving": five_year_saving
    }

def recomend_robot(data: RecommendationRequest):
    results = []

    task = data.task.lower()

    for robot in robots:
        score = 0
        reasons = []

        if data.object_type in robot.get("objects", []):
            score += 40
            reasons.append("Подходит для данного типа объекта")

        if "короб" in task and "коробки" in robot.get("tasks", []):
            score += 40
            reasons.append("Подходит для работы с коробками")

        if "паллет" in task and "паллеты" in robot.get("tasks", []):
            score += 40
            reasons.append("Подходит для работы с паллетами")

        if "транспорт" in task and "транспортировка " in robot.get("tasks", []):
            score += 40
            reasons.append("Подходит для транспортировки")

        if robot["load"] >= data.load_kg :
            score += 15
            reasons.append("Высокая грузоподъемность")
        else: 
            reasons.append("Грузоподъемность робота недостаточна")

        if data.area_m2 >= 5000:
            score += 10
            reasons.append("Подходит для работы на больших участках")

        if data.shifts >= 2:
            score += 5
            reasons.append("Подходит для р аботы в несколько смен")

        if data.workers >= 20:
            score += 5
            reasons.append("Подходит для объекта с большим количеством сотрудников")
            
        score = min(score, 100)

        roi = calculate_roi(
            robot_price=robot["price"], 
            workers=data.workers, 
            shifts=data.shifts
        )

        results.append({
            "robot": robot, 
            "score": score, 
            "reasons": reasons, 
            "roi": roi
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )
    return results

