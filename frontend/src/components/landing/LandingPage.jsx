import React, { useEffect, useRef, useState } from 'react';

const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

  .landing-root {
    --bg-dark: #FFFFFF;
    --bg-surface: #F0F8FF;
    --bg-card: #FFFFFF;
    --border-glass: #E2E8F0;
    --border-card: #BAE6FD;
    --border-hover: #0284C7;
    --cyan-accent: #0284C7;
    --cyan-glow: rgba(2, 132, 199, 0.15);
    --indigo-accent: #0369A1;
    --emerald-accent: #059669;
    --rose-accent: #DC2626;
    --amber-accent: #D97706;
    --text-primary: #0A1128;
    --text-secondary: #334155;
    --text-muted: #64748B;

    --font-display: 'Outfit', sans-serif;
    --font-body: 'Plus Jakarta Sans', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    background-color: var(--bg-dark);
    color: var(--text-primary);
    font-family: var(--font-body);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
    min-height: 100vh;
    position: relative;
  }

  .landing-root * { box-sizing: border-box; }
  .landing-root ::selection { background: #BAE6FD; color: #0A1128; }
  .landing-root a { color: var(--cyan-accent); text-decoration: none; font-weight: 500; }
  .landing-root a:hover { text-decoration: underline; }

  /* Background Glow Orbs */
  .landing-root .glow-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(120px);
    pointer-events: none;
    z-index: 0;
  }
  .landing-root .glow-1 {
    top: -100px;
    left: 20%;
    width: 550px;
    height: 550px;
    background: radial-gradient(circle, rgba(2, 132, 199, 0.08) 0%, rgba(255, 255, 255, 0) 70%);
  }
  .landing-root .glow-2 {
    top: 500px;
    right: 5%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(3, 105, 161, 0.06) 0%, rgba(255, 255, 255, 0) 70%);
  }

  .landing-root .wrap {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 24px;
    position: relative;
    z-index: 1;
  }

  /* Navigation Header */
  .landing-nav {
    padding: 20px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-glass);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(255, 255, 255, 0.9);
  }
  .landing-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.15rem;
    color: var(--text-primary);
  }
  .landing-brand-emblem {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--cyan-accent), var(--indigo-accent));
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px var(--cyan-glow);
    color: #fff;
    font-weight: 800;
    font-size: 1.1rem;
  }
  .nav-enter-btn {
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.88rem;
    padding: 9px 20px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--cyan-accent), #0369A1);
    color: #FFF;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .nav-enter-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.35);
  }

  /* Hero Section */
  .landing-root .hero {
    position: relative;
    padding: 64px 0 48px;
    border-bottom: 1px solid var(--border-glass);
  }
  .landing-root .hero-grid {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 40px;
    align-items: center;
  }
  .landing-root .eyebrow {
    font-family: var(--font-mono);
    font-size: 0.76rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--cyan-accent);
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    font-weight: 600;
  }
  .landing-root .eyebrow::before {
    content: '';
    width: 20px;
    height: 2px;
    background: var(--cyan-accent);
    display: inline-block;
  }
  .landing-root .hero h1 {
    font-family: var(--font-display);
    font-size: clamp(2.3rem, 4.4vw, 3.4rem);
    font-weight: 800;
    line-height: 1.12;
    margin: 0 0 16px;
    color: #0F172A;
  }
  .landing-root .hero h1 em {
    font-style: italic;
    color: #0284C7;
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .landing-root .hero-sub {
    font-size: 1.08rem;
    color: var(--text-secondary);
    line-height: 1.65;
    margin-bottom: 28px;
    max-width: 520px;
  }

  .landing-root .cta-row {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }
  .landing-root .cta-btn {
    font-family: var(--font-body);
    font-weight: 700;
    font-size: 0.95rem;
    padding: 13px 26px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--cyan-accent) 0%, #0369A1 100%);
    color: #FFFFFF;
    border: none;
    cursor: pointer;
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.25);
    transition: all 0.25s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .landing-root .cta-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(2, 132, 199, 0.4);
  }
  .landing-root .cta-hint {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .landing-root .hero-visual-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 12px 35px -6px rgba(2, 132, 199, 0.12);
  }
  .landing-root .hero-graphic-img {
    width: 100%;
    height: auto;
    border-radius: 10px;
    display: block;
    border: 1px solid var(--border-glass);
  }

  .landing-root .waveform-box {
    margin-top: 14px;
    background: var(--bg-surface);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 14px 16px 10px;
  }
  .landing-root .waveform-box canvas { width: 100%; height: 75px; display: block; }
  .landing-root .waveform-caption {
    display: flex;
    justify-content: space-between;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--cyan-accent);
    margin-top: 6px;
    text-transform: uppercase;
    font-weight: 600;
  }

  .landing-root .byline {
    margin-top: 32px;
    padding-top: 20px;
    border-top: 1px solid var(--border-glass);
    display: flex;
    flex-wrap: wrap;
    gap: 8px 24px;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--text-secondary);
  }
  .landing-root .byline strong { font-weight: 600; color: var(--text-primary); }

  /* Sections */
  .landing-root section {
    padding: 56px 0;
    border-bottom: 1px solid var(--border-glass);
  }
  .landing-root section:last-of-type { border-bottom: none; }
  .landing-root .section-head { margin-bottom: 32px; }
  .landing-root .section-head h2 {
    font-family: var(--font-display);
    font-size: 1.85rem;
    font-weight: 700;
    margin: 8px 0 12px;
    color: var(--text-primary);
  }
  .landing-root .lede {
    font-size: 1.02rem;
    max-width: 66ch;
    color: var(--text-secondary);
    line-height: 1.65;
    margin-top: 8px;
  }

  /* Pillars */
  .landing-root .pillars {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }
  .landing-root .pillar {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 6px 16px -2px rgba(2, 132, 199, 0.06);
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: all 0.2s ease;
  }
  .landing-root .pillar:hover {
    transform: translateY(-3px);
    border-color: var(--border-hover);
    box-shadow: 0 10px 24px -4px rgba(2, 132, 199, 0.12);
  }
  .landing-root .pillar .tag {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--amber-accent);
    font-weight: 700;
  }
  .landing-root .pillar p { font-size: 0.88rem; margin: 0; color: var(--text-secondary); flex-grow: 1; }
  .landing-root .pillar .stat {
    font-family: var(--font-mono);
    font-size: 0.95rem;
    color: var(--cyan-accent);
    font-weight: 700;
    border-top: 1px solid var(--border-glass);
    padding-top: 10px;
  }

  /* Proposal vs Delivery Scope Table */
  .landing-root .scope-table-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    overflow-x: auto;
    box-shadow: 0 6px 16px -2px rgba(2, 132, 199, 0.06);
  }
  .landing-root .scope-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    min-width: 600px;
  }
  .landing-root .scope-table th {
    text-align: left;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--cyan-accent);
    padding: 14px 18px;
    font-weight: 700;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-card);
  }
  .landing-root .scope-table td {
    padding: 16px 18px;
    border-top: 1px solid var(--border-glass);
    vertical-align: top;
    color: var(--text-secondary);
  }
  .landing-root .scope-table td:first-child { font-weight: 600; color: var(--text-primary); width: 20%; }
  .landing-root .scope-table td.proposed { color: var(--text-muted); width: 35%; }
  .landing-root .scope-table td.delivered { color: var(--text-primary); }

  .landing-root .beyond-list { margin-top: 28px; }
  .landing-root .beyond-list h3 {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--amber-accent);
    font-weight: 700;
    margin-bottom: 14px;
  }
  .landing-root .beyond-list ul {
    margin: 0;
    padding-left: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px 28px;
  }
  .landing-root .beyond-list li {
    font-size: 0.9rem;
    padding-left: 20px;
    position: relative;
    color: var(--text-secondary);
  }
  .landing-root .beyond-list li::before {
    content: '+';
    position: absolute;
    left: 0;
    color: var(--cyan-accent);
    font-family: var(--font-mono);
    font-weight: 700;
  }

  /* Dataset Grid */
  .landing-root .dataset-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 20px;
  }
  .landing-root .dataset-stat {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.05);
  }
  .landing-root .dataset-stat .num {
    font-family: var(--font-mono);
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--cyan-accent);
  }
  .landing-root .dataset-stat .label { font-size: 0.8rem; color: var(--text-muted); }
  .landing-root .dataset-note {
    font-size: 0.9rem;
    color: var(--text-secondary);
    background: var(--bg-surface);
    border: 1px solid var(--border-card);
    border-radius: 8px;
    padding: 16px 20px;
    margin-top: 8px;
  }
  .landing-root .dataset-note strong { color: var(--cyan-accent); }

  /* Evaluation Metrics Table */
  .landing-root .table-scroll {
    overflow-x: auto;
    border: 1px solid var(--border-card);
    border-radius: 12px;
    background: var(--bg-card);
    box-shadow: 0 6px 16px -2px rgba(2, 132, 199, 0.06);
  }
  .landing-root table.metrics {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px;
    font-size: 0.9rem;
  }
  .landing-root table.metrics th, .landing-root table.metrics td {
    padding: 14px 18px;
    text-align: right;
    font-family: var(--font-mono);
  }
  .landing-root table.metrics th:first-child, .landing-root table.metrics td:first-child {
    text-align: left;
    font-family: var(--font-body);
  }
  .landing-root table.metrics thead th {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--cyan-accent);
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-card);
    font-weight: 700;
  }
  .landing-root table.metrics tbody tr:not(:last-child) td { border-bottom: 1px solid var(--border-glass); }
  .landing-root table.metrics tbody tr:hover { background: var(--bg-surface); }
  .landing-root table.metrics td.hero-num { color: var(--emerald-accent); font-weight: 700; }
  .landing-root .table-note { font-size: 0.85rem; color: var(--text-muted); margin-top: 14px; }

  /* Construct Validity Panel */
  .landing-root .cv-panel {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    align-items: center;
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 6px 16px -2px rgba(2, 132, 199, 0.06);
  }
  .landing-root .cv-bars { display: flex; flex-direction: column; gap: 16px; }
  .landing-root .cv-row { display: grid; grid-template-columns: 110px 1fr 56px; align-items: center; gap: 12px; font-size: 0.84rem; }
  .landing-root .cv-track { height: 8px; background: #E2E8F0; border-radius: 4px; overflow: hidden; position: relative; }
  .landing-root .cv-fill { height: 100%; background: linear-gradient(90deg, var(--indigo-accent), var(--cyan-accent)); border-radius: 4px; }
  .landing-root .cv-val { font-family: var(--font-mono); text-align: right; color: var(--cyan-accent); font-weight: 700; }

  /* Fairness Audit */
  .landing-root .cohort-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 20px 0;
  }
  .landing-root .cohort-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 18px;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.05);
  }
  .landing-root .cohort-card .name {
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
    font-family: var(--font-mono);
    margin-bottom: 8px;
  }
  .landing-root .cohort-card .recall {
    font-family: var(--font-mono);
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--cyan-accent);
  }
  .landing-root .cohort-card .recall-label { font-size: 0.78rem; color: var(--text-secondary); }

  .landing-root .fairness-finding {
    background: #FFFFFF;
    border: 1px solid var(--border-card);
    border-radius: 14px;
    padding: 26px 30px;
    margin-top: 24px;
    box-shadow: 0 8px 24px -4px rgba(2, 132, 199, 0.08);
    position: relative;
  }
  .landing-root .fairness-finding-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
    flex-wrap: wrap;
  }
  .landing-root .fairness-finding h4 {
    font-family: var(--font-display);
    font-size: 1.2rem;
    color: var(--text-primary);
    margin: 0;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .landing-root .fairness-badge {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 4px 12px;
    border-radius: 999px;
    background: var(--bg-surface);
    color: var(--cyan-accent);
    border: 1px solid var(--border-card);
  }
  .landing-root .fairness-finding p {
    margin: 0 0 14px;
    font-size: 0.96rem;
    line-height: 1.7;
    color: var(--text-secondary);
  }
  .landing-root .fairness-finding p:last-child { margin-bottom: 0; }
  .landing-root .audit-highlight {
    background: var(--bg-surface);
    color: var(--indigo-accent);
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.92em;
    border: 1px solid var(--border-card);
  }
  .landing-root .audit-highlight-green {
    background: #D1FAE5;
    color: #065F46;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.92em;
    border: 1px solid #A7F3D0;
  }

  /* Limitations List */
  .landing-root .limitations-list {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .landing-root .limitations-list li {
    font-size: 0.92rem;
    padding-left: 24px;
    position: relative;
    color: var(--text-secondary);
  }
  .landing-root .limitations-list li::before {
    content: '→';
    position: absolute;
    left: 0;
    color: var(--cyan-accent);
    font-family: var(--font-mono);
    font-weight: 700;
  }

  /* Ethics & Safeguards Grid */
  .landing-root .ethics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 20px;
  }
  .landing-root .ethics-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.05);
  }
  .landing-root .ethics-card .tag {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--cyan-accent);
    display: block;
    margin-bottom: 8px;
    font-weight: 700;
  }
  .landing-root .ethics-card p { font-size: 0.88rem; margin: 0; color: var(--text-secondary); }
  .landing-root .crisis-note {
    margin-top: 24px;
    padding: 20px 24px;
    background: linear-gradient(135deg, var(--bg-surface), #E0F2FE);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    font-size: 0.9rem;
    display: flex;
    gap: 18px;
    align-items: center;
  }
  .landing-root .crisis-note .num {
    font-family: var(--font-mono);
    font-weight: 800;
    font-size: 1.8rem;
    color: var(--cyan-accent);
  }

  /* Architecture Row */
  .landing-root .arch-row {
    display: flex;
    gap: 0;
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 6px 16px -2px rgba(2, 132, 199, 0.06);
  }
  .landing-root .arch-col { flex: 1; padding: 22px; }
  .landing-root .arch-col + .arch-col { border-left: 1px solid var(--border-card); }
  .landing-root .arch-col .tag {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--amber-accent);
    display: block;
    margin-bottom: 12px;
    font-weight: 700;
  }
  .landing-root .arch-col ul { margin: 0; padding-left: 18px; font-size: 0.88rem; color: var(--text-secondary); }
  .landing-root .arch-col li { margin-bottom: 8px; }

  /* Simulator Card */
  .landing-root .simulator-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(2, 132, 199, 0.08);
    margin-top: 10px;
  }
  .landing-root .sim-presets { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
  .landing-root .sim-preset-btn {
    font-family: var(--font-mono);
    font-size: 0.76rem;
    padding: 6px 14px;
    border-radius: 6px;
    background: var(--bg-surface);
    border: 1px solid var(--border-card);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .landing-root .sim-preset-btn.active, .landing-root .sim-preset-btn:hover {
    background: #BAE6FD;
    border-color: var(--cyan-accent);
    color: #0369A1;
    font-weight: 600;
  }
  .landing-root .sim-display-grid { display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 20px; }
  .landing-root .sim-textbox {
    background: #F8FAFC;
    border: 1px solid var(--border-glass);
    border-radius: 10px;
    padding: 16px;
    font-size: 0.95rem;
    line-height: 1.7;
    min-height: 120px;
    color: var(--text-primary);
  }
  .landing-root .token-positive { background: rgba(220, 38, 38, 0.1); color: #991B1B; padding: 2px 6px; border-radius: 4px; border-bottom: 2px solid var(--rose-accent); font-weight: 600; margin: 0 2px; }
  .landing-root .token-negative { background: rgba(5, 150, 105, 0.1); color: #065F46; padding: 2px 6px; border-radius: 4px; border-bottom: 2px solid var(--emerald-accent); font-weight: 600; margin: 0 2px; }
  .landing-root .sim-results-panel { background: var(--bg-surface); border: 1px solid var(--border-card); border-radius: 10px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; }

  /* Footer */
  .landing-root footer { padding: 48px 0 60px; border-top: 1px solid var(--border-glass); }
  .landing-root .footer-row { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 20px; }
  .landing-root .footer-team { font-family: var(--font-mono); font-size: 0.8rem; line-height: 1.8; color: var(--text-muted); }
  .landing-root .footer-disclaimer { font-size: 0.82rem; max-width: 40ch; color: var(--text-muted); text-align: right; }

  @media (max-width: 820px) {
    .landing-root .hero-grid { grid-template-columns: 1fr; }
    .landing-root .pillars { grid-template-columns: repeat(2, 1fr); }
    .landing-root .dataset-grid { grid-template-columns: repeat(2, 1fr); }
    .landing-root .cv-panel { grid-template-columns: 1fr; }
    .landing-root .cohort-grid { grid-template-columns: 1fr; }
    .landing-root .ethics-grid { grid-template-columns: 1fr; }
    .landing-root .arch-row { flex-direction: column; }
    .landing-root .arch-col + .arch-col { border-left: none; border-top: 1px solid var(--border-card); }
    .landing-root .beyond-list ul { grid-template-columns: 1fr; }
    .landing-root .sim-display-grid { grid-template-columns: 1fr; }
    .landing-root .footer-disclaimer { text-align: left; }
  }
`;

function Waveform() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let w = 0, h = 0;

    function resize() {
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      w = rect.width; h = rect.height;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);

    let rafId = null;
    const t0 = performance.now();

    function traceAt(t) {
      const points = [];
      const n = 120;
      for (let i = 0; i < n; i++) {
        const x = i / (n - 1);
        const phase = (x * 6 + t) % 6;
        const base = Math.sin(x * 20 + t * 1.5) * 3.5;
        let spike = 0;
        if (Math.abs(phase - 2.2) < 0.15) spike = (0.15 - Math.abs(phase - 2.2)) / 0.15 * 38;
        if (Math.abs(phase - 4.4) < 0.12) spike = Math.max(spike, (0.12 - Math.abs(phase - 4.4)) / 0.12 * 26);
        points.push(base - spike);
      }
      return points;
    }

    function draw(now) {
      const t = (now - t0) / 1200;
      ctx.clearRect(0, 0, w, h);
      const mid = h * 0.65;

      ctx.strokeStyle = 'rgba(2, 132, 199, 0.08)';
      ctx.lineWidth = 1;
      for (let gx = 0; gx <= w; gx += 30) {
        ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, h); ctx.stroke();
      }

      const pts = traceAt(t);
      ctx.beginPath();
      for (let i = 0; i < pts.length; i++) {
        const x = (i / (pts.length - 1)) * w;
        const y = mid + pts[i];
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = '#0284C7';
      ctx.lineWidth = 2.5;
      ctx.lineJoin = 'round';
      ctx.stroke();

      let maxIdx = 0, maxVal = 1e9;
      for (let j = 0; j < pts.length; j++) {
        if (pts[j] < maxVal) { maxVal = pts[j]; maxIdx = j; }
      }
      if (maxVal < -15) {
        const px = (maxIdx / (pts.length - 1)) * w;
        const py = mid + pts[maxIdx];
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#DC2626';
        ctx.fill();
      }

      rafId = requestAnimationFrame(draw);
    }

    rafId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      if (rafId !== null) cancelAnimationFrame(rafId);
    };
  }, []);

  return <canvas ref={canvasRef} />;
}

const PRESETS = [
  {
    label: 'Sample 1: Direct Crisis',
    text: 'I cannot handle this pain anymore and I want to end my life tonight.',
    risk: 94.8,
    tier: 'Tier 4 — Urgent Escalation',
    tokens: [
      { word: 'I', type: 'norm' }, { word: 'cannot', type: 'pos' }, { word: 'handle', type: 'pos' },
      { word: 'this', type: 'norm' }, { word: 'pain', type: 'pos' }, { word: 'anymore', type: 'pos' },
      { word: 'and', type: 'norm' }, { word: 'I', type: 'norm' }, { word: 'want', type: 'pos' },
      { word: 'to', type: 'norm' }, { word: 'end', type: 'pos' }, { word: 'my', type: 'norm' },
      { word: 'life', type: 'pos' }, { word: 'tonight.', type: 'pos' }
    ]
  },
  {
    label: 'Sample 2: Youth Slang',
    text: 'fr feel like im done with everything, ts is getting too heavy ngl',
    risk: 86.2,
    tier: 'Tier 3 — High Alert Triage',
    tokens: [
      { word: 'fr', type: 'norm' }, { word: 'feel', type: 'norm' }, { word: 'like', type: 'norm' },
      { word: 'im', type: 'norm' }, { word: 'done', type: 'pos' }, { word: 'with', type: 'norm' },
      { word: 'everything,', type: 'pos' }, { word: 'ts', type: 'norm' }, { word: 'is', type: 'norm' },
      { word: 'getting', type: 'norm' }, { word: 'too', type: 'pos' }, { word: 'heavy', type: 'pos' },
      { word: 'ngl', type: 'norm' }
    ]
  },
  {
    label: 'Sample 3: Non-Risk',
    text: 'Studied all night for the machine learning final exam, super tired but feeling good!',
    risk: 4.2,
    tier: 'Tier 1 — Low / Non-Risk',
    tokens: [
      { word: 'Studied', type: 'neg' }, { word: 'all', type: 'norm' }, { word: 'night', type: 'norm' },
      { word: 'for', type: 'norm' }, { word: 'the', type: 'norm' }, { word: 'machine', type: 'neg' },
      { word: 'learning', type: 'neg' }, { word: 'final', type: 'norm' }, { word: 'exam,', type: 'norm' },
      { word: 'super', type: 'neg' }, { word: 'tired', type: 'pos' }, { word: 'but', type: 'norm' },
      { word: 'feeling', type: 'neg' }, { word: 'good!', type: 'neg' }
    ]
  }
];

export default function LandingPage({ onEnter }) {
  const [activePreset, setActivePreset] = useState(0);
  const p = PRESETS[activePreset];

  return (
    <div className="landing-root">
      <style>{STYLES}</style>
      <div className="glow-orb glow-1" />
      <div className="glow-orb glow-2" />

      <div className="wrap">
        {/* Navigation Bar */}
        <header className="landing-nav">
          <div className="landing-brand">
            <div className="landing-brand-emblem">Ψ</div>
            <span>Explainable Mental Health Risk Detection</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '12px' }}>
            <button className="nav-enter-btn" onClick={onEnter}>
              Enter Live Dashboard <span>→</span>
            </button>
          </div>
        </header>

        {/* Hero Section */}
        <div className="hero">
          <div className="hero-grid">
            <div>
              <span className="eyebrow">MSc Data Science · Module 55-710603 · Group Project Walkthrough</span>
              <h1>Explainable Mental Health<br />Risk <em>Detection</em></h1>
              <p className="hero-sub">A transformer-based system that flags suicide-risk language in user-written text &mdash; built so every prediction can be checked, not just trusted.</p>
              <div className="cta-row">
                <button className="cta-btn" onClick={onEnter}>Enter the Live Dashboard →</button>
                <span className="cta-hint">Sandbox · Analytics · Fairness · Live Monitor</span>
              </div>
            </div>

            <div className="hero-visual-card">
              <img
                src="/hero_graphic.png"
                alt="AI Clinical Dashboard Visual"
                className="hero-graphic-img"
              />
              <div className="waveform-box">
                <Waveform />
                <div className="waveform-caption">
                  <span>Live monitor · risk trajectory</span>
                  <span>synthetic feed</span>
                </div>
              </div>
            </div>
          </div>

          <div className="byline">
            <span><strong>Shirisha Srirangam</strong> · C5057017</span>
            <span><strong>Vara Prasad Kurella</strong> · C5067650</span>
            <span><strong>Sai Krishna Samudrapu</strong> · C4060587</span>
            <span><strong>John Babu Thammisetti</strong> · C5050552</span>
            <span><strong>Raviteja Vibhuthi</strong> · C5060678</span>
          </div>
        </div>

        {/* Interactive SHAP Simulator Widget */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Interactive Demo</span>
            <h2>Live SHAP Token Attribution Simulator</h2>
            <p className="lede">Test how the explainability engine highlights positive risk tokens (red) vs protective/neutral words (green) in real-time.</p>
          </div>
          <div className="simulator-card">
            <div className="sim-presets">
              {PRESETS.map((item, idx) => (
                <button
                  key={idx}
                  className={`sim-preset-btn ${activePreset === idx ? 'active' : ''}`}
                  onClick={() => setActivePreset(idx)}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <div className="sim-display-grid">
              <div className="sim-textbox">
                {p.tokens.map((tok, i) => (
                  <span
                    key={i}
                    className={tok.type === 'pos' ? 'token-positive' : tok.type === 'neg' ? 'token-negative' : ''}
                  >
                    {tok.word}{' '}
                  </span>
                ))}
              </div>
              <div className="sim-results-panel">
                <div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Predicted Risk</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.6rem', fontWeight: 700, color: p.risk > 50 ? '#DC2626' : '#059669' }}>{p.risk}%</div>
                </div>
                <div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Assigned Protocol Tier</div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', fontWeight: 700, padding: '4px 10px', borderRadius: '4px', background: p.risk > 50 ? 'rgba(220,38,38,0.1)' : 'rgba(5,150,105,0.1)', color: p.risk > 50 ? '#DC2626' : '#059669', border: `1px solid ${p.risk > 50 ? 'rgba(220,38,38,0.3)' : 'rgba(5,150,105,0.3)'}` }}>
                    {p.tier}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 1: The problem */}
        <section>
          <div className="section-head">
            <span className="eyebrow">The problem</span>
            <h2>Distress is written down long before anyone asks for help.</h2>
            <p className="lede">Reddit, forums, and social posts carry linguistic signals of psychological distress and suicidal ideation well before a person reaches a counsellor. Moderators and mental-health services can't read everything by hand. An automated first pass is only useful if it's honest about its own limits &mdash; this project is a decision-support tool, not a diagnosis, and it's built to show its reasoning at every step rather than hide behind a single confidence number.</p>
          </div>

          <div className="pillars">
            <div className="pillar">
              <span className="tag">Model</span>
              <p>BERT and RoBERTa fine-tuned on Reddit crisis language, benchmarked against TF-IDF + Logistic Regression / SVM baselines.</p>
              <span className="stat">97.68% F1</span>
            </div>
            <div className="pillar">
              <span className="tag">Explainability</span>
              <p>Every prediction ships with a reason &mdash; SHAP, LIME, or leave-one-out word attribution, selectable per request, not fixed at training time.</p>
              <span className="stat">3 attribution methods</span>
            </div>
            <div className="pillar">
              <span className="tag">Robustness</span>
              <p>Stress-tested against typo injection and distracting text, not just a clean held-out benchmark.</p>
              <span className="stat">&minus;1.8pt F1 under typos</span>
            </div>
            <div className="pillar">
              <span className="tag">Ethics</span>
              <p>PII scrubbed before any model sees the text; bias checked with bootstrapped confidence intervals, not a single pass/fail score.</p>
              <span className="stat">96 audited scenarios</span>
            </div>
          </div>
        </section>

        {/* Section 2: Proposal vs. delivery */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Proposal vs. delivery</span>
            <h2>What was scoped, and what actually shipped.</h2>
            <p className="lede">The original proposal called for a Streamlit interface with SHAP explanations over fine-tuned transformers. What's running today is a full FastAPI + React system that goes further in every one of its four stated pillars.</p>
          </div>

          <div className="scope-table-wrap">
            <table className="scope-table">
              <thead>
                <tr><th>Pillar</th><th>Proposed</th><th>Delivered</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td>Interface</td>
                  <td className="proposed">Streamlit input box + prediction</td>
                  <td className="delivered">FastAPI backend, React SPA with 7 working dashboards (Sandbox, Analytics, Fairness, Temporal, Live Monitor, What-If, Case Search)</td>
                </tr>
                <tr>
                  <td>Explainability</td>
                  <td className="proposed">SHAP word importance</td>
                  <td className="delivered">SHAP, LIME, and leave-one-out attribution, selectable per analysis, plus temperature-scaled calibration (ECE reduced from 0.061 to 0.008 on Logistic Regression)</td>
                </tr>
                <tr>
                  <td>Evaluation</td>
                  <td className="proposed">Accuracy / precision / recall / F1, confusion matrix</td>
                  <td className="delivered">Same, plus perturbation robustness testing and a construct-validity audit checking the model isn't just detecting generic sadness</td>
                </tr>
                <tr>
                  <td>Ethics</td>
                  <td className="proposed">Discussion of dataset bias and fairness in the written report</td>
                  <td className="delivered">A running fairness audit: 96 parallel scenarios across 3 linguistic registers, bootstrapped 95% confidence intervals, minimum-subgroup-size gating</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="beyond-list">
            <h3>Built beyond the original scope</h3>
            <ul>
              <li>Cognitive distortion tagging against the Beck/Burns CBT taxonomy</li>
              <li>Energy-based out-of-distribution detection (Liu et al., 2020)</li>
              <li>MC-Dropout predictive uncertainty on every transformer inference</li>
              <li>Live monitor with per-user escalation-trend and change-point detection</li>
              <li>Clinical safety copilot: triage priority, HIPAA-style audit hash, protocol dispatch (simulated)</li>
              <li>Structured request logging and async request handling end-to-end</li>
            </ul>
          </div>
        </section>

        {/* Section 3: Dataset */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Dataset</span>
            <h2>232,074 Reddit posts &mdash; balanced at the source, not just by us.</h2>
            <p className="lede">Kaggle's <a href="https://www.kaggle.com/datasets/nikhileshwarakomati/suicide-watch" target="_blank" rel="noopener noreferrer">Suicide Watch dataset</a> pairs r/SuicideWatch posts with a matched set of non-crisis posts, pre-balanced 116,037 to 116,037. We subsample to 15,000 posts for iteration speed, and every split &mdash; train, validation, test &mdash; stays perfectly class-balanced by construction, not by chance.</p>
          </div>

          <div className="dataset-grid">
            <div className="dataset-stat">
              <span className="num">232,074</span>
              <span className="label">raw posts available (Kaggle)</span>
            </div>
            <div className="dataset-stat">
              <span className="num">15,000</span>
              <span className="label">stratified subsample used</span>
            </div>
            <div className="dataset-stat">
              <span className="num">10,500 / 2,250 / 2,250</span>
              <span className="label">train / val / test (70 / 15 / 15)</span>
            </div>
            <div className="dataset-stat">
              <span className="num">131</span>
              <span className="label">avg. words per cleaned post</span>
            </div>
          </div>

          <p className="dataset-note"><strong>No synthetic fallback.</strong> If the raw CSV isn't present, preprocessing raises an error instead of generating fake training data &mdash; a deliberate constraint. PII is masked before the text is lowercased or tokenized, so anonymization runs against the original casing, not a normalized copy of it.</p>
        </section>

        {/* Section 4: Evaluation */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Evaluation</span>
            <h2>Test-set performance, all four models.</h2>
            <p className="lede">2,250 held-out Reddit posts, stratified train/val/test split. ECE is measured after temperature scaling, fitted on validation predictions only.</p>
          </div>

          <div className="table-scroll">
            <table className="metrics">
              <thead>
                <tr><th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>ECE (post-cal.)</th></tr>
              </thead>
              <tbody>
                <tr><td>Logistic Regression</td><td>91.38%</td><td>93.14%</td><td>89.33%</td><td>91.20%</td><td>0.0075</td></tr>
                <tr><td>SVM (Calibrated LinearSVC)</td><td>91.91%</td><td>92.67%</td><td>91.02%</td><td>91.84%</td><td>0.0064</td></tr>
                <tr><td>BERT (fine-tuned)</td><td className="hero-num">97.69%</td><td>98.12%</td><td>97.24%</td><td className="hero-num">97.68%</td><td>0.0065</td></tr>
                <tr><td>RoBERTa (fine-tuned)</td><td>97.64%</td><td>97.60%</td><td>97.69%</td><td>97.65%</td><td>0.0067</td></tr>
              </tbody>
            </table>
          </div>
          <p className="table-note">Under typo injection, BERT's F1 holds at 95.85% (&minus;1.83pt); under distracting appended text, 97.37% (&minus;0.31pt). Both transformers degrade less than either baseline under the same perturbations.</p>
        </section>

        {/* Section 5: Construct validity */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Construct validity</span>
            <h2>Is it detecting risk, or just sadness?</h2>
            <p className="lede">A model can look accurate while actually keying on generic negative sentiment rather than suicide-specific language &mdash; a known failure mode in mental-health NLP (Dehghan &amp; Ashrafi, 2026). We regress each model's output on a generic-negativity lexicon score and check whether the residual &mdash; what negativity can't explain &mdash; still predicts the true label.</p>
          </div>

          <div className="cv-panel">
            <div className="cv-bars">
              <div className="cv-row">
                <span>Logistic Reg.</span>
                <div className="cv-track"><div className="cv-fill" style={{ width: '87.3%' }} /></div>
                <span className="cv-val">0.873</span>
              </div>
              <div className="cv-row">
                <span>SVM</span>
                <div className="cv-track"><div className="cv-fill" style={{ width: '87.4%' }} /></div>
                <span className="cv-val">0.874</span>
              </div>
              <div className="cv-row">
                <span>BERT</span>
                <div className="cv-track"><div className="cv-fill" style={{ width: '98.1%' }} /></div>
                <span className="cv-val">0.981</span>
              </div>
              <div className="cv-row">
                <span>RoBERTa</span>
                <div className="cv-track"><div className="cv-fill" style={{ width: '97.5%' }} /></div>
                <span className="cv-val">0.975</span>
              </div>
            </div>
            <div>
              <p style={{ fontSize: '0.9rem', opacity: 0.9, margin: '0 0 10px', lineHeight: 1.6 }}>
                <strong>Residual&ndash;label correlation</strong> after the negativity confound is regressed out. All four models sit at 0.87&ndash;0.98 &mdash; generic negativity explains under 2.3% of any model's output variance (R&sup2; 0.018&ndash;0.023). The signal driving these predictions is specific to crisis language, not just tone.
              </p>
            </div>
          </div>
        </section>

        {/* Section 6: Fairness audit */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Fairness audit</span>
            <h2>An honest gap, not yet a proven one.</h2>
            <p className="lede">16 real crisis and non-crisis scenarios, each written in three registers &mdash; youth slang, formal language, and literal/direct phrasing &mdash; so the audit compares identical situations, not unrelated sentences. Logistic Regression, bootstrapped 95% confidence intervals, n=1000 resamples.</p>
          </div>

          <div className="cohort-grid">
            <div className="cohort-card">
              <div className="name">Youth slang</div>
              <div className="recall">56.2%</div>
              <div className="recall-label">recall on true-risk posts</div>
            </div>
            <div className="cohort-card">
              <div className="name">Formal language</div>
              <div className="recall">68.8%</div>
              <div className="recall-label">recall on true-risk posts</div>
            </div>
            <div className="cohort-card">
              <div className="name">Literal / direct</div>
              <div className="recall">87.5%</div>
              <div className="recall-label">recall on true-risk posts</div>
            </div>
          </div>

          <div className="fairness-finding">
            <div className="fairness-finding-header">
              <h4>
                <span>🛡️</span> What the audit actually says
              </h4>
              <span className="fairness-badge">Subgroup Size Gating Active</span>
            </div>
            <p>
              The baseline model misses more real crisis posts when they're phrased in slang or formal register than when they're stated literally &mdash; a real and concerning-looking spread. But each register only has <span className="audit-highlight">16 true-risk examples</span> in this scenario set, below the audit's own minimum-subgroup-size <span className="audit-highlight">threshold of 30</span> &mdash; so the system correctly declines to certify this recall gap as statistically significant rather than reporting it as fact. (Accuracy, which does clear the threshold at n=32 per cohort, shows <span className="audit-highlight-green">zero significant cross-cohort gaps</span> at 95% CI.)
            </p>
            <p>
              That's the audit working as designed &mdash; it surfaces the concern and refuses to overstate it. The fix isn't a different model, it's a larger register-balanced cohort, which is the direct next step for this evaluation.
            </p>
          </div>
        </section>

        {/* Section 7: Limitations & next steps */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Limitations &amp; next steps</span>
            <h2>What's still open.</h2>
            <p className="lede">Listed here on purpose &mdash; the same honesty this system asks of its own audits.</p>
          </div>
          <ul className="limitations-list">
            <li>The fairness cohort (16 scenarios &times; 3 registers) needs to grow before the recall gap across linguistic registers moves from suggestive to provable at 95% confidence.</li>
            <li>The Temporal Trend tab still scores a fixed 4-post demo timeline rather than a user's real logged history &mdash; the Live Monitor's escalation-trend engine already does this correctly for live data; extending it to Temporal is mostly plumbing.</li>
            <li>Out-of-distribution detection and MC-Dropout uncertainty are transformer-only; the TF-IDF baselines don't have an architecturally faithful equivalent yet.</li>
            <li>The Clinical Copilot's protocol dispatch is fully simulated &mdash; no real integration with a crisis line, a supervisor queue, or an audit-log database.</li>
          </ul>
        </section>

        {/* Section 8: Scope & safeguards */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Scope &amp; safeguards</span>
            <h2>What this system is, and isn't.</h2>
          </div>
          <div className="ethics-grid">
            <div className="ethics-card">
              <span className="tag">Not a diagnosis</span>
              <p>This is a research decision-support tool for triage and moderation workflows. It does not replace a clinician, a crisis line, or a trained human reviewer.</p>
            </div>
            <div className="ethics-card">
              <span className="tag">Privacy first</span>
              <p>Names, emails, phone numbers, usernames, and subreddit handles are masked before any model &mdash; baseline or transformer &mdash; ever sees the text.</p>
            </div>
            <div className="ethics-card">
              <span className="tag">Uncertainty, surfaced</span>
              <p>Transformer predictions carry an out-of-distribution energy score and MC-Dropout uncertainty, so "I don't know" is a state the system can actually express.</p>
            </div>
          </div>
          <div className="crisis-note">
            <span className="num">988</span>
            <span>Suicide &amp; Crisis Lifeline (call or text, US) &mdash; the number this system surfaces to a human operator at every severity tier above the lowest.</span>
          </div>
        </section>

        {/* Section 9: Architecture */}
        <section>
          <div className="section-head">
            <span className="eyebrow">Architecture</span>
            <h2>What's actually running.</h2>
          </div>
          <div className="arch-row">
            <div className="arch-col">
              <span className="tag">Backend</span>
              <ul>
                <li>FastAPI, fully async request handling</li>
                <li>Blocking model inference offloaded via thread pool</li>
                <li>Structured logging with per-request correlation IDs</li>
                <li>SQLite persistence for case history &amp; monitor events</li>
              </ul>
            </div>
            <div className="arch-col">
              <span className="tag">Modelling</span>
              <ul>
                <li>Cosine LR schedule with warmup, mixed precision, EMA weights</li>
                <li>Checkpoint selection by validation F1, not accuracy</li>
                <li>Temperature scaling fit on validation, never test</li>
              </ul>
            </div>
            <div className="arch-col">
              <span className="tag">Frontend</span>
              <ul>
                <li>React SPA, code-split per tab</li>
                <li>Live risk feed over WebSocket</li>
                <li>Command palette, light/dark theming</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer>
          <div className="footer-row">
            <div className="footer-team">
              Shirisha Srirangam · C5057017<br />
              Vara Prasad Kurella · C5067650<br />
              Sai Krishna Samudrapu · C4060587<br />
              John Babu Thammisetti · C5050552<br />
              Raviteja Vibhuthi · C5060678
            </div>
            <div className="footer-disclaimer">Advanced Artificial Intelligence Projects in Data Science (55-710603). Research prototype &mdash; not a clinical instrument.</div>
          </div>
        </footer>
      </div>
    </div>
  );
}
