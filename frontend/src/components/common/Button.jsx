import React from 'react';

export default function Button({ children, variant = 'primary', className = '', ...props }) {
  const classes = [`btn`, `btn-${variant}`, className].filter(Boolean).join(' ');
  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
