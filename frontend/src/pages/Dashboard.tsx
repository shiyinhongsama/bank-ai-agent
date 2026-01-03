/**
 * 仪表板页面
 */

import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  CreditCard,
  PiggyBank,
  Users,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';

// 模拟数据
const stats = [
  {
    title: '总资产',
    value: '¥125,000.50',
    change: '+2.5%',
    trend: 'up',
    icon: DollarSign,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
  },
  {
    title: '月度收益',
    value: '¥3,250.00',
    change: '+8.2%',
    trend: 'up',
    icon: TrendingUp,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    title: '投资回报',
    value: '15.8%',
    change: '+1.2%',
    trend: 'up',
    icon: PiggyBank,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
  {
    title: '贷款申请',
    value: '2',
    change: '0',
    trend: 'neutral',
    icon: CreditCard,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
  },
];

const recentTransactions = [
  {
    id: 1,
    type: '转账',
    description: '转账给张三',
    amount: -1000,
    date: '2024-12-01 14:30',
    status: 'completed',
  },
  {
    id: 2,
    type: '存款',
    description: 'ATM存款',
    amount: 5000,
    date: '2024-12-01 10:15',
    status: 'completed',
  },
  {
    id: 3,
    type: '投资',
    description: '理财产品收益',
    amount: 125.50,
    date: '2024-11-30 16:00',
    status: 'completed',
  },
  {
    id: 4,
    type: '支出',
    description: '消费支出',
    amount: -235.80,
    date: '2024-11-30 12:45',
    status: 'completed',
  },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">仪表板</h1>
        <p className="text-gray-400">欢迎回来，这里是您的金融概览</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          const isPositive = stat.trend === 'up';
          const isNeutral = stat.trend === 'neutral';

          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                {!isNeutral && (
                  <div className={`flex items-center space-x-1 ${
                    isPositive ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {isPositive ? (
                      <ArrowUpRight className="w-4 h-4" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4" />
                    )}
                    <span className="text-sm font-medium">{stat.change}</span>
                  </div>
                )}
              </div>
              <div>
                <h3 className="text-gray-400 text-sm font-medium mb-1">{stat.title}</h3>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 最近交易 */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="bg-gray-800 border border-gray-700 rounded-lg p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">最近交易</h2>
            <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">
              查看全部
            </button>
          </div>
          <div className="space-y-4">
            {recentTransactions.map((transaction) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    transaction.amount > 0 ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="text-white font-medium">{transaction.type}</p>
                    <p className="text-gray-400 text-sm">{transaction.description}</p>
                    <p className="text-gray-500 text-xs">{transaction.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${
                    transaction.amount > 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {transaction.amount > 0 ? '+' : ''}¥{Math.abs(transaction.amount).toFixed(2)}
                  </p>
                  <span className="text-xs text-gray-500 capitalize">{transaction.status}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* 快速操作 */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="bg-gray-800 border border-gray-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-semibold text-white mb-6">快速操作</h2>
          <div className="grid grid-cols-2 gap-4">
            <button className="flex flex-col items-center p-4 bg-blue-600/10 border border-blue-600/20 rounded-lg hover:bg-blue-600/20 transition-colors group">
              <CreditCard className="w-8 h-8 text-blue-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white font-medium">转账</span>
            </button>
            <button className="flex flex-col items-center p-4 bg-green-600/10 border border-green-600/20 rounded-lg hover:bg-green-600/20 transition-colors group">
              <PiggyBank className="w-8 h-8 text-green-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white font-medium">理财</span>
            </button>
            <button className="flex flex-col items-center p-4 bg-purple-600/10 border border-purple-600/20 rounded-lg hover:bg-purple-600/20 transition-colors group">
              <TrendingUp className="w-8 h-8 text-purple-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white font-medium">投资</span>
            </button>
            <button className="flex flex-col items-center p-4 bg-yellow-600/10 border border-yellow-600/20 rounded-lg hover:bg-yellow-600/20 transition-colors group">
              <Users className="w-8 h-8 text-yellow-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white font-medium">客服</span>
            </button>
          </div>
        </motion.div>
      </div>

      {/* 智能助手推荐 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 border border-blue-600/20 rounded-lg p-6"
      >
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-lg">AI</span>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-1">智能助手建议</h3>
            <p className="text-gray-300 text-sm">
              基于您的消费习惯，我们推荐您考虑增加定期储蓄，为未来投资机会做准备。
            </p>
          </div>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
            了解更多
          </button>
        </div>
      </motion.div>
    </div>
  );
}