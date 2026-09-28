import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getSolution } from '../api'
import { Bot, ArrowLeft, MapPin, Zap, Weight, Battery, Crosshair, Navigation } from 'lucide-react'

export default function CatalogDetail() {
  const { id } = useParams()
  const [sol, setSol] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      getSolution(Number(id)).then((res) => setSol(res.data)).catch(() => {}).finally(() => setLoading(false))
    }
  }, [id])

  const fmt = (v: number) => v ? new Intl.NumberFormat('ru-RU').format(v) : '—'

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>
  if (!sol) return <div className="text-center py-20 text-gray-500">Решение не найдено</div>

  const specs = [
    { group: 'Идентификация', items: [
      { label: 'Производитель', value: sol.manufacturer },
      { label: 'Категория', value: sol.category?.name },
      { label: 'Страна', value: sol.country },
      { label: 'Доступность', value: sol.availability_status },
    ]},
    { group: 'Технические характеристики', items: [
      { label: 'Грузоподъёмность', value: sol.payload_capacity_kg ? `${sol.payload_capacity_kg} кг` : '—' },
      { label: 'Габариты (Д×Ш×В)', value: sol.length_mm ? `${sol.length_mm}×${sol.width_mm}×${sol.height_mm} мм` : '—' },
      { label: 'Макс. скорость', value: sol.max_speed_ms ? `${sol.max_speed_ms} м/с` : '—' },
      { label: 'Производительность', value: sol.productivity_per_hour ? `${sol.productivity_per_hour} оп./ч` : '—' },
      { label: 'Автономность', value: sol.battery_life_hours ? `${sol.battery_life_hours} ч` : '—' },
      { label: 'Точность позиционирования', value: sol.positioning_accuracy_mm ? `±${sol.positioning_accuracy_mm} мм` : '—' },
      { label: 'Навигация', value: sol.navigation_type || '—' },
      { label: 'Условия эксплуатации', value: sol.operating_conditions || '—' },
    ]},
    { group: 'Инфраструктура', items: [
      { label: 'Мин. ширина прохода', value: sol.min_aisle_width_mm ? `${sol.min_aisle_width_mm} мм` : '—' },
      { label: 'Зарядные станции', value: sol.charging_stations_required ? 'Требуются' : 'Не требуются' },
      { label: 'Связь', value: sol.connectivity_requirements || '—' },
      { label: 'Интеграция', value: sol.integration_options || '—' },
    ]},
    { group: 'Экономика', items: [
      { label: 'Стоимость оборудования', value: `${fmt(sol.equipment_cost_rub)} ₽` },
      { label: 'Стоимость ПО', value: `${fmt(sol.software_cost_rub)} ₽` },
      { label: 'Стоимость внедрения', value: `${fmt(sol.implementation_cost_rub)} ₽` },
      { label: 'Годовое обслуживание', value: `${fmt(sol.annual_maintenance_cost_rub)} ₽` },
      { label: 'Модель приобретения', value: sol.acquisition_model === 'both' ? 'Покупка / Аренда' : sol.acquisition_model === 'raas' ? 'Аренда (RaaS)' : 'Покупка' },
      { label: 'Срок службы', value: sol.service_life_years ? `${sol.service_life_years} лет` : '—' },
    ]},
    { group: 'Применимость', items: [
      { label: 'Процессы', value: sol.supported_processes?.join(', ') || '—' },
      { label: 'Типы объектов', value: sol.supported_object_types?.join(', ') || '—' },
      { label: 'Ограничения', value: sol.limitations || 'Не указаны' },
    ]},
    { group: 'Качество данных', items: [
      { label: 'Источник', value: sol.data_source || '—' },
      { label: 'Полнота', value: sol.data_completeness === 'full' ? 'Полные данные' : sol.data_completeness === 'partial' ? 'Частичные' : 'Минимальные' },
    ]},
  ]

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <Link to="/catalog" className="inline-flex items-center text-primary-600 hover:underline mb-6">
        <ArrowLeft className="h-4 w-4 mr-1" /> Назад к каталогу
      </Link>

      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="h-48 bg-gradient-to-br from-primary-500 to-indigo-600 flex items-center justify-center">
          <Bot className="h-24 w-24 text-white/80" />
        </div>
        <div className="p-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{sol.name}</h1>
              <p className="text-gray-500 mt-1">{sol.manufacturer} • {sol.country}</p>
            </div>
            <span className="bg-primary-50 text-primary-700 px-3 py-1 rounded-full text-sm font-medium">
              {sol.category?.name?.split('(')[0]?.trim()}
            </span>
          </div>
          <p className="text-gray-600 mb-8">{sol.description}</p>

          {specs.map((group) => (
            <div key={group.group} className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b">{group.group}</h2>
              <div className="grid md:grid-cols-2 gap-3">
                {group.items.map((item) => (
                  <div key={item.label} className="flex justify-between py-1.5">
                    <span className="text-gray-500 text-sm">{item.label}</span>
                    <span className="text-gray-900 text-sm font-medium text-right max-w-[60%]">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="mt-8 flex gap-4">
            <Link to="/projects/new" className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors">
              Добавить в проект
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
