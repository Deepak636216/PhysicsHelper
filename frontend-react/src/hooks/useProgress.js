import { useState, useCallback } from 'react';

const useProgress = () => {
  const [progress, setProgress] = useState(0);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [maxHints, setMaxHints] = useState(3);

  const updateProgress = useCallback((newProgress, newHintsUsed, newMaxHints) => {
    if (newProgress !== null && newProgress !== undefined) {
      setProgress(newProgress);
    }
    if (newHintsUsed !== undefined) {
      setHintsUsed(newHintsUsed);
    }
    if (newMaxHints !== undefined) {
      setMaxHints(newMaxHints);
    }
  }, []);

  const resetProgress = useCallback(() => {
    setProgress(0);
    setHintsUsed(0);
    setMaxHints(3);
  }, []);

  return {
    progress,
    hintsUsed,
    maxHints,
    updateProgress,
    resetProgress,
  };
};

export default useProgress;
