import React from 'react';
import { useNotification } from '../../hooks/useNotification';

export default function Toast() {
  const { notifications, removeNotification } = useNotification();

  if (!notifications.length) return null;

  return (
    <div className="toast-container">
      {notifications.map(({ id, message, type }) => (
        <div key={id} className={`toast-item toast-${type}`}>
          <span className="toast-icon">
            {type === 'success' && '✓'}
            {type === 'error' && '✕'}
            {type === 'warning' && '⚠'}
            {type === 'info' && 'ℹ'}
          </span>
          <span className="toast-message">{message}</span>
          <button className="toast-close" onClick={() => removeNotification(id)}>
            &times;
          </button>
        </div>
      ))}
    </div>
  );
}
