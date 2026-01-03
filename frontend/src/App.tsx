/**
 * 主应用组件
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './hooks/useAuth';

// 布局组件
import Layout from './components/layout/Layout';
import AuthLayout from './components/layout/AuthLayout';

// 页面组件
import Dashboard from './pages/Dashboard';
import Accounts from './pages/Accounts';
import Transactions from './pages/Transactions';
import Investments from './pages/Investments';
import Loans from './pages/Loans';
import Chat from './pages/Chat';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// 创建QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5分钟
    },
  },
});

// 受保护的路由组件
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

// 公开路由组件（已登录用户重定向到dashboard）
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/dashboard" /> : <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-950 text-white">
            <Routes>
              {/* 公开路由 */}
              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <AuthLayout>
                      <Login />
                    </AuthLayout>
                  </PublicRoute>
                }
              />
              <Route
                path="/register"
                element={
                  <PublicRoute>
                    <AuthLayout>
                      <Register />
                    </AuthLayout>
                  </PublicRoute>
                }
              />

              {/* 受保护的路由 */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="accounts" element={<Accounts />} />
                <Route path="transactions" element={<Transactions />} />
                <Route path="investments" element={<Investments />} />
                <Route path="loans" element={<Loans />} />
                <Route path="chat" element={<Chat />} />
              </Route>

              {/* 默认路由 */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>

            {/* Toast通知 */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#1f2937',
                  color: '#f9fafb',
                  border: '1px solid #374151',
                },
                success: {
                  iconTheme: {
                    primary: '#10b981',
                    secondary: '#f9fafb',
                  },
                },
                error: {
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#f9fafb',
                  },
                },
              }}
            />
          </div>
        </Router>
      </AuthProvider>
      
      {/* React Query开发工具 */}
      {import.meta.env.DEV && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
}

export default App;
