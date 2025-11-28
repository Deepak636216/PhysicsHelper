import { useState, useCallback } from 'react';
import chatAPI from '../services/api';
import conversationLogger from '../utils/conversationLogger';

const useChat = (sessionId, initializeSession, updateProgress) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(
    async (userMessage) => {
      if (!userMessage.trim()) return;

      setIsLoading(true);

      try {
        // Add user message to UI
        setMessages((prev) => [
          ...prev,
          { role: 'user', content: userMessage, type: null },
        ]);

        // Send to backend
        const response = await chatAPI.sendMessage(sessionId, userMessage);

        // Initialize session if first message
        if (!sessionId && response.session_id) {
          initializeSession(response.session_id);
          // Update logger with the new session ID
          conversationLogger.updateSessionId(response.session_id);
        }

        // Add assistant response
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: response.response, type: null },
        ]);

        // Log assistant response
        conversationLogger.logMessage({
          role: 'assistant',
          content: response.response,
          type: 'chat',
          metadata: response.metadata
        });

        // Update progress from metadata
        if (response.metadata) {
          const { progress_score, hints_used } = response.metadata;
          updateProgress(progress_score, hints_used, 3);

          // Log progress update
          conversationLogger.logProgress({
            progress_score,
            hints_used
          });
        }
      } catch (error) {
        console.error('Error sending message:', error);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'Sorry, there was an error processing your request.',
            type: null,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, initializeSession, updateProgress]
  );

  const requestHint = useCallback(async () => {
    if (!sessionId) return;

    setIsLoading(true);

    try {
      const response = await chatAPI.requestHint(sessionId);

      if (response.success) {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: response.hint, type: 'hint' },
        ]);

        // Log hint response
        conversationLogger.logMessage({
          role: 'assistant',
          content: response.hint,
          type: 'hint',
          metadata: { hint_level: response.hint_level }
        });

        // Update hints used
        updateProgress(null, response.hints_used, 3);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: response.message || 'Maximum hints reached.',
            type: 'hint',
          },
        ]);
      }
    } catch (error) {
      console.error('Error requesting hint:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, there was an error getting a hint.',
          type: 'hint',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, updateProgress]);

  const requestSolution = useCallback(async () => {
    if (!sessionId) return;

    setIsLoading(true);

    try {
      const response = await chatAPI.requestSolution(sessionId);

      // Build solution message with feedback
      let solutionContent = response.feedback + '\n\n';
      if (response.solution) {
        solutionContent += response.solution;
        if (response.final_answer) {
          solutionContent += '\n\n**Final Answer:** ' + response.final_answer;
        }
      }

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: solutionContent, type: 'solution' },
      ]);

      // Log solution response
      conversationLogger.logMessage({
        role: 'assistant',
        content: solutionContent,
        type: 'solution',
        metadata: {
          solution_unlocked: response.solution_unlocked,
          progress_percentage: response.progress_percentage
        }
      });

      // Update progress
      if (response.progress_percentage !== undefined) {
        updateProgress(response.progress_percentage, null, 3);
      }
    } catch (error) {
      console.error('Error requesting solution:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, there was an error getting the solution.',
          type: 'solution',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, updateProgress]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    requestHint,
    requestSolution,
    clearMessages,
  };
};

export default useChat;
