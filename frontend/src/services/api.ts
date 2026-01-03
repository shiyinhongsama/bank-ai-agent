/**
 * API服务
 */

import axios, { AxiosResponse } from 'axios';
import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  Account, 
  Transaction, 
  InvestmentProduct, 
  InvestmentAccount, 
  LoanProduct, 
  LoanApplication, 
  ChatMessage, 
  ChatResponse,
  TransferRequest,
  LoanApplicationRequest,
  ApiResponse,
  AgentInfo,
  KnowledgeResult
} from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // token过期，清除本地存储并跳转到登录页
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authApi = {
  login: (data: LoginRequest): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/api/v1/auth/login', data),
  
  register: (data: RegisterRequest): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/api/v1/auth/register', data),
  
  logout: (): Promise<AxiosResponse<{ message: string }>> =>
    api.post('/api/v1/auth/logout'),
  
  getCurrentUser: (): Promise<AxiosResponse<AuthResponse['user']>> =>
    api.get('/api/v1/auth/me'),
};

// 账户相关API
export const accountApi = {
  getAccounts: (): Promise<AxiosResponse<Account[]>> =>
    api.get('/api/v1/accounts/'),
  
  getAccount: (accountId: number): Promise<AxiosResponse<Account>> =>
    api.get(`/api/v1/accounts/${accountId}`),
  
  getAccountTransactions: (
    accountId: number, 
    limit: number = 20, 
    offset: number = 0
  ): Promise<AxiosResponse<Transaction[]>> =>
    api.get(`/api/v1/accounts/${accountId}/transactions?limit=${limit}&offset=${offset}`),
  
  getAccountBalance: (accountId: number): Promise<AxiosResponse<{ balance: number; available_balance: number }>> =>
    api.get(`/api/v1/accounts/${accountId}/balance`),
};

// 交易相关API
export const transactionApi = {
  transferMoney: (data: TransferRequest): Promise<AxiosResponse<{
    transaction_id: string;
    status: string;
    amount: number;
    estimated_arrival: string;
  }>> =>
    api.post('/api/v1/transactions/transfer', data),
  
  getTransferStatus: (transactionId: string): Promise<AxiosResponse<{
    transaction_id: string;
    status: string;
    amount: number;
    processed_at: string;
    arrived_at: string;
  }>> =>
    api.get(`/api/v1/transactions/transfer/${transactionId}`),
  
  getTransferLimits: (accountId: number): Promise<AxiosResponse<{
    daily_limit: number;
    monthly_limit: number;
    single_limit: number;
    used_today: number;
    used_this_month: number;
  }>> =>
    api.get(`/api/v1/transactions/limits?account_id=${accountId}`),
};

// 投资理财相关API
export const investmentApi = {
  getProducts: (params?: {
    risk_level?: string;
    investment_type?: string;
  }): Promise<AxiosResponse<InvestmentProduct[]>> =>
    api.get('/api/v1/investments/products', { params }),
  
  getProduct: (productId: number): Promise<AxiosResponse<InvestmentProduct>> =>
    api.get(`/api/v1/investments/products/${productId}`),
  
  getAccounts: (userId: number = 1): Promise<AxiosResponse<InvestmentAccount[]>> =>
    api.get(`/api/v1/investments/accounts?user_id=${userId}`),
  
  purchaseInvestment: (productId: number, amount: number): Promise<AxiosResponse<{
    success: boolean;
    message: string;
    data: any;
  }>> =>
    api.post('/api/v1/investments/purchase', {
      product_id: productId,
      amount: amount,
    }),
};

// 贷款相关API
export const loanApi = {
  getProducts: (params?: {
    loan_type?: string;
    max_amount?: number;
  }): Promise<AxiosResponse<LoanProduct[]>> =>
    api.get('/api/v1/loans/products', { params }),
  
  getProduct: (productId: number): Promise<AxiosResponse<LoanProduct>> =>
    api.get(`/api/v1/loans/products/${productId}`),
  
  createApplication: (data: LoanApplicationRequest): Promise<AxiosResponse<LoanApplication>> =>
    api.post('/api/v1/loans/applications', data),
  
  getApplications: (userId: number = 1): Promise<AxiosResponse<LoanApplication[]>> =>
    api.get(`/api/v1/loans/applications?user_id=${userId}`),
  
  getApplication: (applicationId: number): Promise<AxiosResponse<LoanApplication>> =>
    api.get(`/api/v1/loans/applications/${applicationId}`),
};

// 聊天相关API
export const chatApi = {
  sendMessage: (data: ChatMessage): Promise<AxiosResponse<ChatResponse>> =>
    api.post('/api/v1/chat/message', data),
  
  getAgentInfo: (): Promise<AxiosResponse<AgentInfo>> =>
    api.get('/api/v1/chat/agents'),
};

// Agent管理API
export const agentApi = {
  getStatus: (): Promise<AxiosResponse<{
    success: boolean;
    data: {
      agents: AgentInfo;
      vector_db: any;
      timestamp: string;
    };
  }>> =>
    api.get('/api/v1/agents/status'),
  
  addKnowledge: (content: string, category: string, keywords: string[]): Promise<AxiosResponse<{
    success: boolean;
    message: string;
  }>> =>
    api.post('/api/v1/agents/knowledge/add', {
      content,
      category,
      keywords,
    }),
  
  searchKnowledge: (query: string, limit: number = 5): Promise<AxiosResponse<{
    success: boolean;
    data: {
      query: string;
      results: KnowledgeResult[];
      count: number;
    };
  }>> =>
    api.get('/api/v1/agents/knowledge/search', {
      params: { query, limit },
    }),
};

// 健康检查API
export const healthApi = {
  check: (): Promise<AxiosResponse<{ status: string; service: string; version: string }>> =>
    api.get('/health'),
};

export default api;