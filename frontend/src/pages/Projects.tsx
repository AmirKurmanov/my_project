import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getProjects, deleteProject } from '../api'
import toast from 'react-hot-toast'
import { Plus, FolderOpen, Trash2, Clock, Bot } from 'lucide-react'

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    getProjects().then((res) => setProjects(res.data)).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить проект?')) return
    try {
      await deleteProject(id)
      toast.success('Проект удалён')
      load()
    } catch { toast.error('Ошибка удаления') }
  }

  const statusLabels: any = {
    draft: { label: 'Черновик', color: 'bg-yellow-100 text-yellow-800' },
    calculated: { label: 'Рассчитан', color: 'bg-green-100 text-green-800' },
    completed: { label: 'Завершён', color: 'bg-blue-100 text-blue-800' },
  }

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Мои проекты</h1>
          <p className="text-gray-500 mt-1">Управляйте проектами роботизации</p>
        </div>
        <Link to="/projects/new" className="bg-primary-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center">
          <Plus className="h-5 w-5 mr-2" /> Новый проект
        </Link>
      </div>

      {projects.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center shadow-sm border">
          <FolderOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Нет проектов</h2>
          <p className="text-gray-500 mb-6">Создайте первый проект для подбора роботизированных решений</p>
          <Link to="/projects/new" className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700">
            Создать проект
          </Link>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((p) => {
            const status = statusLabels[p.status] || statusLabels.draft
            return (
              <div key={p.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden card-hover">
                <Link to={`/projects/${p.id}`} className="block p-6">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-gray-900 line-clamp-2">{p.name}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${status.color} whitespace-nowrap ml-2`}>
                      {status.label}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mb-3">
                    {p.object_type?.name || '—'}
                  </p>
                  <div className="flex items-center text-xs text-gray-400">
                    <Clock className="h-3.5 w-3.5 mr-1" />
                    {new Date(p.updated_at || p.created_at).toLocaleDateString('ru-RU')}
                    <span className="mx-2">•</span>
                    <Bot className="h-3.5 w-3.5 mr-1" />
                    {p.scenarios?.length || 0} сценариев
                  </div>
                </Link>
                <div className="border-t px-6 py-2 flex justify-end">
                  <button onClick={() => handleDelete(p.id)} className="text-red-400 hover:text-red-600 p-1">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
