/**
 * 贷款服务页面
 */

import { motion } from 'framer-motion';
import { FileText, Calculator, CreditCard } from 'lucide-react';

export default function Loans() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">贷款服务</h1>
        <p className="text-gray-400">申请贷款，实现您的梦想</p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-2">贷款服务功能开发中</h3>
          <p className="text-gray-500">即将为您带来便捷的贷款申请体验</p>
        </div>
      </motion.div>
    </div>
  );
}