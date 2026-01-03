/**
 * 侧边栏导航组件
 */

import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  CreditCard,
  ArrowUpDown,
  TrendingUp,
  FileText,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Brain,
  User,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

const navigationItems = [
  {
    id: 'dashboard',
    label: '仪表板',
    icon: LayoutDashboard,
    path: '/dashboard',
  },
  {
    id: 'accounts',
    label: '账户管理',
    icon: CreditCard,
    path: '/accounts',
  },
  {
    id: 'transactions',
    label: '交易记录',
    icon: ArrowUpDown,
    path: '/transactions',
  },
  {
    id: 'investments',
    label: '投资理财',
    icon: TrendingUp,
    path: '/investments',
  },
  {
    id: 'loans',
    label: '贷款服务',
    icon: FileText,
    path: '/loans',
  },
  {
    id: 'chat',
    label: '智能客服',
    icon: MessageSquare,
    path: '/chat',
  },
];

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  return (
    <motion.aside
      className={`bg-gray-900 border-r border-gray-800 transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
      initial={{ x: -100 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex flex-col h-full">
        {/* Logo区域 */}
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <AnimatePresence>
              {!isCollapsed && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                >
                  <h1 className="text-xl font-bold text-white">银行AI</h1>
                  <p className="text-sm text-gray-400">智能助手</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* 导航菜单 */}
        <nav className="flex-1 p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.id}
                to={item.path}
                className={`flex items-center space-x-3 px-3 py-3 rounded-lg transition-all duration-200 group ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'}`} />
                <AnimatePresence>
                  {!isCollapsed && (
                    <motion.span
                      className="font-medium"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      transition={{ duration: 0.2 }}
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
                
                {/* 激活状态指示器 */}
                {isActive && (
                  <motion.div
                    className="absolute right-2 w-2 h-2 bg-white rounded-full"
                    layoutId="activeIndicator"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* 用户信息和控制 */}
        <div className="p-4 border-t border-gray-800">
          {/* 用户信息 */}
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <AnimatePresence>
              {!isCollapsed && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                  className="flex-1 min-w-0"
                >
                  <p className="text-sm font-medium text-white truncate">
                    {user?.full_name || user?.username}
                  </p>
                  <p className="text-xs text-gray-400 truncate">
                    {user?.email}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* 控制按钮 */}
          <div className="space-y-2">
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="w-full flex items-center justify-center px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              {isCollapsed ? (
                <ChevronRight className="w-5 h-5" />
              ) : (
                <>
                  <ChevronLeft className="w-5 h-5 mr-2" />
                  <span className="text-sm">收起</span>
                </>
              )}
            </button>
            
            <button
              onClick={logout}
              className="w-full flex items-center justify-center px-3 py-2 text-red-400 hover:text-white hover:bg-red-900/20 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              {!isCollapsed && <span className="text-sm ml-2">退出</span>}
            </button>
          </div>
        </div>
      </div>
    </motion.aside>
  );
}