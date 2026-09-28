import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { getObjectTypes, getDemoData, matchSolutions, createProject } from '../api'
import toast from 'react-hot-toast'
import { Warehouse, Plane, Building2, Bot, ChevronRight, ChevronLeft, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react'

const iconMap: any = { Warehouse, Plane, Hospital: Building2 }

export default function NewProject() {
  const navigate = useNavigate()
  const location = useLocation()
  const [step, setStep] = useState(1)
  const [objectTypes, setObjectTypes] = useState<any[]>([])
  const [selectedType, setSelectedType] = useState<any>(null)
  const [params, setParams] = useState<any>({})
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [selectedRobots, setSelectedRobots] = useState<number[]>([])
  const [projectName, setProjectName] = useState('')
  const [loadingRecs, setLoadingRecs] = useState(false)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    getObjectTypes().then((res) => {
      setObjectTypes(res.data)
      const preselect = (location.state as any)?.objectType
      if (preselect) {
        const found = res.data.find((o: any) => o.slug === preselect)
        if (found) { setSelectedType(found); setStep(2) }
      }
    })
  }, [])

  const handleSelectType = (obj: any) => {
    setSelectedType(obj)
    // Set defaults
    const defaults: any = {}
    obj.parameters_schema?.fields?.forEach((f: any) => {
      if (f.default !== undefined) defaults[f.name] = f.default
    })
    setParams(defaults)
    setStep(2)
  }

  const handleLoadDemo = async () => {
    if (!selectedType) return
    try {
      const res = await getDemoData(selectedType.slug)
      setParams(res.data.parameters)
      toast.success('Демо-данные загружены')
    } catch { toast.error('Ошибка загрузки демо-данных') }
  }

  const handleGetRecommendations = async () => {
    if (!selectedType) return
    setLoadingRecs(true)
    try {
      const res = await matchSolutions({ object_type_slug: selectedType.slug, parameters: params })
      setRecommendations(res.data.recommendations)
      setStep(3)
    } catch { toast.error('Ошибка получения рекомендаций') }
    finally { setLoadingRecs(false) }
  }

  const handleCreate = async () => {
    if (!projectName.trim()) { toast.error('Введите название проекта'); return }
    setCreating(true)
    try {
      const res = await createProject({
        name: projectName,
        object_type_id: selectedType.id,
        parameters: params,
      })
      toast.success('Проект создан!')
      navigate(`/projects/${res.data.id}`)
    } catch { toast.error('Ошибка создания проекта') }
    finally { setCreating(false) }
  }

  const toggleRobot = (id: number) => {
    setSelectedRobots(prev => prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id])
  }

  const renderField = (field: any) => {
    if (field.type === 'select') {
      return (
        <select
          value={params[field.name] || field.default || ''}
          onChange={(e) => setParams({ ...params, [field.name]: e.target.value })}
          className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
        >
          {field.options?.map((opt: string) => <option key={opt} value={opt}>{opt}</option>)}
        </select>
      )
    }
    return (
      <div className="relative">
        <input
          type="number"
          value={params[field.name] ?? ''}
          onChange={(e) => setParams({ ...params, [field.name]: e.target.value === '' ? '' : Number(e.target.value) })}
          min={field.min}
          max={field.max}
          className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none pr-16"
          placeholder={field.default?.toString()}
        />
        {field.unit && <span className="absolute right-3 top-2 text-xs text-gray-400">{field.unit}</span>}
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Steps indicator */}
      <div className="flex items-center justify-center mb-10 space-x-4">
        {[1, 2, 3, 4].map((s) => (
          <React.Fragment key={s}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm ${step >= s ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
              {step > s ? <CheckCircle2 className="h-5 w-5" /> : s}
            </div>
            {s < 4 && <div className={`w-16 h-0.5 ${step > s ? 'bg-primary-600' : 'bg-gray-200'}`} />}
          </React.Fragment>
        ))}
      </div>

      {/* Step 1: Select object type */}
      {step === 1 && (
        <div>
          <h1 className="text-2xl font-bold text-center mb-8">Выберите тип объекта</h1>
          <div className="grid md:grid-cols-3 gap-6">
            {objectTypes.map((obj) => {
              const Icon = iconMap[obj.icon] || Bot
              return (
                <button
                  key={obj.id}
                  onClick={() => handleSelectType(obj)}
                  className="bg-white border-2 border-gray-100 rounded-2xl p-8 text-left hover:border-primary-300 transition-all card-hover"
                >
                  <div className="bg-primary-50 rounded-xl p-4 w-16 h-16 flex items-center justify-center mb-4">
                    <Icon className="h-8 w-8 text-primary-600" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">{obj.name}</h3>
                  <p className="text-gray-500 text-sm">{obj.description}</p>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Step 2: Parameters */}
      {step === 2 && selectedType && (
        <div>
          <h1 className="text-2xl font-bold mb-2">Параметры объекта: {selectedType.name}</h1>
          <p className="text-gray-500 mb-6">Заполните характеристики вашего объекта или загрузите демо-данные</p>

          <div className="flex gap-3 mb-6">
            <button onClick={handleLoadDemo} className="bg-green-50 text-green-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-100 flex items-center">
              <Sparkles className="h-4 w-4 mr-2" /> Использовать демо-данные
            </button>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="grid md:grid-cols-2 gap-4">
              {selectedType.parameters_schema?.fields?.map((field: any) => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between mt-8">
            <button onClick={() => setStep(1)} className="flex items-center text-gray-500 hover:text-gray-700">
              <ChevronLeft className="h-5 w-5 mr-1" /> Назад
            </button>
            <button
              onClick={handleGetRecommendations}
              disabled={loadingRecs}
              className="bg-primary-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-primary-700 flex items-center disabled:opacity-50"
            >
              {loadingRecs ? 'Подбор...' : 'Подобрать решения'} <ChevronRight className="h-5 w-5 ml-1" />
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Recommendations */}
      {step === 3 && (
        <div>
          <h1 className="text-2xl font-bold mb-2">Рекомендованные решения</h1>
          <p className="text-gray-500 mb-6">Выберите решения для добавления в проект</p>

          <div className="space-y-4">
            {recommendations.filter(r => !r.excluded).map((rec: any) => (
              <div
                key={rec.solution.id}
                className={`bg-white rounded-xl p-5 shadow-sm border-2 cursor-pointer transition-all ${
                  selectedRobots.includes(rec.solution.id) ? 'border-primary-500 bg-primary-50/30' : 'border-gray-100 hover:border-gray-200'
                }`}
                onClick={() => toggleRobot(rec.solution.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900">{rec.solution.name}</h3>
                      <span className="bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full text-xs font-medium">
                        {rec.score}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">
                      {rec.solution.manufacturer} • {rec.solution.category?.name?.split('(')[0]?.trim()}
                    </p>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {rec.reasons.map((r: string, i: number) => (
                        <span key={i} className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded flex items-center">
                          <CheckCircle2 className="h-3 w-3 mr-1" /> {r}
                        </span>
                      ))}
                    </div>
                    {rec.warnings.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {rec.warnings.map((w: string, i: number) => (
                          <span key={i} className="text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded flex items-center">
                            <AlertTriangle className="h-3 w-3 mr-1" /> {w}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ml-4 ${
                    selectedRobots.includes(rec.solution.id) ? 'bg-primary-600 border-primary-600' : 'border-gray-300'
                  }`}>
                    {selectedRobots.includes(rec.solution.id) && <CheckCircle2 className="h-4 w-4 text-white" />}
                  </div>
                </div>
              </div>
            ))}

            {recommendations.filter(r => r.excluded).length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-400 mb-3">Не подходят:</h3>
                {recommendations.filter(r => r.excluded).map((rec: any) => (
                  <div key={rec.solution.id} className="bg-gray-50 rounded-lg p-4 mb-2 opacity-60">
                    <span className="font-medium text-gray-600">{rec.solution.name}</span>
                    <span className="text-xs text-red-500 ml-3">{rec.excluded_reasons?.join('; ')}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Sticky navigation bar — always visible at the bottom of the viewport */}
          <div className="sticky bottom-0 left-0 right-0 mt-6 -mx-4 px-4 py-4 bg-white/80 backdrop-blur-md border-t border-gray-200 shadow-[0_-4px_20px_rgba(0,0,0,0.08)] z-40">
            <div className="max-w-5xl mx-auto flex justify-between items-center">
              <button onClick={() => setStep(2)} className="flex items-center text-gray-500 hover:text-gray-700 transition-colors">
                <ChevronLeft className="h-5 w-5 mr-1" /> Назад
              </button>
              <div className="flex items-center gap-4">
                {selectedRobots.length > 0 && (
                  <span className="text-sm text-gray-500">
                    Выбрано: <span className="font-semibold text-primary-600">{selectedRobots.length}</span>
                  </span>
                )}
                <button onClick={() => setStep(4)} className="bg-primary-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-primary-700 flex items-center transition-colors shadow-lg shadow-primary-600/25">
                  Далее <ChevronRight className="h-5 w-5 ml-1" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Create */}
      {step === 4 && (
        <div>
          <h1 className="text-2xl font-bold mb-6">Создание проекта</h1>
          <div className="bg-white rounded-xl p-6 shadow-sm border max-w-lg">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Название проекта</label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary-500 outline-none"
                placeholder={`Проект: ${selectedType?.name}`}
              />
            </div>
            <div className="mb-4 text-sm text-gray-500">
              <p>Тип объекта: <strong>{selectedType?.name}</strong></p>
              <p>Выбрано решений: <strong>{selectedRobots.length}</strong></p>
            </div>
            <div className="flex justify-between mt-6">
              <button onClick={() => setStep(3)} className="flex items-center text-gray-500">
                <ChevronLeft className="h-5 w-5 mr-1" /> Назад
              </button>
              <button
                onClick={handleCreate}
                disabled={creating}
                className="bg-primary-600 text-white px-8 py-2.5 rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50"
              >
                {creating ? 'Создание...' : 'Создать проект'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
