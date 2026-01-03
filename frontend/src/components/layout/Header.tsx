/**
 * 顶部导航组件
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell, 
  Search, 
  Settings, 
  User, 
  Sun, 
  Moon,
  Activity,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export default function Header() {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const { user } = useAuth();

  // 模拟通知数据
  const notifications = [
    {
      id: 1,
      type: 'success',
      title: '转账完成',
      message: '您的转账1000元已成功到账',
      time: '5分钟前',
      icon: CheckCircle,
    },
    {
      id: 2,
      type: 'warning',
      title: '理财到期提醒',
      message: '您的理财产品即将到期，请及时处理',
      time: '1小时前',
      icon: AlertCircle,
    },
    {
      id: 3,
      type: 'info',
      title: '系统维护通知',
      message: '系统将于今晚23:00进行维护更新',
      time: '2小时前',
      icon: Activity,
    },
  ];

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'info':
      default:
        return 'text-blue-500';
    }
  };

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* 搜索栏 */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索功能、账户、交易..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>
        </div>

        {/* 右侧操作区 */}
        <div className="flex items-center space-x-4">
          {/* 主题切换 */}
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
          >
            {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>

          {/* 通知 */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <Bell className="w-5 h-5" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {notifications.length}
                </span>
              )}
            </button>

            {/* 通知下拉菜单 */}
            <AnimatePresence>
              {showNotifications && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setShowNotifications(false)}
                  />
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20"
                  >
                    <div className="p-4 border-b border-gray-700">
                      <h3 className="text-lg font-semibold text-white">通知</h3>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.map((notification) => {
                        const Icon = notification.icon;
                        return (
                          <div
                            key={notification.id}
                            className="p-4 border-b border-gray-700 hover:bg-gray-700 transition-colors cursor-pointer"
                          >
                            <div className="flex items-start space-x-3">
                              <Icon className={`w-5 h-5 mt-0.5 ${getNotificationIcon(notification.type)}`} />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-white">
                                  {notification.title}
                                </p>
                                <p className="text-sm text-gray-400 mt-1">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                  {notification.time}
                                </p>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    <div className="p-4 border-t border-gray-700">
                      <button className="w-full text-center text-sm text-blue-400 hover:text-blue-300 transition-colors">
                        查看所有通知
                      </button>
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>

          {/* 设置 */}
          <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
            <Settings className="w-5 h-5" />
          </button>

          {/* 用户菜单 */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center space-x-2 p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="text-left hidden sm:block">
                <p className="text-sm font-medium text-white">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-gray-400">在线</p>
              </div>
            </button>

            {/* 用户下拉菜单 */}
            <AnimatePresence>
              {showProfile && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setShowProfile(false)}
                  />
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20"
                  >
                    <div className="p-4 border-b border-gray-700">
                      <p className="text-sm font-medium text-white">
                        {user?.full_name || user?.username}
                      </p>
                      <p className="text-xs text-gray-400">
                        {user?.email}
                      </p>
                    </div>
                    <div className="py-2">
                      <button className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:text-white hover:bg-gray-700 transition-colors">
                        个人资料
                      </button>
                      <button className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:text-white hover:bg-gray-700 transition-colors">
                        账户设置
                      </button>
                      <button className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:text-white hover:bg-gray-700 transition-colors">
                        安全设置
                      </button>
                      <hr className="my-2 border-gray-700" />
                      <button className="w-full px-4 py-2 text-left text-sm text-red-400 hover:text-red-300 hover:bg-gray-700 transition-colors">
                        退出登录
                      </button>
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
}