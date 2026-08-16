import React, { createContext, useState, useEffect, useRef, useCallback } from 'react';
import { startMonitor, stopMonitor, connectMonitorSocket, fetchMonitorUserTrends } from '../services/apiClient';
import { useNotification } from '../hooks/useNotification';
import { useAppContext } from '../hooks/useAppContext';

export const MonitorContext = createContext();

export function MonitorProvider({ children }) {
  const { addNotification } = useNotification();
  const { modelChoice } = useAppContext();

  const [monitorRunning, setMonitorRunning] = useState(false);
  const [monitorLoading, setMonitorLoading] = useState(false);
  const [monitorEvents, setMonitorEvents] = useState([]);
  const [userTrends, setUserTrends] = useState([]);
  const socketRef = useRef(null);

  const refreshUserTrends = useCallback(async () => {
    try {
      const data = await fetchMonitorUserTrends();
      setUserTrends(data);
    } catch (err) {
      // Background trend refresh non-critical
    }
  }, []);

  const handleStartMonitor = useCallback(async () => {
    setMonitorLoading(true);
    try {
      await startMonitor(modelChoice);
      setMonitorRunning(true);
      addNotification(`Live feed monitor started with ${modelChoice}`, 'success');
      refreshUserTrends();
    } catch (err) {
      addNotification(err.message || 'Failed to start monitor service.', 'error');
    } finally {
      setMonitorLoading(false);
    }
  }, [modelChoice, addNotification, refreshUserTrends]);

  const handleStopMonitor = useCallback(async () => {
    setMonitorLoading(true);
    try {
      await stopMonitor();
      setMonitorRunning(false);
      addNotification('Live feed monitor stopped', 'info');
    } catch (err) {
      addNotification(err.message || 'Failed to stop monitor service.', 'error');
    } finally {
      setMonitorLoading(false);
    }
  }, [addNotification]);

  useEffect(() => {
    // Only connect while the monitor is actually running -- matches the backend, which
    // only ever pushes 'event'/'error' messages while its feed loop is active, and avoids
    // an idle socket sitting open (and reconnecting on every mount) when it's not.
    if (!monitorRunning) {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      return undefined;
    }

    const socket = connectMonitorSocket((msg) => {
      // The backend (services/monitor_manager.py) sends flat messages, not a
      // { type, data } envelope: {"type": "history", "events": [...]} on connect,
      // {"type": "event", post, prob_suicide, tier_num, ...} per tick, and
      // {"type": "error", "detail": ...} if the feed loop dies.
      if (msg.type === 'history') {
        setMonitorEvents(msg.events.slice(0, 50));
      } else if (msg.type === 'event') {
        setMonitorEvents((prev) => [msg, ...prev].slice(0, 50));
        refreshUserTrends();
      } else if (msg.type === 'error') {
        setMonitorRunning(false);
        addNotification(`Live monitor stopped: ${msg.detail}`, 'error');
      }
    });
    socketRef.current = socket;
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [monitorRunning, refreshUserTrends, addNotification]);

  const value = {
    monitorRunning,
    monitorLoading,
    monitorEvents,
    userTrends,
    handleStartMonitor,
    handleStopMonitor,
    refreshUserTrends,
  };

  return <MonitorContext.Provider value={value}>{children}</MonitorContext.Provider>;
}
