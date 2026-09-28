import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getSolutions, getCategories } from '../api'
import { Search, Filter, Bot, Weight, Zap, DollarSign } from 'lucide-react'

export default function Catalog() {
  const [solutions, setSolutions] = useState<any[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<number | null>(null)
  const [sortBy, setSortBy] = useState('name')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getCategories().then((res) => setCategories(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    getSolutions({ search: search || undefined, category_id: categoryFilter || undefined, sort_by: sortBy })
      .then((res) => setSolutions(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [search, categoryFilter, sortBy])

  const formatPrice = (price: number) => {
    if (!price) return '—'
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽'
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Каталог роботизированных решений</h1>
      <p className="text-gray-500 mb-8">Просмотрите и сравните доступные решения для вашего объекта</p>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar */}
        <div className="lg:w-64 flex-shrink-0">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 sticky top-24">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <Filter className="h-4 w-4 mr-2" /> Фильтры
            </h3>
            <div className="mb-4">
              <label className="text-sm font-medium text-gray-600 mb-2 block">Поиск</label>
              <div className="relative">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Название, производитель..."
                  className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
            </div>
            <div className="mb-4">
              <label className="text-sm font-medium text-gray-600 mb-2 block">Категория</label>
              <select
                value={categoryFilter || ''}
                onChange={(e) => setCategoryFilter(e.target.value ? Number(e.target.value) : null)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
              >
                <option value="">Все категории</option>
                {categories.map((c: any) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600 mb-2 block">Сортировка</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
              >
                <option value="name">По названию</option>
                <option value="price">По цене</option>
                <option value="payload">По грузоподъёмности</option>
              </select>
            </div>
          </div>
        </div>

        {/* Grid */}
        <div className="flex-1">
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : solutions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">Решения не найдены</div>
          ) : (
            <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-6">
              {solutions.map((sol: any) => (
                <Link
                  key={sol.id}
                  to={`/catalog/${sol.id}`}
                  className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden card-hover"
                >
                  <div className="h-40 bg-gradient-to-br from-primary-500 to-indigo-600 flex items-center justify-center">
                    <Bot className="h-16 w-16 text-white/80" />
                  </div>
                  <div className="p-5">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{sol.name}</h3>
                      <span className="text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded-full whitespace-nowrap ml-2">
                        {sol.category?.name?.split('(')[0]?.trim() || 'Робот'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">{sol.manufacturer} • {sol.country || '—'}</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center text-gray-600">
                        <Weight className="h-3.5 w-3.5 mr-1 text-gray-400" />
                        {sol.payload_capacity_kg ? `${sol.payload_capacity_kg} кг` : '—'}
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Zap className="h-3.5 w-3.5 mr-1 text-gray-400" />
                        {sol.max_speed_ms ? `${sol.max_speed_ms} м/с` : '—'}
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t flex justify-between items-center">
                      <span className="font-semibold text-primary-700 text-sm">
                        {formatPrice(sol.equipment_cost_rub)}
                      </span>
                      <span className="text-xs text-primary-600 font-medium">Подробнее →</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
