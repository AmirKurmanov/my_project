import io
import math
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Project, Scenario, User
from app.auth import get_required_user

router = APIRouter(prefix="/api/projects", tags=["Экспорт"])

@router.get("/{project_id}/export/excel")
def export_excel(
    project_id: int,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    import pandas as pd
    from openpyxl.styles import Font, PatternFill, Alignment

    project = (
        db.query(Project)
        .options(joinedload(Project.object_type), joinedload(Project.scenarios))
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        status_map = {"draft": "Черновик", "calculated": "Рассчитан"}
        translated_status = status_map.get(project.status, project.status)

        # 1. Info
        info_data = {
            "Параметр": ["Название проекта", "Тип объекта", "Статус", "Дата создания", "Создатель"],
            "Значение": [
                project.name,
                project.object_type.name if project.object_type else "",
                translated_status,
                (project.created_at + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
                user.full_name
            ],
        }
        pd.DataFrame(info_data).to_excel(writer, sheet_name="Информация", index=False)

        # 2. Parameters
        params_data = {"Наименование параметра": [], "Значение": []}
        param_map = {
            "area_sqm": "Площадь, кв.м", "zones_count": "Количество зон", "work_shifts": "Количество смен",
            "incoming_operations_per_day": "Входящих операций в день", "internal_operations_per_day": "Внутренних операций в день",
            "outgoing_operations_per_day": "Исходящих операций в день", "storage_type": "Тип хранения",
            "sku_count": "Количество SKU", "avg_cargo_weight_kg": "Средний вес груза, кг",
            "avg_cargo_length_mm": "Длина груза, мм", "avg_cargo_width_mm": "Ширина груза, мм",
            "avg_cargo_height_mm": "Высота груза, мм", "staff_count": "Количество сотрудников",
            "avg_salary_rub": "Средняя зарплата, руб", "current_productivity": "Текущая производительность",
            "route_length_m": "Длина маршрута, м", "available_aisle_width_mm": "Доступная ширина проезда, мм",
            "peak_operations_per_hour": "Пиковых операций в час", "passenger_traffic_per_day": "Пассажиропоток в день",
            "cleaning_area_sqm": "Площадь уборки, кв.м", "beds_count": "Количество коек", "meals_per_day": "Приемов пищи в день",
            "operation_zone": "Зона работы", "work_mode": "Режим работы", "passenger_flow_per_day": "Пассажиропоток в день",
            "cargo_flow_kg_per_day": "Грузопоток в день, кг", "avg_object_weight_kg": "Средний вес груза/объекта, кг",
            "security_requirements": "Требования безопасности", "has_closed_zones": "Наличие закрытых зон",
            "facility_type": "Тип учреждения", "floors_count": "Количество этажей", "daily_cargo_trips": "Рейсов с грузами в день",
            "daily_linen_trips": "Рейсов с бельем в день", "daily_food_trips": "Рейсов с питанием в день",
            "daily_medicine_trips": "Рейсов с медикаментами в день", "daily_waste_trips": "Рейсов с отходами в день",
            "has_elevators": "Наличие лифтов", "sanitization_requirements": "Требования к дезинфекции",
            "staff_reduction_pct": "Ожидаемое сокращение персонала, %"
        }
        if project.parameters:
            params_data = {
                "Наименование параметра": [param_map.get(k, k) for k in project.parameters.keys()],
                "Значение": list(project.parameters.values()),
            }
        pd.DataFrame(params_data).to_excel(writer, sheet_name="Вводные данные", index=False)

        # 3. Scenarios Overview
        scenarios = project.scenarios
        rows = []
        capex_rows = []
        opex_rows = []
        if scenarios:
            for s in scenarios:
                r = s.results or {}
                rows.append({
                    "Сценарий": s.name,
                    "Тип": "Роботизация" if s.scenario_type == "purchase" else "Текущий процесс (Базовый)",
                    "CAPEX (Итого), руб.": r.get("capex_total", 0),
                    "OPEX в год, руб.": r.get("opex_annual", 0),
                    "Годовой эффект, руб.": r.get("annual_effect", 0),
                    "Срок окупаемости, лет": r.get("payback_years", "-"),
                    "ROI, %": r.get("roi_pct", "-"),
                    "TCO 5 лет, руб.": r.get("tco_5years", 0),
                })
                
                # Breakdown capex
                cb = r.get("capex_breakdown", {})
                for k, v in cb.items():
                    capex_rows.append({"Сценарий": s.name, "Статья CAPEX": k, "Сумма, руб.": v})
                
                # Breakdown opex
                ob = r.get("opex_breakdown", {})
                for k, v in ob.items():
                    opex_rows.append({"Сценарий": s.name, "Статья OPEX": k, "Сумма в год, руб.": v})

        if not rows:
            rows.append({"Сценарий": "Нет данных. Запустите расчет экономики в проекте.", "Тип": "", "CAPEX (Итого), руб.": "", "OPEX в год, руб.": "", "Годовой эффект, руб.": "", "Срок окупаемости, лет": "", "ROI, %": "", "TCO 5 лет, руб.": ""})
        if not capex_rows:
            capex_rows.append({"Сценарий": "Нет данных", "Статья CAPEX": "", "Сумма, руб.": ""})
        if not opex_rows:
            opex_rows.append({"Сценарий": "Нет данных", "Статья OPEX": "", "Сумма в год, руб.": ""})

        pd.DataFrame(rows).to_excel(writer, sheet_name="Сравнение сценариев", index=False)
        pd.DataFrame(capex_rows).to_excel(writer, sheet_name="Детализация CAPEX", index=False)
        pd.DataFrame(opex_rows).to_excel(writer, sheet_name="Детализация OPEX", index=False)

        # Apply simple formatting to all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            # Headers
            for cell in worksheet[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1E3A8A", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            # Widths
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = min(adjusted_width, 50)

    output.seek(0)
    filename = f"robomatch_project_{project_id}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{project_id}/export/pdf")
def export_pdf(
    project_id: int,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Register fonts
    fonts_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    pdfmetrics.registerFont(TTFont('Roboto', os.path.join(fonts_dir, 'Roboto-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto-Bold', os.path.join(fonts_dir, 'Roboto-Bold.ttf')))

    project = (
        db.query(Project)
        .options(joinedload(Project.object_type), joinedload(Project.scenarios))
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=15 * mm, bottomMargin=15 * mm, leftMargin=15 * mm, rightMargin=15 * mm)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CyrillicTitle', fontName='Roboto-Bold', fontSize=18, spaceAfter=15))
    styles.add(ParagraphStyle(name='CyrillicHeading', fontName='Roboto-Bold', fontSize=14, spaceAfter=10, spaceBefore=15))
    styles.add(ParagraphStyle(name='CyrillicNormal', fontName='Roboto', fontSize=10))

    elements = []

    # Title
    elements.append(Paragraph(f"Отчет RoboMatch: {project.name}", styles["CyrillicTitle"]))

    # Project info
    elements.append(Paragraph("Информация о проекте", styles["CyrillicHeading"]))
    status_map = {"draft": "Черновик", "calculated": "Рассчитан"}
    translated_status = status_map.get(project.status, project.status)

    info_table = Table([
        ["Проект", project.name],
        ["Тип объекта", project.object_type.name if project.object_type else ""],
        ["Статус", translated_status],
        ["Дата расчета", (project.created_at + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M")],
    ], colWidths=[150, 400])
    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e0e7ff")),
        ("FONTNAME", (0, 0), (-1, -1), 'Roboto'),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 5 * mm))

    # Scenarios
    scenarios = project.scenarios
    if scenarios:
        elements.append(Paragraph("Сравнение сценариев роботизации", styles["CyrillicHeading"]))
        header = ["Сценарий", "Тип", "CAPEX, руб.", "OPEX/год, руб.", "Годовой эффект, руб.", "Окупаемость, лет", "ROI, %", "TCO 5 лет, руб."]
        rows = [header]
        for s in scenarios:
            r = s.results or {}
            rows.append([
                s.name[:30],
                "Роботизация" if s.scenario_type == "purchase" else "Базовый",
                f"{r.get('capex_total', 0):,.0f}".replace(',', ' '),
                f"{r.get('opex_annual', 0):,.0f}".replace(',', ' '),
                f"{r.get('annual_effect', 0):,.0f}".replace(',', ' ') if r.get('annual_effect') else "-",
                f"{r.get('payback_years', '-')}" if r.get("payback_years") else "-",
                f"{r.get('roi_pct', 0):.1f}" if r.get("roi_pct") else "-",
                f"{r.get('tco_5years', 0):,.0f}".replace(',', ' ') if r.get("tco_5years") else "-",
            ])
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), 'Roboto'),
            ("FONTNAME", (0, 0), (-1, 0), 'Roboto-Bold'),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (1, -1), "LEFT"),
        ]))
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    filename = f"robomatch_project_{project_id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
