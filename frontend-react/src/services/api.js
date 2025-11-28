const API_BASE_URL = '/api';

// Get or create student ID
const getStudentId = () => {
  let studentId = localStorage.getItem('jee_student_id');
  if (!studentId) {
    studentId = `student_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    localStorage.setItem('jee_student_id', studentId);
  }
  return studentId;
};

export const chatAPI = {
  async sendMessage(sessionId, message) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        student_id: getStudentId(),
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  },

  async requestHint(sessionId) {
    const response = await fetch(`${API_BASE_URL}/request-hint`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        student_id: getStudentId(),
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to request hint');
    }

    return response.json();
  },

  async requestSolution(sessionId) {
    const response = await fetch(`${API_BASE_URL}/request-solution`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        student_id: getStudentId(),
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to request solution');
    }

    return response.json();
  },
};

export default chatAPI;
