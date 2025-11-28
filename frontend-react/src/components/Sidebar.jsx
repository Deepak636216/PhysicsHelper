import React from 'react';

const Sidebar = ({ isOpen, onToggle, onNewChat, conversations, activeConversationId, onSelectConversation }) => {
  // Group conversations by date
  const groupConversationsByDate = (conversations) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const groups = {
      today: [],
      yesterday: [],
      previous7Days: [],
      previous30Days: [],
      older: []
    };

    conversations.forEach(conv => {
      const convDate = new Date(conv.last_message_at || conv.created_at);

      if (convDate >= today) {
        groups.today.push(conv);
      } else if (convDate >= yesterday) {
        groups.yesterday.push(conv);
      } else if (convDate >= sevenDaysAgo) {
        groups.previous7Days.push(conv);
      } else if (convDate >= thirtyDaysAgo) {
        groups.previous30Days.push(conv);
      } else {
        groups.older.push(conv);
      }
    });

    return groups;
  };

  const groups = groupConversationsByDate(conversations);

  const ConversationGroup = ({ title, conversations }) => {
    if (conversations.length === 0) return null;

    return (
      <div className="conversation-group">
        <div className="group-title">{title}</div>
        {conversations.map(conv => (
          <div
            key={conv.id}
            className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
            onClick={() => onSelectConversation(conv.id)}
          >
            <div className="conversation-title">{conv.title}</div>
            <div className="conversation-meta">
              {conv.hints_used > 0 && <span className="meta-badge">💡 {conv.hints_used}</span>}
              {conv.progress > 0 && <span className="meta-badge">📊 {conv.progress}%</span>}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <span className="btn-icon">➕</span>
          New Chat
        </button>
      </div>

      <div className="conversations-list">
        <ConversationGroup title="Today" conversations={groups.today} />
        <ConversationGroup title="Yesterday" conversations={groups.yesterday} />
        <ConversationGroup title="Previous 7 Days" conversations={groups.previous7Days} />
        <ConversationGroup title="Previous 30 Days" conversations={groups.previous30Days} />
        <ConversationGroup title="Older" conversations={groups.older} />
      </div>
    </div>
  );
};

export default Sidebar;
