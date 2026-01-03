/**
 * 认证布局组件
 */

import { motion } from 'framer-motion';

interface AuthLayoutProps {
  children: React.ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-950 flex">
      {/* 左侧装饰区域 */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="absolute inset-0">
          {/* 动画背景装饰 */}
          <motion.div
            className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute bottom-32 right-32 w-48 h-48 bg-white/5 rounded-full"
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 6,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/5 rounded-full"
            animate={{
              scale: [1, 1.3, 1],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </div>
        
        <div className="relative z-10 flex flex-col justify-center px-12">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h1 className="text-5xl font-bold text-white mb-6">
              银行AI智能体
            </h1>
            <p className="text-xl text-blue-100 mb-8 leading-relaxed">
              体验下一代银行服务，让AI为您的金融服务提供智能支持。
              从账户管理到投资理财，我们为您提供全方位的智能解决方案。
            </p>
            <div className="space-y-4">
              <motion.div
                className="flex items-center space-x-3"
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
              >
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-blue-100">智能客服24/7在线服务</span>
              </motion.div>
              <motion.div
                className="flex items-center space-x-3"
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.8 }}
              >
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-blue-100">个性化理财建议</span>
              </motion.div>
              <motion.div
                className="flex items-center space-x-3"
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 1.0 }}
              >
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-blue-100">实时账户监控</span>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* 右侧表单区域 */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          className="w-full max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {children}
        </motion.div>
      </div>
    </div>
  );
}