/**
 * 投资理财页面
 */

import { motion } from 'framer-motion';
import { TrendingUp, PieChart, DollarSign } from 'lucide-react';

export default function Investments() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">投资理财</h1>
        <p className="text-gray-400">发现投资机会，管理您的投资组合</p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="text-center py-12">
          <TrendingUp className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-2">投资理财功能开发中</h3>
          <p className="text-gray-500">即将为您带来专业的投资理财服务</p>
        </div>
      </motion.div>
    </div>
  );
}