import React, { useState, useEffect } from 'react'
import { getSolutions, getCategories, createSolution, updateSolution, deleteSolution } from '../api'
import toast from 'react-hot-toast'
import { Plus, Pencil, Trash2, Save, X, Database, Users, Settings, Bot } from 'lucide-react'

export default function Admin() {
  const [tab, setTab] = useState('catalog')
  const [solutions, setSolutions] = useState<any[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [editId, setEditId] = useState<number | null>(null)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState<any>({
    name: '', manufacturer: '', category_id: '', country: 'Россия',
    description: '', payload_capacity_kg: '', max_speed_ms: '',
    productivity_per_hour: '', battery_life_hours: '',
    equipment_cost_rub: '', annual_maintenance_cost_rub: '',
    service_life_years: '', navigation_type: '', operating_conditions: '',
    min_aisle_width_mm: '', positioning_accuracy_mm: '',
    length_mm: '', width_mm: '', height_mm: '',
    software_cost_rub: '', implementation_cost_rub: '',
    acquisition_model: 'purchase', availability_status: 'В наличии',
    data_source: '', data_completeness: 'full',
    supported_processes: '', supported_object_types: '',
  })

  const load = () => {
    setLoading(true)
    Promise.all([getSolutions({}), getCategories()])
      .then(([solRes, catRes]) => {
        setSolutions(solRes.data)
        setCategories(catRes.data)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const resetForm = () => {
    setForm({
      name: '', manufacturer: '', category_id: '', country: 'Россия',
      description: '', payload_capacity_kg: '', max_speed_ms: '',
      productivity_per_hour: '', battery_life_hours: '',
      equipment_cost_rub: '', annual_maintenance_cost_rub: '',
      service_life_years: '', navigation_type: '', operating_conditions: '',
      min_aisle_width_mm: '', positioning_accuracy_mm: '',
      length_mm: '', width_mm: '', height_mm: '',
      software_cost_rub: '', implementation_cost_rub: '',
      acquisition_model: 'purchase', availability_status: 'В наличии',
      data_source: '', data_completeness: 'full',
      supported_processes: '', supported_object_types: '',
    })
  }

  const handleEdit = (sol: any) => {
    setEditId(sol.id)
    setShowAdd(true)
    setForm({
      name: sol.name || '',
      manufacturer: sol.manufacturer || '',
      category_id: sol.category_id || '',
      country: sol.country || '',
      description: sol.description || '',
      payload_capacity_kg: sol.payload_capacity_kg ?? '',
      max_speed_ms: sol.max_speed_ms ?? '',
      productivity_per_hour: sol.productivity_per_hour ?? '',
      battery_life_hours: sol.battery_life_hours ?? '',
      equipment_cost_rub: sol.equipment_cost_rub ?? '',
      annual_maintenance_cost_rub: sol.annual_maintenance_cost_rub ?? '',
      service_life_years: sol.service_life_years ?? '',
      navigation_type: sol.navigation_type || '',
      operating_conditions: sol.operating_conditions || '',
      min_aisle_width_mm: sol.min_aisle_width_mm ?? '',
      positioning_accuracy_mm: sol.positioning_accuracy_mm ?? '',
      length_mm: sol.length_mm ?? '',
      width_mm: sol.width_mm ?? '',
      height_mm: sol.height_mm ?? '',
      software_cost_rub: sol.software_cost_rub ?? '',
      implementation_cost_rub: sol.implementation_cost_rub ?? '',
      acquisition_model: sol.acquisition_model || 'purchase',
      availability_status: sol.availability_status || 'В наличии',
      data_source: sol.data_source || '',
      data_completeness: sol.data_completeness || 'full',
      supported_processes: sol.supported_processes?.join(', ') || '',
      supported_object_types: sol.supported_object_types?.join(', ') || '',
    })
  }

  const handleSave = async () => {
    if (!form.name || !form.manufacturer || !form.category_id) {
      toast.error('Заполните обязательные поля: название, производитель, категория')
      return
    }

    const data: any = { ...form }
    // Convert numeric fields
    const numFields = [
      'payload_capacity_kg', 'max_speed_ms', 'productivity_per_hour', 'battery_life_hours',
      'equipment_cost_rub', 'annual_maintenance_cost_rub', 'min_aisle_width_mm',
      'positioning_accuracy_mm', 'length_mm', 'width_mm', 'height_mm',
      'software_cost_rub', 'implementation_cost_rub',
    ]
    numFields.forEach(f => {
      data[f] = data[f] === '' ? null : Number(data[f])
    })
    data.category_id = Number(data.category_id)
    data.service_life_years = data.service_life_years === '' ? null : Number(data.service_life_years)
    data.supported_processes = data.supported_processes ? data.supported_processes.split(',').map((s: string) => s.trim()).filter(Boolean) : []
    data.supported_object_types = data.supported_object_types ? data.supported_object_types.split(',').map((s: string) => s.trim()).filter(Boolean) : []

    try {
      if (editId) {
        await updateSolution(editId, data)
        toast.success('Решение обновлено')
      } else {
        await createSolution(data)
        toast.success('Решение добавлено')
      }
      setShowAdd(false)
      setEditId(null)
      resetForm()
      load()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Ошибка сохранения')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить решение из каталога?')) return
    try {
      await deleteSolution(id)
      toast.success('Решение удалено')
      load()
    } catch {
      toast.error('Ошибка удаления')
    }
  }

  const fmt = (v: any) => v != null ? new Intl.NumberFormat('ru-RU').format(v) : '—'

  const tabs = [
    { id: 'catalog', label: 'Каталог решений', icon: Database },
    { id: 'info', label: 'Справочники', icon: Settings },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Панель администратора</h1>
        <p className="text-gray-500 mt-1">Управление каталогом, справочниками и данными платформы</p>
      </div>

      <div className="flex border-b mb-6 overflow-x-auto">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center px-5 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              tab === t.id ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <t.icon className="h-4 w-4 mr-2" /> {t.label}
          </button>
        ))}
      </div>

      {/* Catalog Tab */}
      {tab === 'catalog' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Каталог роботизированных решений ({solutions.length})</h2>
            <button
              onClick={() => { setShowAdd(true); setEditId(null); resetForm() }}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 flex items-center"
            >
              <Plus className="h-4 w-4 mr-1" /> Добавить решение
            </button>
          </div>

          {/* Add/Edit Form */}
          {showAdd && (
            <div className="bg-blue-50 rounded-xl p-6 mb-6 border border-blue-200">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-lg">{editId ? 'Редактирование решения' : 'Новое решение'}</h3>
                <button onClick={() => { setShowAdd(false); setEditId(null); resetForm() }}>
                  <X className="h-5 w-5 text-gray-500" />
                </button>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Название *</label>
                  <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="TransBot-100" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Производитель *</label>
                  <input value={form.manufacturer} onChange={e => setForm({ ...form, manufacturer: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="РобоТех" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Категория *</label>
                  <select value={form.category_id} onChange={e => setForm({ ...form, category_id: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm">
                    <option value="">Выберите</option>
                    {categories.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Страна</label>
                  <input value={form.country} onChange={e => setForm({ ...form, country: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Доступность</label>
                  <select value={form.availability_status} onChange={e => setForm({ ...form, availability_status: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm">
                    <option value="В наличии">В наличии</option>
                    <option value="Под заказ">Под заказ</option>
                    <option value="Разработка">Разработка</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Модель приобретения</label>
                  <select value={form.acquisition_model} onChange={e => setForm({ ...form, acquisition_model: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm">
                    <option value="purchase">Покупка</option>
                    <option value="raas">Аренда (RaaS)</option>
                    <option value="both">Покупка / Аренда</option>
                  </select>
                </div>

                <div className="md:col-span-3">
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Описание</label>
                  <textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm" rows={2} />
                </div>

                {/* Technical specs */}
                <div className="md:col-span-3 border-t pt-4 mt-2">
                  <h4 className="font-medium text-gray-700 mb-3">Технические характеристики</h4>
                  <div className="grid md:grid-cols-4 gap-3">
                    <div>
                      <label className="text-xs text-gray-500 block">Грузоподъёмность (кг)</label>
                      <input type="number" value={form.payload_capacity_kg} onChange={e => setForm({ ...form, payload_capacity_kg: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Скорость (м/с)</label>
                      <input type="number" step="0.1" value={form.max_speed_ms} onChange={e => setForm({ ...form, max_speed_ms: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Производительность (оп./ч)</label>
                      <input type="number" value={form.productivity_per_hour} onChange={e => setForm({ ...form, productivity_per_hour: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Автономность (ч)</label>
                      <input type="number" value={form.battery_life_hours} onChange={e => setForm({ ...form, battery_life_hours: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Длина (мм)</label>
                      <input type="number" value={form.length_mm} onChange={e => setForm({ ...form, length_mm: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Ширина (мм)</label>
                      <input type="number" value={form.width_mm} onChange={e => setForm({ ...form, width_mm: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Высота (мм)</label>
                      <input type="number" value={form.height_mm} onChange={e => setForm({ ...form, height_mm: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Точность (мм)</label>
                      <input type="number" value={form.positioning_accuracy_mm} onChange={e => setForm({ ...form, positioning_accuracy_mm: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Мин. ширина прохода (мм)</label>
                      <input type="number" value={form.min_aisle_width_mm} onChange={e => setForm({ ...form, min_aisle_width_mm: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Навигация</label>
                      <input value={form.navigation_type} onChange={e => setForm({ ...form, navigation_type: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" placeholder="SLAM + LiDAR" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Условия</label>
                      <input value={form.operating_conditions} onChange={e => setForm({ ...form, operating_conditions: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Срок службы (лет)</label>
                      <input type="number" value={form.service_life_years} onChange={e => setForm({ ...form, service_life_years: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                  </div>
                </div>

                {/* Economics */}
                <div className="md:col-span-3 border-t pt-4 mt-2">
                  <h4 className="font-medium text-gray-700 mb-3">Экономика</h4>
                  <div className="grid md:grid-cols-4 gap-3">
                    <div>
                      <label className="text-xs text-gray-500 block">Стоимость оборуд. (₽)</label>
                      <input type="number" value={form.equipment_cost_rub} onChange={e => setForm({ ...form, equipment_cost_rub: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Стоимость ПО (₽)</label>
                      <input type="number" value={form.software_cost_rub} onChange={e => setForm({ ...form, software_cost_rub: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Стоимость внедрения (₽)</label>
                      <input type="number" value={form.implementation_cost_rub} onChange={e => setForm({ ...form, implementation_cost_rub: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Годовое обслуж. (₽)</label>
                      <input type="number" value={form.annual_maintenance_cost_rub} onChange={e => setForm({ ...form, annual_maintenance_cost_rub: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                  </div>
                </div>

                {/* Applicability */}
                <div className="md:col-span-3 border-t pt-4 mt-2">
                  <h4 className="font-medium text-gray-700 mb-3">Применимость и данные</h4>
                  <div className="grid md:grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs text-gray-500 block">Процессы (через запятую)</label>
                      <input value={form.supported_processes} onChange={e => setForm({ ...form, supported_processes: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" placeholder="Транспортировка, Сортировка" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Типы объектов (slugs через запятую)</label>
                      <input value={form.supported_object_types} onChange={e => setForm({ ...form, supported_object_types: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" placeholder="warehouse, airport, medical" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Источник данных</label>
                      <input value={form.data_source} onChange={e => setForm({ ...form, data_source: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block">Полнота данных</label>
                      <select value={form.data_completeness} onChange={e => setForm({ ...form, data_completeness: e.target.value })}
                        className="w-full border rounded-lg px-3 py-1.5 text-sm">
                        <option value="full">Полные</option>
                        <option value="partial">Частичные</option>
                        <option value="minimal">Минимальные</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button onClick={handleSave} className="bg-primary-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 flex items-center">
                  <Save className="h-4 w-4 mr-1" /> {editId ? 'Сохранить' : 'Добавить'}
                </button>
                <button onClick={() => { setShowAdd(false); setEditId(null); resetForm() }} className="text-gray-500 px-4 py-2 text-sm">
                  Отмена
                </button>
              </div>
            </div>
          )}

          {/* Solutions Table */}
          {loading ? (
            <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b">
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Название</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Производитель</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Категория</th>
                    <th className="px-4 py-3 text-right font-medium text-gray-600">Грузоподъёмность</th>
                    <th className="px-4 py-3 text-right font-medium text-gray-600">Цена</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Доступность</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Полнота</th>
                    <th className="px-4 py-3 text-center font-medium text-gray-600">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {solutions.map((sol: any) => (
                    <tr key={sol.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{sol.name}</td>
                      <td className="px-4 py-3 text-gray-600">{sol.manufacturer}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full">
                          {sol.category?.name?.split('(')[0]?.trim() || '—'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">{sol.payload_capacity_kg ? `${sol.payload_capacity_kg} кг` : '—'}</td>
                      <td className="px-4 py-3 text-right">{fmt(sol.equipment_cost_rub)} ₽</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          sol.availability_status === 'В наличии' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                        }`}>{sol.availability_status}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          sol.data_completeness === 'full' ? 'bg-green-100 text-green-700' :
                          sol.data_completeness === 'partial' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {sol.data_completeness === 'full' ? 'Полные' : sol.data_completeness === 'partial' ? 'Частичные' : 'Минимальные'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center gap-2">
                          <button onClick={() => handleEdit(sol)} className="text-blue-500 hover:text-blue-700 p-1" title="Редактировать">
                            <Pencil className="h-4 w-4" />
                          </button>
                          <button onClick={() => handleDelete(sol.id)} className="text-red-400 hover:text-red-600 p-1" title="Удалить">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Info Tab */}
      {tab === 'info' && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Справочники</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-5 shadow-sm border">
              <h3 className="font-semibold mb-3 flex items-center"><Bot className="h-5 w-5 mr-2 text-primary-600" /> Категории решений</h3>
              <div className="space-y-2">
                {categories.map((c: any) => (
                  <div key={c.id} className="flex justify-between items-center py-2 border-b last:border-0">
                    <div>
                      <div className="font-medium text-sm">{c.name}</div>
                      <div className="text-xs text-gray-500">{c.description}</div>
                    </div>
                    <span className="text-xs text-gray-400">{c.slug}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl p-5 shadow-sm border">
              <h3 className="font-semibold mb-3 flex items-center"><Settings className="h-5 w-5 mr-2 text-primary-600" /> Статистика</h3>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">Всего решений в каталоге</span>
                  <span className="font-semibold">{solutions.length}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">Категорий</span>
                  <span className="font-semibold">{categories.length}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">С полными данными</span>
                  <span className="font-semibold">{solutions.filter((s: any) => s.data_completeness === 'full').length}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm text-gray-600">Требуют дополнения</span>
                  <span className="font-semibold text-yellow-600">{solutions.filter((s: any) => s.data_completeness !== 'full').length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
