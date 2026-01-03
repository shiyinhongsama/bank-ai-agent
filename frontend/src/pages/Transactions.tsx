/**
 * 交易记录页面
 */

import { motion } from 'framer-motion';
import { ArrowUpDown, Download, Filter, Calendar } from 'lucide-react';

export default function Transactions() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">交易记录</h1>
        <p className="text-gray-400">查看您的所有交易历史记录</p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="text-center py-12">
          <ArrowUpDown className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-2">交易记录功能开发中</h3>
          <p className="text-gray-500">即将为您带来完整的交易记录查看体验</p>
        </div>
      </motion.div>
    </div>
  );
}