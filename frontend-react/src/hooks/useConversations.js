import { useState, useEffect, useCallback } from 'react';

const useConversations = () => {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  // Load conversations from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('jee_conversations');
    if (stored) {
      const parsed = JSON.parse(stored);
      setConversations(parsed.conversations || []);
      setActiveConversationId(parsed.activeConversationId || null);
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (conversations.length > 0 || activeConversationId) {
      localStorage.setItem('jee_conversations', JSON.stringify({
        conversations,
        activeConversationId
      }));
    }
  }, [conversations, activeConversationId]);

  const createNewConversation = useCallback((firstMessage = null) => {
    const newConv = {
      id: `conv_${Date.now()}`,
      title: firstMessage ? firstMessage.substring(0, 50) : 'New Chat',
      created_at: new Date().toISOString(),
      last_message_at: new Date().toISOString(),
      messages: [],
      session_id: null,
      hints_used: 0,
      progress: 0
    };

    setConversations(prev => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
    return newConv.id;
  }, []);

  const updateConversation = useCallback((conversationId, updates) => {
    setConversations(prev =>
      prev.map(conv =>
        conv.id === conversationId
          ? { ...conv, ...updates, last_message_at: new Date().toISOString() }
          : conv
      )
    );
  }, []);

  const deleteConversation = useCallback((conversationId) => {
    setConversations(prev => prev.filter(conv => conv.id !== conversationId));
    if (activeConversationId === conversationId) {
      setActiveConversationId(conversations[0]?.id || null);
    }
  }, [activeConversationId, conversations]);

  const getActiveConversation = useCallback(() => {
    return conversations.find(conv => conv.id === activeConversationId) || null;
  }, [conversations, activeConversationId]);

  return {
    conversations,
    activeConversationId,
    setActiveConversationId,
    createNewConversation,
    updateConversation,
    deleteConversation,
    getActiveConversation
  };
};

export default useConversations;
