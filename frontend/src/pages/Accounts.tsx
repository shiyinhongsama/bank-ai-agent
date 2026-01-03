/**
 * 账户管理页面
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  CreditCard, 
  Eye, 
  EyeOff, 
  ArrowUpDown, 
  Download,
  RefreshCw,
  Calendar,
  DollarSign,
} from 'lucide-react';
import { accountApi } from '../services/api';
import { Account, Transaction } from '../types';
import toast from 'react-hot-toast';

// 模拟账户数据
const mockAccounts: Account[] = [
  {
    id: 1,
    account_number: '6226090000000123',
    account_type: 'savings',
    currency: 'CNY',
    balance: 125000.50,
    available_balance: 120000.50,
    status: 'active',
    opened_date: '2024-01-15T10:30:00',
    last_transaction_date: '2024-12-01T14:20:00',
  },
];

const mockTransactions: Transaction[] = [
  {
    id: 1,
    transaction_number: 'TXN202412010001',
    transaction_type: 'deposit',
    amount: 1000.0,
    currency: 'CNY',
    balance_after: 125000.50,
    status: 'completed',
    description: 'ATM存款',
    created_at: '2024-12-01T14:20:00',
  },
];

export default function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [showBalance, setShowBalance] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      
      // 模拟API调用
      setTimeout(() => {
        setAccounts(mockAccounts);
        setTransactions(mockTransactions);
        setSelectedAccount(mockAccounts[0]);
        setIsLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('加载数据失败:', error);
      toast.error('加载数据失败');
      setIsLoading(false);
    }
  };

  const formatBalance = (balance: number) => {
    return showBalance ? `¥${balance.toLocaleString()}` : '¥****';
  };

  const getAccountTypeName = (type: string) => {
    const types: Record<string, string> = {
      savings: '储蓄账户',
      checking: '支票账户',
      credit: '信用卡',
    };
    return types[type] || type;
  };

  const getAccountTypeIcon = (type: string) => {
    return CreditCard; // 简化处理
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">账户管理</h1>
          <p className="text-gray-400">管理您的银行账户和交易记录</p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>刷新</span>
        </button>
      </div>

      {/* 账户卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts.map((account) => {
          const Icon = getAccountTypeIcon(account.account_type);
          const isSelected = selectedAccount?.id === account.id;

          return (
            <motion.div
              key={account.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`bg-gray-800 border rounded-lg p-6 cursor-pointer transition-all hover:border-gray-600 ${
                isSelected ? 'border-blue-500 ring-1 ring-blue-500/20' : 'border-gray-700'
              }`}
              onClick={() => setSelectedAccount(account)}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">
                      {getAccountTypeName(account.account_type)}
                    </h3>
                    <p className="text-gray-400 text-sm">
                      {account.account_number.replace(/(\d{4})\d{10}(\d{4})/, '$1****$2')}
                    </p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowBalance(!showBalance);
                  }}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  {showBalance ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-gray-400 text-sm">账户余额</p>
                  <p className="text-2xl font-bold text-white">
                    {formatBalance(account.balance)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">可用余额</p>
                  <p className="text-lg font-medium text-gray-300">
                    {formatBalance(account.available_balance)}
                  </p>
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-gray-700">
                  <span className="text-xs text-gray-500">
                    {new Date(account.opened_date).toLocaleDateString()}开户
                  </span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    account.status === 'active' 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {account.status === 'active' ? '正常' : '冻结'}
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* 交易记录 */}
      {selectedAccount && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800 border border-gray-700 rounded-lg"
        >
          <div className="p-6 border-b border-gray-700">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
                <ArrowUpDown className="w-5 h-5" />
                <span>交易记录</span>
              </h2>
              <button className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors">
                <Download className="w-4 h-4" />
                <span>导出</span>
              </button>
            </div>
          </div>

          <div className="p-6">
            <div className="space-y-4">
              {transactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      transaction.amount > 0 ? 'bg-green-500/20' : 'bg-red-500/20'
                    }`}>
                      <DollarSign className={`w-5 h-5 ${
                        transaction.amount > 0 ? 'text-green-400' : 'text-red-400'
                      }`} />
                    </div>
                    <div>
                      <p className="text-white font-medium">{transaction.description}</p>
                      <div className="flex items-center space-x-2 text-sm text-gray-400">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(transaction.created_at).toLocaleString()}</span>
                        <span>•</span>
                        <span>{transaction.transaction_number}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-semibold ${
                      transaction.amount > 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {transaction.amount > 0 ? '+' : ''}¥{Math.abs(transaction.amount).toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-400">
                      余额: ¥{transaction.balance_after.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {transactions.length === 0 && (
              <div className="text-center py-8">
                <p className="text-gray-400">暂无交易记录</p>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}