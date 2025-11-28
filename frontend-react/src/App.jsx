import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import ActionButtons from './components/ActionButtons';
import InputArea from './components/InputArea';
import useSession from './hooks/useSession';
import useProgress from './hooks/useProgress';
import useChat from './hooks/useChat';
import useConversations from './hooks/useConversations';
import conversationLogger from './utils/conversationLogger';
import './App.css';

function App() {
  const { sessionId, resetSession, initializeSession } = useSession();
  const { progress, hintsUsed, maxHints, updateProgress, resetProgress } = useProgress();
  const { messages, isLoading, sendMessage, requestHint, requestSolution, clearMessages } = useChat(
    sessionId,
    initializeSession,
    updateProgress
  );

  const {
    conversations,
    activeConversationId,
    setActiveConversationId,
    createNewConversation,
    updateConversation,
    getActiveConversation
  } = useConversations();

  const [showWelcome, setShowWelcome] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleSendMessage = async (message) => {
    setShowWelcome(false);

    // Start logger session if first message
    if (!conversationLogger.getCurrentSession()) {
      const studentId = localStorage.getItem('jee_student_id');
      conversationLogger.startSession(sessionId, studentId);
    }

    // Log user message
    conversationLogger.logMessage({
      role: 'user',
      content: message,
      type: 'chat'
    });

    // Create new conversation if first message
    if (!activeConversationId) {
      const newConvId = createNewConversation(message);
      updateConversation(newConvId, {
        session_id: sessionId,
        messages: [...messages]
      });
    }

    await sendMessage(message);
  };

  const handleHintClick = async () => {
    conversationLogger.logInteraction('hint_request');
    await requestHint();
  };

  const handleSolutionClick = async () => {
    conversationLogger.logInteraction('solution_request');
    await requestSolution();
  };

  const handleNewChat = () => {
    // End current logging session before starting new chat
    if (conversationLogger.getCurrentSession()) {
      conversationLogger.endSession({
        final_progress: progress,
        final_hints_used: hintsUsed
      });
    }

    resetSession();
    resetProgress();
    clearMessages();
    setShowWelcome(true);
    createNewConversation();
  };

  const handleSelectConversation = (conversationId) => {
    setActiveConversationId(conversationId);
    const conv = conversations.find(c => c.id === conversationId);
    if (conv) {
      // Load conversation data
      // This would load messages, hints, progress from the saved conversation
      setShowWelcome(conv.messages.length === 0);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Update active conversation with current state
  useEffect(() => {
    if (activeConversationId && messages.length > 0) {
      updateConversation(activeConversationId, {
        messages,
        hints_used: hintsUsed,
        progress,
        session_id: sessionId
      });
    }
  }, [messages, hintsUsed, progress, activeConversationId, sessionId, updateConversation]);

  return (
    <div className="app-layout">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
        onNewChat={handleNewChat}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
      />

      <div className="main-content">
        <Header
          onToggleSidebar={toggleSidebar}
          hintsUsed={hintsUsed}
          maxHints={maxHints}
          progress={progress}
        />
        <ChatArea messages={messages} showWelcome={showWelcome} isLoading={isLoading} />
        <ActionButtons
          onHintClick={handleHintClick}
          onSolutionClick={handleSolutionClick}
          onNewQuestionClick={handleNewChat}
          disabled={isLoading}
        />
        <InputArea onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}

export default App;
