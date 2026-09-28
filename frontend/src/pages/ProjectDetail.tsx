import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { getProject, createScenario, calculateScenario, compareScenarios, getSolutions, exportPDF, exportExcel, getSimulation, deleteScenario } from '../api'
import toast from 'react-hot-toast'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend
} from 'chart.js'
import { Bar, Line } from 'react-chartjs-2'
import { Calculator, BarChart3, Eye, Download, Plus, Play, Pause, RotateCcw, Settings, Trash2, HelpCircle } from 'lucide-react'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend)

const fmt = (v: any) => {
  if (v === null || v === undefined || v === '—') return '—'
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(v)
}

export default function ProjectDetail() {
  const { id } = useParams()
  const [project, setProject] = useState<any>(null)
  const [tab, setTab] = useState('scenarios')
  const [solutions, setSolutions] = useState<any[]>([])
  const [comparison, setComparison] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [calcLoading, setCalcLoading] = useState<number | null>(null)

  // Scenario creation
  const [showNewScenario, setShowNewScenario] = useState(false)
  const [newScenario, setNewScenario] = useState({ name: '', scenario_type: 'purchase', robot_solution_id: '' })

  // Visualization
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [simData, setSimData] = useState<any>(null)
  const [simFrame, setSimFrame] = useState(0)
  const [simPlaying, setSimPlaying] = useState(false)
  const [simSpeed, setSimSpeed] = useState(1)
  const animRef = useRef<number>(0)

  const load = () => {
    if (!id) return
    setLoading(true)
    getProject(Number(id)).then(res => setProject(res.data)).catch(() => {}).finally(() => setLoading(false))
    getSolutions({}).then(res => setSolutions(res.data)).catch(() => {})
  }

  useEffect(load, [id])

  const handleCalculate = async (scenarioId: number) => {
    setCalcLoading(scenarioId)
    try {
      await calculateScenario(scenarioId)
      toast.success('Расчёт выполнен')
      load()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Ошибка расчёта')
    } finally { setCalcLoading(null) }
  }

  const handleCreateScenario = async () => {
    if (!newScenario.name) { toast.error('Введите название'); return }
    try {
      await createScenario(Number(id), {
        ...newScenario,
        robot_solution_id: newScenario.robot_solution_id ? Number(newScenario.robot_solution_id) : null,
      })
      toast.success('Сценарий создан')
      setShowNewScenario(false)
      setNewScenario({ name: '', scenario_type: 'purchase', robot_solution_id: '' })
      load()
    } catch { toast.error('Ошибка создания') }
  }

  const handleDeleteScenario = async (scenarioId: number) => { if (!window.confirm('Удалить сценарий?')) return; try { await deleteScenario(scenarioId); toast.success('Сценарий удален'); load(); } catch { toast.error('Ошибка удаления') } }

  const loadComparison = async () => {
    try {
      const res = await compareScenarios(Number(id))
      setComparison(res.data)
    } catch {}
  }

  useEffect(() => { if (tab === 'comparison') loadComparison() }, [tab])

  // Visualization
  const loadSimulation = async () => {
    try {
      const res = await getSimulation(Number(id))
      setSimData(res.data)
      setSimFrame(0)
    } catch { toast.error('Ошибка загрузки симуляции') }
  }

  useEffect(() => { if (tab === 'visualization') loadSimulation() }, [tab])

  const drawFrame = useCallback(() => {
    if (!canvasRef.current || !simData) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return
    const W = canvasRef.current.width
    const H = canvasRef.current.height

    ctx.clearRect(0, 0, W, H)
    ctx.fillStyle = '#f1f5f9'
    ctx.fillRect(0, 0, W, H)

    // Draw zones
    simData.layout.zones.forEach((z: any) => {
      ctx.fillStyle = z.color + '30'
      ctx.strokeStyle = z.color
      ctx.lineWidth = 2
      ctx.fillRect(z.x * W, z.y * H, z.w * W, z.h * H)
      ctx.strokeRect(z.x * W, z.y * H, z.w * W, z.h * H)
      ctx.fillStyle = '#334155'
      ctx.font = '11px Inter, sans-serif'
      ctx.fillText(z.name, z.x * W + 5, z.y * H + 15)
    })

    // Draw paths
    ctx.strokeStyle = '#94a3b8'
    ctx.lineWidth = 1
    ctx.setLineDash([5, 5])
    simData.layout.paths.forEach((p: any) => {
      if (p.waypoints?.length >= 2) {
        ctx.beginPath()
        ctx.moveTo(p.waypoints[0][0] * W, p.waypoints[0][1] * H)
        for (let i = 1; i < p.waypoints.length; i++) {
          ctx.lineTo(p.waypoints[i][0] * W, p.waypoints[i][1] * H)
        }
        ctx.stroke()
      }
    })
    ctx.setLineDash([])

    // Draw robots
    const frame = simData.frames[simFrame] || simData.frames[0]
    if (frame) {
      frame.robots.forEach((r: any) => {
        const colors: any = { moving: '#3b82f6', working: '#22c55e', idle: '#f59e0b' }
        ctx.fillStyle = colors[r.state] || '#6366f1'
        ctx.beginPath()
        ctx.arc(r.x * W, r.y * H, 8, 0, Math.PI * 2)
        ctx.fill()
        ctx.fillStyle = 'white'
        ctx.font = 'bold 8px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(`R${r.id + 1}`, r.x * W, r.y * H + 3)
        ctx.textAlign = 'start'
      })
    }
  }, [simData, simFrame])

  useEffect(() => { drawFrame() }, [drawFrame])

  useEffect(() => {
    if (simPlaying && simData) {
      const interval = setInterval(() => {
        setSimFrame(f => {
          if (f >= simData.frames.length - 1) { setSimPlaying(false); return 0 }
          return f + 1
        })
      }, 100 / simSpeed)
      return () => clearInterval(interval)
    }
  }, [simPlaying, simSpeed, simData])

  const handleExport = async (type: 'pdf' | 'excel') => {
    try {
      const res = type === 'pdf' ? await exportPDF(Number(id)) : await exportExcel(Number(id))
      const blob = new Blob([res.data])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `robopodbor_project_${id}.${type === 'pdf' ? 'pdf' : 'xlsx'}`
      a.click()
      toast.success('Файл скачан')
    } catch { toast.error('Ошибка экспорта') }
  }

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>
  if (!project) return <div className="text-center py-20 text-gray-500">Проект не найден</div>

  const tabs = [
    { id: 'scenarios', label: 'Сценарии', icon: Calculator },
    { id: 'comparison', label: 'Сравнение', icon: BarChart3 },
    { id: 'visualization', label: 'Визуализация', icon: Eye },
    { id: 'export', label: 'Экспорт', icon: Download },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
        <p className="text-gray-500">{project.object_type?.name} • {new Date(project.created_at).toLocaleDateString('ru-RU')}</p>
      </div>

      {/* Tabs */}
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

      {/* Scenarios Tab */}
      {tab === 'scenarios' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Сценарии проекта</h2>
            <button onClick={() => setShowNewScenario(true)} className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 flex items-center">
              <Plus className="h-4 w-4 mr-1" /> Добавить сценарий
            </button>
          </div>

          {showNewScenario && (
            <div className="bg-blue-50 rounded-xl p-5 mb-6 border border-blue-200">
              <h3 className="font-semibold mb-3">Новый сценарий</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Название</label>
                  <input
                    value={newScenario.name}
                    onChange={e => setNewScenario({ ...newScenario, name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="Покупка AMR"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Тип</label>
                  <select
                    value={newScenario.scenario_type}
                    onChange={e => setNewScenario({ ...newScenario, scenario_type: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="purchase">Покупка</option>
                    <option value="raas">Аренда (RaaS)</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Робот</label>
                  <select
                    value={newScenario.robot_solution_id}
                    onChange={e => setNewScenario({ ...newScenario, robot_solution_id: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">Выберите робота</option>
                    {solutions.map((s: any) => (
                      <option key={s.id} value={s.id}>{s.name} ({s.manufacturer})</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex gap-3 mt-4">
                <button onClick={handleCreateScenario} className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm">Создать</button>
                <button onClick={() => setShowNewScenario(false)} className="text-gray-500 text-sm">Отмена</button>
              </div>
            </div>
          )}

          <div className="space-y-4">
            {project.scenarios?.map((s: any) => (
              <div key={s.id} className="bg-white rounded-xl p-5 shadow-sm border">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{s.name}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      s.scenario_type === 'baseline' ? 'bg-gray-100 text-gray-600' :
                      s.scenario_type === 'purchase' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                    }`}>
                      {s.scenario_type === 'baseline' ? 'Базовый' : s.scenario_type === 'purchase' ? 'Покупка' : 'RaaS'}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    {s.scenario_type !== 'baseline' && (
                      <button onClick={() => handleDeleteScenario(s.id)} className="text-red-500 hover:text-red-700 px-2 py-1.5 rounded-lg border border-red-200"><Trash2 className="h-4 w-4" /></button>
                    )}
                    {s.scenario_type !== 'baseline' && (
                      <button onClick={() => handleCalculate(s.id)} disabled={calcLoading === s.id} className="bg-green-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-green-700 flex items-center disabled:opacity-50">
                        <Calculator className='h-4 w-4 mr-1' />{calcLoading === s.id ? 'Расчёт...' : 'Рассчитать'}
                      </button>
                    )}
                  </div>
                </div>
                {s.results && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t">
                    <div>
                      <div className="flex items-center space-x-1 relative group cursor-help w-max">
                        <div className="text-xs text-gray-500">Роботов</div>
                        <HelpCircle className="w-3.5 h-3.5 text-gray-400" />
                        <div className="absolute bottom-full mb-2 -left-2 w-64 bg-gray-900 text-white text-xs rounded py-1.5 px-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                          Расчетный размер парка роботов, необходимый для 100% покрытия пиковой нагрузки вашего объекта с учетом времени на их зарядку.
                          <div className="absolute top-full left-4 -mt-1 w-2 h-2 bg-gray-900 rotate-45"></div>
                        </div>
                      </div>
                      <div className="text-lg font-bold text-gray-900">{s.results.robot_count}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">CAPEX</div>
                      <div className="text-lg font-bold text-gray-900">{fmt(s.results.capex_total)} ₽</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">OPEX/год</div>
                      <div className="text-lg font-bold text-gray-900">{fmt(s.results.opex_annual)} ₽</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Окупаемость</div>
                      <div className="text-lg font-bold text-green-600">
                        {s.results.payback_years ? `${s.results.payback_years} лет` : '—'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comparison Tab */}
      {tab === 'comparison' && comparison && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Сравнение сценариев</h2>

          {/* Table */}
          <div className="bg-white rounded-xl shadow-sm border overflow-x-auto mb-8">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-primary-800 text-white">
                  <th className="px-4 py-3 text-left">Показатель</th>
                  {comparison.scenarios.map((s: any) => (
                    <th key={s.id} className="px-4 py-3 text-right">{s.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { label: 'Тип', key: 'type', unit: '', hint: '', transform: (v: string) => v === 'baseline' ? 'Базовый' : v === 'purchase' ? 'Покупка' : 'RaaS' },
                  { label: 'Кол-во роботов', key: 'robot_count', unit: 'шт.', hint: '' },
                  { label: 'CAPEX', key: 'capex_total', format: true, unit: '₽', hint: 'начальные вложения' },
                  { label: 'OPEX / год', key: 'opex_annual', format: true, unit: '₽', hint: 'ежегодные расходы' },
                  { label: 'Годовой эффект', key: 'annual_effect', format: true, unit: '₽', hint: 'экономия в год' },
                  { label: 'Срок окупаемости', key: 'payback_years', unit: 'лет', hint: 'когда вернутся вложения' },
                  { label: 'ROI', key: 'roi_pct', unit: '%', hint: 'рентабельность инвестиций' },
                  { label: 'TCO за 5 лет', key: 'tco_5years', format: true, unit: '₽', hint: 'полная стоимость владения' },
                ].map(row => (
                  <tr key={row.label} className="border-t">
                    <td className="px-4 py-2.5 font-medium text-gray-700">
                      {row.label}{row.unit && <span className="text-gray-400 font-normal">, {row.unit}</span>}
                      {row.hint && (
                        <span className="block text-[11px] font-normal text-gray-400">{row.hint}</span>
                      )}
                    </td>
                    {comparison.scenarios.map((s: any) => {
                      let val = row.key === 'type' ? s.type : s.results?.[row.key]
                      if (row.transform) val = row.transform(val)
                      else if (row.format) val = val != null && val !== '—' ? fmt(val) + ' ₽' : '—'
                      else val = val ?? '—'
                      return <td key={s.id} className="px-4 py-2.5 text-right">{val}</td>
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Charts */}
          {comparison.scenarios.some((s: any) => s.results) && (
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl p-5 shadow-sm border">
                <h3 className="font-semibold mb-4">CAPEX и OPEX по сценариям</h3>
                <Bar data={{
                  labels: comparison.scenarios.map((s: any) => s.name.substring(0, 20)),
                  datasets: [
                    {
                      label: 'CAPEX',
                      data: comparison.scenarios.map((s: any) => s.results?.capex_total || 0),
                      backgroundColor: '#3b82f6',
                    },
                    {
                      label: 'OPEX/год',
                      data: comparison.scenarios.map((s: any) => s.results?.opex_annual || 0),
                      backgroundColor: '#8b5cf6',
                    },
                  ],
                }} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
              </div>
              <div className="bg-white rounded-xl p-5 shadow-sm border">
                <h3 className="font-semibold mb-4">TCO по годам</h3>
                <Line data={{
                  labels: ['Год 1', 'Год 2', 'Год 3', 'Год 4', 'Год 5'],
                  datasets: comparison.scenarios.filter((s: any) => s.results?.tco_yearly).map((s: any, i: number) => ({
                    label: s.name.substring(0, 20),
                    data: s.results.tco_yearly,
                    borderColor: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444'][i % 4],
                    backgroundColor: ['#3b82f620', '#22c55e20', '#f59e0b20', '#ef444420'][i % 4],
                    fill: true,
                  })),
                }} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
              </div>
            </div>
          )}

          {/* Assumptions */}
          {comparison.scenarios.some((s: any) => s.results?.assumptions) && (
            <div className="bg-yellow-50 rounded-xl p-5 mt-6 border border-yellow-200">
              <h3 className="font-semibold text-yellow-800 mb-2">Допущения и формулы</h3>
              {comparison.scenarios.filter((s: any) => s.results?.assumptions).map((s: any) => (
                <div key={s.id} className="mb-3">
                  <p className="text-sm font-medium text-yellow-700">{s.name}:</p>
                  <ul className="text-xs text-yellow-600 ml-4 list-disc">
                    {s.results.assumptions.map((a: string, i: number) => <li key={i}>{a}</li>)}
                  </ul>
                  {s.results.formulas && (
                    <div className="mt-1">
                      {s.results.formulas.map((f: string, i: number) => (
                        <code key={i} className="block text-xs text-gray-600 bg-white px-2 py-1 rounded mt-1">{f}</code>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Visualization Tab */}
      {tab === 'visualization' && (
        <div>
          <h2 className="text-lg font-semibold mb-4">2D-визуализация работы роботов</h2>
          <div className="grid lg:grid-cols-4 gap-6">
            <div className="lg:col-span-3">
              <div className="bg-white rounded-xl shadow-sm border p-4">
                <canvas ref={canvasRef} width={900} height={500} className="w-full rounded-lg border" />
                <div className="flex items-center justify-between mt-4">
                  <div className="flex gap-2">
                    <button onClick={() => { setSimPlaying(!simPlaying) }} className="bg-primary-600 text-white px-4 py-2 rounded-lg flex items-center text-sm">
                      {simPlaying ? <Pause className="h-4 w-4 mr-1" /> : <Play className="h-4 w-4 mr-1" />}
                      {simPlaying ? 'Пауза' : 'Запуск'}
                    </button>
                    <button onClick={() => { setSimFrame(0); setSimPlaying(false) }} className="border px-3 py-2 rounded-lg text-sm">
                      <RotateCcw className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>Скорость:</span>
                    <input type="range" min={0.5} max={5} step={0.5} value={simSpeed} onChange={e => setSimSpeed(Number(e.target.value))} className="w-24" />
                    <span>×{simSpeed}</span>
                  </div>
                  <div className="text-xs text-gray-400 w-32 text-right tabular-nums">
                    Кадр: {simFrame + 1} / {simData?.total_steps || 0}
                  </div>
                </div>
                {/* Legend */}
                <div className="flex gap-4 mt-3 text-xs text-gray-500">
                  <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-blue-500 mr-1"></span> Движение</span>
                  <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-green-500 mr-1"></span> Работа</span>
                  <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-yellow-500 mr-1"></span> Ожидание</span>
                </div>
              </div>
            </div>
            <div>
              <div className="bg-white rounded-xl shadow-sm border p-4">
                <h3 className="font-semibold mb-3">KPI</h3>
                {simData?.kpis && (
                  <div className="space-y-3">
                    <div><span className="text-xs text-gray-500 block">Операций выполнено</span><span className="text-xl font-bold">{simData.kpis.throughput}</span></div>
                    <div><span className="text-xs text-gray-500 block">Загрузка</span><span className="text-xl font-bold text-green-600">{simData.kpis.utilization_pct}%</span></div>
                    <div><span className="text-xs text-gray-500 block">Простой</span><span className="text-xl font-bold text-yellow-600">{simData.kpis.idle_time_pct}%</span></div>
                    <div><span className="text-xs text-gray-500 block">Операций на робота</span><span className="text-xl font-bold">{simData.kpis.operations_per_robot}</span></div>
                    <div><span className="text-xs text-gray-500 block">Узкое место</span><span className="text-sm font-medium text-red-600">{simData.kpis.bottleneck_zone}</span></div>
                  </div>
                )}
              </div>
              <div className="bg-white rounded-xl shadow-sm border p-4 mt-4">
                <h3 className="font-semibold mb-2 text-sm">Сценарий</h3>
                <p className="text-sm text-gray-600">{simData?.scenario_name || '—'}</p>
                <div className="flex items-center space-x-1 mt-1 group relative cursor-help w-max">
                  <p className="text-sm text-gray-500">Роботов: {simData?.robot_count || 0}</p>
                  <HelpCircle className="w-3.5 h-3.5 text-gray-400" />
                  <div className="absolute bottom-full mb-2 -left-2 w-64 bg-gray-900 text-white text-xs rounded py-1.5 px-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                    Расчетный размер парка роботов, необходимый для 100% покрытия пиковой нагрузки вашего объекта с учетом времени на их зарядку.
                    <div className="absolute top-full left-4 -mt-1 w-2 h-2 bg-gray-900 rotate-45"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Export Tab */}
      {tab === 'export' && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Экспорт результатов</h2>
          <div className="grid md:grid-cols-2 gap-6 max-w-2xl">
            <button
              onClick={() => handleExport('pdf')}
              className="bg-white rounded-xl p-6 shadow-sm border hover:border-primary-300 transition-colors text-left"
            >
              <Download className="h-10 w-10 text-red-500 mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Скачать PDF</h3>
              <p className="text-sm text-gray-500">Полный отчёт с параметрами, сценариями и расчётами</p>
            </button>
            <button
              onClick={() => handleExport('excel')}
              className="bg-white rounded-xl p-6 shadow-sm border hover:border-primary-300 transition-colors text-left"
            >
              <Download className="h-10 w-10 text-green-500 mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Скачать Excel</h3>
              <p className="text-sm text-gray-500">Таблицы с данными для дальнейшего анализа</p>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
