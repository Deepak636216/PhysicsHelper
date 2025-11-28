import React, { useEffect, useRef, useMemo } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const Message = ({ role, content, type }) => {
  const messageRef = useRef(null);

  // Configure marked to not escape HTML and preserve math
  marked.setOptions({
    breaks: true,
    gfm: true,
  });

  // Parse markdown and sanitize HTML
  const htmlContent = useMemo(() => {
    try {
      // For user messages, just sanitize without markdown parsing
      if (role === 'user') {
        return DOMPurify.sanitize(content.replace(/\n/g, '<br>'));
      }

      // For assistant messages, parse markdown
      const rawHtml = marked.parse(content);
      return DOMPurify.sanitize(rawHtml, {
        ADD_TAGS: ['math', 'annotation', 'semantics', 'mrow', 'mi', 'mo', 'mn', 'mfrac', 'msup', 'msub'],
        ADD_ATTR: ['xmlns', 'display']
      });
    } catch (error) {
      console.error('Error parsing markdown:', error);
      return DOMPurify.sanitize(content);
    }
  }, [content, role]);

  useEffect(() => {
    // Re-render MathJax when message content changes
    if (window.MathJax && window.MathJax.typesetPromise && messageRef.current) {
      // Use a small delay to ensure DOM is updated
      setTimeout(() => {
        window.MathJax.typesetPromise([messageRef.current]).catch((err) =>
          console.error('MathJax rendering error:', err)
        );
      }, 50);
    }
  }, [content, htmlContent]);

  const getMessageClass = () => {
    if (type === 'hint') return 'message hint-message';
    if (type === 'solution') return 'message solution-message';
    if (role === 'user') return 'message user-message';
    return 'message assistant-message';
  };

  const getMessageIcon = () => {
    if (type === 'hint') return '💡';
    if (type === 'solution') return '✓';
    if (role === 'user') return '👤';
    return '🤖';
  };

  return (
    <div className={getMessageClass()} ref={messageRef}>
      <div className="message-icon">{getMessageIcon()}</div>
      <div className="message-content">
        <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
      </div>
    </div>
  );
};

export default Message;
