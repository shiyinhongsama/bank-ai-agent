/**
 * 智能客服页面
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Brain } from 'lucide-react';
import { chatApi } from '../services/api';
import { ConversationMessage } from '../types';
import toast from 'react-hot-toast';

export default function Chat() {
  const [messages, setMessages] = useState<ConversationMessage[]>([
    {
      id: '1',
      type: 'assistant',
      content: '您好！我是银行AI智能助手，很高兴为您服务。我可以帮助您解答账户、转账、理财、贷款等各类问题，请随时向我提问。',
      timestamp: new Date().toISOString(),
      agent_type: 'general',
      confidence: 1.0,
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState('general');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: userMessage.content,
        conversation_id: 'chat-session',
      });

      const assistantMessage: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        agent_type: response.data.agent_type,
        confidence: response.data.confidence,
      };

      setCurrentAgent(response.data.agent_type);
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('发送消息失败:', error);
      toast.error('发送消息失败，请重试');
      
      const errorMessage: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '抱歉，我现在无法处理您的请求，请稍后再试。',
        timestamp: new Date().toISOString(),
        agent_type: 'error',
        confidence: 0,
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getAgentDisplayName = (agentType: string) => {
    const agentNames: Record<string, string> = {
      general: '通用客服',
      account: '账户专员',
      transfer: '转账专员',
      investment: '理财专员',
      loan: '贷款专员',
      security: '安全专员',
      error: '系统',
    };
    return agentNames[agentType] || 'AI助手';
  };

  const getAgentColor = (agentType: string) => {
    const colors: Record<string, string> = {
      general: 'from-blue-500 to-blue-600',
      account: 'from-green-500 to-green-600',
      transfer: 'from-purple-500 to-purple-600',
      investment: 'from-yellow-500 to-yellow-600',
      loan: 'from-red-500 to-red-600',
      security: 'from-orange-500 to-orange-600',
      error: 'from-gray-500 to-gray-600',
    };
    return colors[agentType] || 'from-gray-500 to-gray-600';
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-3">
          <Brain className="w-8 h-8 text-blue-400" />
          <span>智能客服</span>
        </h1>
        <p className="text-gray-400">与AI助手对话，获取专业的银行服务支持</p>
      </div>

      {/* 聊天区域 */}
      <div className="flex-1 bg-gray-800 border border-gray-700 rounded-lg flex flex-col">
        {/* 聊天头部 */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 bg-gradient-to-br ${getAgentColor(currentAgent)} rounded-full flex items-center justify-center`}>
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-medium">{getAgentDisplayName(currentAgent)}</h3>
              <p className="text-gray-400 text-sm">
                {currentAgent !== 'error' ? '在线' : '服务暂时不可用'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <span className="text-blue-400 text-sm font-medium">AI驱动</span>
          </div>
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  {/* 头像 */}
                  <div className={`flex-shrink-0 ${message.type === 'user' ? 'ml-3' : 'mr-3'}`}>
                    {message.type === 'user' ? (
                      <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    ) : (
                      <div className={`w-8 h-8 bg-gradient-to-br ${getAgentColor(message.agent_type || 'general')} rounded-full flex items-center justify-center`}>
                        <Bot className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </div>

                  {/* 消息内容 */}
                  <div className={`rounded-lg p-3 ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-100'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.type === 'assistant' && (
                      <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
                        <span>{getAgentDisplayName(message.agent_type || 'general')}</span>
                        {message.confidence && (
                          <span>置信度: {Math.round(message.confidence * 100)}%</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* 加载指示器 */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="flex max-w-[80%]">
                <div className="mr-3">
                  <div className={`w-8 h-8 bg-gradient-to-br ${getAgentColor(currentAgent)} rounded-full flex items-center justify-center`}>
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="bg-gray-700 rounded-lg p-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入您的问题..."
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={1}
                style={{
                  minHeight: '48px',
                  maxHeight: '120px',
                  height: 'auto',
                }}
              />
            </div>
            <motion.button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg flex items-center justify-center transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>
          
          {/* 快捷问题 */}
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              '查询账户余额',
              '如何进行转账？',
              '推荐理财产品',
              '申请贷款流程',
            ].map((question, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(question)}
                className="px-3 py-1 text-sm text-gray-400 bg-gray-700 hover:bg-gray-600 rounded-full transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}