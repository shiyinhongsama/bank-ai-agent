/**
 * TypeScript类型定义
 */

// 用户相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  is_verified: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// 账户相关类型
export interface Account {
  id: number;
  account_number: string;
  account_type: string;
  currency: string;
  balance: number;
  available_balance: number;
  status: string;
  opened_date: string;
  last_transaction_date: string;
}

export interface Transaction {
  id: number;
  transaction_number: string;
  transaction_type: string;
  amount: number;
  currency: string;
  balance_after: number;
  status: string;
  description: string;
  created_at: string;
}

// 投资理财相关类型
export interface InvestmentProduct {
  id: number;
  name: string;
  product_code: string;
  investment_type: string;
  risk_level: string;
  expected_return: number;
  min_investment: number;
  max_investment: number;
  currency: string;
  is_available: boolean;
  description: string;
  features: string[];
  fees: string;
}

export interface InvestmentAccount {
  id: number;
  account_number: string;
  product_name: string;
  investment_amount: number;
  current_value: number;
  total_return: number;
  return_rate: number;
  status: string;
  investment_date: string;
  last_valuation_date: string;
}

// 贷款相关类型
export interface LoanProduct {
  id: number;
  name: string;
  product_code: string;
  loan_type: string;
  min_amount: number;
  max_amount: number;
  min_term_months: number;
  max_term_months: number;
  interest_rate: number;
  processing_fee: number;
  min_income: number;
  min_credit_score: number;
  is_available: boolean;
  description: string;
  requirements: string;
}

export interface LoanApplication {
  id: number;
  application_number: string;
  product_name: string;
  requested_amount: number;
  requested_term_months: number;
  status: string;
  submitted_at: string;
  approved_amount?: number;
  approved_interest_rate?: number;
}

// 聊天相关类型
export interface ChatMessage {
  message: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  agent_type: string;
  confidence: number;
  conversation_id: string;
  timestamp: string;
}

export interface ConversationMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  agent_type?: string;
  confidence?: number;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Agent相关类型
export interface AgentInfo {
  agents: Record<string, {
    type: string;
    name: string;
    capabilities: string[];
  }>;
  conversation_states: number;
}

export interface KnowledgeResult {
  content: string;
  metadata: {
    category: string;
    keywords: string[];
    created_at: string;
  };
  distance: number;
  id: string;
}

// 统计数据类型
export interface DashboardStats {
  total_balance: number;
  monthly_income: number;
  investment_returns: number;
  loan_applications: number;
}

// 主题相关类型
export interface ThemeConfig {
  isDark: boolean;
  primaryColor: string;
  secondaryColor: string;
}

// 导航相关类型
export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavigationItem[];
}

// 表单相关类型
export interface TransferRequest {
  from_account_id: number;
  to_account_number: string;
  to_account_name: string;
  to_bank_name: string;
  amount: number;
  currency: string;
  description: string;
}

export interface LoanApplicationRequest {
  product_id: number;
  requested_amount: number;
  requested_term_months: number;
  purpose: string;
  monthly_income: number;
  employment_status: string;
  employer_name?: string;
  work_years?: number;
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: 'chat_response' | 'error' | 'typing' | 'connected' | 'disconnected';
  data: any;
}