import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Bot, Menu, X, LogOut, User, Settings } from 'lucide-react'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isAdmin, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-white shadow-sm sticky top-0 z-50 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <Bot className="h-8 w-8 text-primary-600" />
                <span className="text-xl font-bold text-primary-800">RoboMatch</span>
              </Link>
              <div className="hidden md:flex ml-10 space-x-8">
                <Link to="/catalog" className="text-gray-600 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors">
                  Каталог
                </Link>
                {isAuthenticated && (
                  <Link to="/projects" className="text-gray-600 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors">
                    Мои проекты
                  </Link>
                )}
                {isAdmin && (
                  <Link to="/admin" className="text-gray-600 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors">
                    Админ
                  </Link>
                )}
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-4">
              {isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <User className="h-4 w-4 mr-1" />
                    {user?.full_name}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center text-sm text-gray-500 hover:text-red-600 transition-colors"
                  >
                    <LogOut className="h-4 w-4 mr-1" />
                    Выйти
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <Link to="/login" className="text-sm text-gray-600 hover:text-primary-600 font-medium">
                    Войти
                  </Link>
                  <Link to="/register" className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                    Регистрация
                  </Link>
                </div>
              )}
            </div>
            <div className="md:hidden flex items-center">
              <button onClick={() => setMenuOpen(!menuOpen)}>
                {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>
        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-4 py-3 space-y-2">
              <Link to="/catalog" onClick={() => setMenuOpen(false)} className="block py-2 text-gray-600">Каталог</Link>
              {isAuthenticated && <Link to="/projects" onClick={() => setMenuOpen(false)} className="block py-2 text-gray-600">Мои проекты</Link>}
              {isAdmin && <Link to="/admin" onClick={() => setMenuOpen(false)} className="block py-2 text-gray-600">Админ</Link>}
              {isAuthenticated ? (
                <button onClick={() => { handleLogout(); setMenuOpen(false); }} className="block py-2 text-red-600">Выйти</button>
              ) : (
                <>
                  <Link to="/login" onClick={() => setMenuOpen(false)} className="block py-2 text-gray-600">Войти</Link>
                  <Link to="/register" onClick={() => setMenuOpen(false)} className="block py-2 text-primary-600">Регистрация</Link>
                </>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="bg-primary-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Bot className="h-6 w-6" />
              <span className="font-bold">RoboMatch</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
