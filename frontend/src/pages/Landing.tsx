import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Warehouse, Plane, Building2, ArrowRight, Bot, Calculator, BarChart3, Eye, Download, ChevronRight, Zap, Shield, TrendingUp } from 'lucide-react'
import { getObjectTypes } from '../api'

const iconMap: any = {
  Warehouse: Warehouse,
  Plane: Plane,
  Hospital: Building2,
}

const steps = [
  { num: 1, title: 'Выбор объекта', desc: 'Выберите тип объекта: склад, аэропорт или мед. учреждение' },
  { num: 2, title: 'Параметры', desc: 'Введите характеристики объекта или загрузите из файла' },
  { num: 3, title: 'Подбор решений', desc: 'Получите подборку подходящих роботизированных решений' },
  { num: 4, title: 'Сравнение', desc: 'Сопоставьте решения по характеристикам' },
  { num: 5, title: 'Расчёт экономики', desc: 'CAPEX, OPEX, ROI, срок окупаемости' },
  { num: 6, title: 'What-if анализ', desc: 'Сравните сценарии при разных параметрах' },
  { num: 7, title: 'Визуализация', desc: '2D-модель работы роботов на объекте' },
  { num: 8, title: 'Экспорт', desc: 'Сохраните отчёт в PDF или Excel' },
]

export default function Landing() {
  const [objectTypes, setObjectTypes] = useState<any[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    getObjectTypes().then((res) => setObjectTypes(res.data)).catch(() => {})
  }, [])

  return (
    <div>
      {/* Hero */}
      <section className="gradient-hero text-white py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex justify-center mb-6">
            <div className="bg-white/20 rounded-2xl p-4">
              <Bot className="h-16 w-16" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            Подберите роботизированное решение<br />для вашего бизнеса
          </h1>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Платформа для экспресс-оценки целесообразности роботизации. Подбор, сравнение, расчёт экономики и визуализация работы роботов на вашем объекте.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/projects/new"
              className="bg-white text-primary-800 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors inline-flex items-center justify-center"
            >
              Начать подбор <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link
              to="/catalog"
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-white/10 transition-colors inline-flex items-center justify-center"
            >
              Каталог решений
            </Link>
          </div>
        </div>
      </section>

      {/* Object Types */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900">Выберите тип объекта</h2>
          <p className="text-gray-500 text-center mb-12 max-w-2xl mx-auto">
            Платформа поддерживает три базовых типа объектов. Начните с выбора вашего сценария.
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            {objectTypes.map((obj) => {
              const Icon = iconMap[obj.icon] || Bot
              return (
                <div
                  key={obj.id}
                  onClick={() => navigate('/projects/new', { state: { objectType: obj.slug } })}
                  className="bg-white border-2 border-gray-100 rounded-2xl p-8 cursor-pointer card-hover hover:border-primary-300"
                >
                  <div className="bg-primary-50 rounded-xl p-4 w-16 h-16 flex items-center justify-center mb-6">
                    <Icon className="h-8 w-8 text-primary-600" />
                  </div>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{obj.name}</h3>
                  <p className="text-gray-500 mb-4">{obj.description}</p>
                  <span className="text-primary-600 font-medium inline-flex items-center">
                    Выбрать <ChevronRight className="h-4 w-4 ml-1" />
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">Как это работает</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step) => (
              <div key={step.num} className="bg-white rounded-xl p-6 shadow-sm">
                <div className="bg-primary-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold mb-4">
                  {step.num}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-sm text-gray-500">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-green-50 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">до 40%</div>
              <div className="text-gray-500">Снижение затрат на логистику</div>
            </div>
            <div className="text-center">
              <div className="bg-blue-50 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">от 2 лет</div>
              <div className="text-gray-500">Средний срок окупаемости</div>
            </div>
            <div className="text-center">
              <div className="bg-purple-50 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">15+</div>
              <div className="text-gray-500">Решений в каталоге</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 gradient-hero text-white">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Готовы оценить эффект роботизации?</h2>
          <p className="text-blue-100 mb-8 text-lg">
            Создайте проект и получите предварительную оценку за несколько минут.
            Результат является экспресс-оценкой и требует верификации при обследовании объекта.
          </p>
          <Link
            to="/projects/new"
            className="bg-white text-primary-800 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors inline-flex items-center"
          >
            Создать проект <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
