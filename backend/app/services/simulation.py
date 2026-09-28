"""
Сервис имитационного моделирования для 2D-визуализации.
Генерирует данные о расположении зон, маршрутах роботов и KPI.
"""
import math
import random
from typing import Dict, Any, List


def generate_facility_layout(object_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Генерация схемы объекта с зонами."""
    area = float(params.get("area_sqm", 5000))
    width = math.sqrt(area * 1.5)
    height = area / width

    if object_type == "warehouse":
        zones = [
            {"id": "receiving", "name": "Зона приёмки", "x": 0.02, "y": 0.3, "w": 0.15, "h": 0.4, "color": "#3b82f6"},
            {"id": "storage", "name": "Зона хранения", "x": 0.20, "y": 0.05, "w": 0.40, "h": 0.9, "color": "#6366f1"},
            {"id": "picking", "name": "Зона комплектации", "x": 0.63, "y": 0.05, "w": 0.15, "h": 0.9, "color": "#8b5cf6"},
            {"id": "shipping", "name": "Зона отгрузки", "x": 0.82, "y": 0.3, "w": 0.15, "h": 0.4, "color": "#a855f7"},
            {"id": "charging", "name": "Зарядная станция", "x": 0.02, "y": 0.82, "w": 0.10, "h": 0.12, "color": "#22c55e"},
        ]
        paths = [
            {"from": "receiving", "to": "storage", "waypoints": [[0.17, 0.5], [0.20, 0.5]]},
            {"from": "storage", "to": "picking", "waypoints": [[0.60, 0.5], [0.63, 0.5]]},
            {"from": "picking", "to": "shipping", "waypoints": [[0.78, 0.5], [0.82, 0.5]]},
            {"from": "storage", "to": "charging", "waypoints": [[0.20, 0.88], [0.12, 0.88]]},
        ]
    elif object_type == "airport":
        zones = [
            {"id": "terminal", "name": "Терминал", "x": 0.05, "y": 0.1, "w": 0.25, "h": 0.8, "color": "#3b82f6"},
            {"id": "baggage", "name": "Багажная зона", "x": 0.35, "y": 0.2, "w": 0.25, "h": 0.3, "color": "#6366f1"},
            {"id": "cargo", "name": "Грузовая зона", "x": 0.35, "y": 0.55, "w": 0.25, "h": 0.3, "color": "#8b5cf6"},
            {"id": "apron", "name": "Перрон", "x": 0.65, "y": 0.1, "w": 0.30, "h": 0.8, "color": "#a855f7"},
            {"id": "charging", "name": "Зарядная станция", "x": 0.05, "y": 0.85, "w": 0.08, "h": 0.1, "color": "#22c55e"},
        ]
        paths = [
            {"from": "terminal", "to": "baggage", "waypoints": [[0.30, 0.35], [0.35, 0.35]]},
            {"from": "baggage", "to": "apron", "waypoints": [[0.60, 0.35], [0.65, 0.35]]},
            {"from": "terminal", "to": "cargo", "waypoints": [[0.30, 0.70], [0.35, 0.70]]},
            {"from": "cargo", "to": "apron", "waypoints": [[0.60, 0.70], [0.65, 0.70]]},
        ]
    else:  # medical
        zones = [
            {"id": "pharmacy", "name": "Аптека", "x": 0.05, "y": 0.05, "w": 0.20, "h": 0.25, "color": "#3b82f6"},
            {"id": "ward", "name": "Палаты", "x": 0.30, "y": 0.05, "w": 0.40, "h": 0.40, "color": "#6366f1"},
            {"id": "kitchen", "name": "Кухня", "x": 0.75, "y": 0.05, "w": 0.20, "h": 0.25, "color": "#8b5cf6"},
            {"id": "laundry", "name": "Прачечная", "x": 0.05, "y": 0.55, "w": 0.20, "h": 0.25, "color": "#a855f7"},
            {"id": "waste", "name": "Утилизация", "x": 0.75, "y": 0.55, "w": 0.20, "h": 0.25, "color": "#ef4444"},
            {"id": "elevator", "name": "Лифт", "x": 0.45, "y": 0.45, "w": 0.10, "h": 0.10, "color": "#f59e0b"},
            {"id": "charging", "name": "Зарядная", "x": 0.05, "y": 0.85, "w": 0.10, "h": 0.10, "color": "#22c55e"},
        ]
        paths = [
            {"from": "pharmacy", "to": "elevator", "waypoints": [[0.25, 0.17], [0.45, 0.17], [0.45, 0.50]]},
            {"from": "kitchen", "to": "elevator", "waypoints": [[0.75, 0.17], [0.55, 0.17], [0.55, 0.50]]},
            {"from": "elevator", "to": "ward", "waypoints": [[0.50, 0.45], [0.50, 0.25]]},
            {"from": "laundry", "to": "elevator", "waypoints": [[0.25, 0.67], [0.45, 0.67], [0.45, 0.55]]},
        ]

    return {
        "width": round(width, 1),
        "height": round(height, 1),
        "zones": zones,
        "paths": paths,
    }


def generate_simulation_data(
    object_type: str,
    params: Dict[str, Any],
    robot_count: int,
    total_steps: int = 200,
) -> Dict[str, Any]:
    """Генерация данных симуляции: позиции роботов по шагам + KPI."""
    layout = generate_facility_layout(object_type, params)
    zones = layout["zones"]
    paths = layout["paths"]

    # Initialize robots at charging/first zone
    robots = []
    for i in range(robot_count):
        start_zone = zones[0]
        robots.append({
            "id": i,
            "x": start_zone["x"] + start_zone["w"] / 2 + random.uniform(-0.02, 0.02),
            "y": start_zone["y"] + start_zone["h"] / 2 + random.uniform(-0.02, 0.02),
            "state": "idle",
            "target_zone": None,
        })

    # Generate timestep data
    frames = []
    operations_completed = 0
    total_idle_time = 0
    total_active_time = 0

    for step in range(total_steps):
        frame_robots = []
        for robot in robots:
            # Simple behavior: move between random zones
            if robot["state"] == "idle" or random.random() < 0.05:
                target = random.choice(zones)
                robot["target_zone"] = target["id"]
                robot["state"] = "moving"

            # Move towards target
            if robot["target_zone"]:
                target_zone = next((z for z in zones if z["id"] == robot["target_zone"]), zones[0])
                tx = target_zone["x"] + target_zone["w"] / 2
                ty = target_zone["y"] + target_zone["h"] / 2
                dx = tx - robot["x"]
                dy = ty - robot["y"]
                dist = math.sqrt(dx ** 2 + dy ** 2)

                if dist < 0.03:
                    robot["state"] = "working"
                    operations_completed += 1
                    robot["target_zone"] = None
                    total_active_time += 1
                else:
                    speed = 0.015
                    robot["x"] += (dx / dist) * speed
                    robot["y"] += (dy / dist) * speed
                    robot["state"] = "moving"
                    total_active_time += 1
            else:
                total_idle_time += 1

            frame_robots.append({
                "id": robot["id"],
                "x": round(robot["x"], 4),
                "y": round(robot["y"], 4),
                "state": robot["state"],
            })

        frames.append({"step": step, "robots": frame_robots})

    total_time = total_idle_time + total_active_time
    utilization = (total_active_time / total_time * 100) if total_time > 0 else 0

    kpis = {
        "throughput": operations_completed,
        "utilization_pct": round(utilization, 1),
        "idle_time_pct": round(100 - utilization, 1),
        "operations_per_robot": round(operations_completed / max(robot_count, 1), 1),
        "bottleneck_zone": max(zones, key=lambda z: random.random())["name"],
    }

    return {
        "layout": layout,
        "frames": frames,
        "kpis": kpis,
        "total_steps": total_steps,
        "robot_count": robot_count,
    }
