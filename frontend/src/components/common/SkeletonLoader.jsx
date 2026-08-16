import React from 'react';

export default function SkeletonLoader({ tabName }) {
  return (
    <div className="skeleton-container">
      <div className="skeleton-header">
        <div className="skeleton-bar title-bar" />
        <div className="skeleton-bar subtitle-bar" />
      </div>
      <div className="skeleton-grid">
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card wide" />
      </div>
      <div className="skeleton-status">
        <div className="spinner-sm" />
        <span>Loading {tabName || 'module'}...</span>
      </div>
    </div>
  );
}
