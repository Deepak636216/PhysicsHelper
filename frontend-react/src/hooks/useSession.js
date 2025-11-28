import { useState, useCallback } from 'react';

const useSession = () => {
  const [sessionId, setSessionId] = useState(null);

  const resetSession = useCallback(() => {
    setSessionId(null);
  }, []);

  const initializeSession = useCallback((newSessionId) => {
    setSessionId(newSessionId);
  }, []);

  return {
    sessionId,
    resetSession,
    initializeSession,
  };
};

export default useSession;
