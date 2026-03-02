import React, { useState } from 'react';

const navItems = [
    { id: 'editor', icon: '⌨️', label: 'Code Editor' },
    { id: 'overview', icon: '📊', label: 'Overview' },
    { id: 'security', icon: '🛡️', label: 'Security' },
    { id: 'refactor', icon: '🔧', label: 'Refactor' },
    { id: 'history', icon: '📋', label: 'History' },
];

export default function Sidebar({ activeView, setActiveView }) {
    const [hoveredId, setHoveredId] = useState(null);

    return (
        <aside
            className="sidebar flex-shrink-0 h-full border-r flex flex-col items-center py-4"
            style={{
                width: 68,
                borderColor: 'var(--border-subtle)',
                background: 'rgba(15, 23, 42, 0.95)',
            }}
        >
            {/* Logo */}
            <div
                className="flex items-center justify-center mb-6 cursor-pointer"
                style={{
                    width: 40, height: 40,
                    borderRadius: 12,
                    background: 'var(--gradient-primary)',
                    boxShadow: 'var(--glow-purple)',
                }}
            >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M16 18l6-6-6-6" /><path d="M8 6l-6 6 6 6" />
                </svg>
            </div>

            <div style={{ width: 32, height: 1, background: 'var(--border-subtle)', marginBottom: 12 }} />

            {/* Nav Items */}
            {navItems.map((item) => (
                <div
                    key={item.id}
                    style={{ position: 'relative', marginBottom: 4 }}
                    onMouseEnter={() => setHoveredId(item.id)}
                    onMouseLeave={() => setHoveredId(null)}
                >
                    <button
                        onClick={() => setActiveView(item.id)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 44,
                            height: 44,
                            borderRadius: 12,
                            cursor: 'pointer',
                            border: 'none',
                            fontSize: 20,
                            transition: 'all 0.2s',
                            background: activeView === item.id ? 'rgba(124, 58, 237, 0.15)' : 'transparent',
                            color: activeView === item.id ? '#C4B5FD' : '#64748B',
                            boxShadow: activeView === item.id ? '0 0 12px rgba(124, 58, 237, 0.15)' : 'none',
                        }}
                    >
                        <span>{item.icon}</span>
                    </button>

                    {/* Active indicator bar */}
                    {activeView === item.id && (
                        <div style={{
                            position: 'absolute',
                            left: -12,
                            top: '50%',
                            transform: 'translateY(-50%)',
                            width: 3,
                            height: 20,
                            borderRadius: '0 3px 3px 0',
                            background: '#7C3AED',
                            boxShadow: '0 0 8px rgba(124, 58, 237, 0.6)',
                        }} />
                    )}

                    {/* Tooltip */}
                    {hoveredId === item.id && (
                        <div style={{
                            position: 'absolute',
                            left: 54,
                            top: '50%',
                            transform: 'translateY(-50%)',
                            padding: '4px 10px',
                            borderRadius: 6,
                            fontSize: 11,
                            fontWeight: 500,
                            whiteSpace: 'nowrap',
                            background: '#1E293B',
                            color: '#94A3B8',
                            border: '1px solid rgba(255,255,255,0.06)',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
                            zIndex: 100,
                            pointerEvents: 'none',
                        }}>
                            {item.label}
                        </div>
                    )}
                </div>
            ))}

            {/* Bottom - Settings */}
            <div style={{ marginTop: 'auto' }}>
                <div style={{ width: 32, height: 1, background: 'var(--border-subtle)', marginBottom: 8, marginLeft: 6 }} />
                <div
                    style={{ position: 'relative' }}
                    onMouseEnter={() => setHoveredId('settings')}
                    onMouseLeave={() => setHoveredId(null)}
                >
                    <button
                        onClick={() => alert('Settings coming soon!')}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 44,
                            height: 44,
                            borderRadius: 12,
                            cursor: 'pointer',
                            border: 'none',
                            fontSize: 20,
                            transition: 'all 0.2s',
                            background: 'transparent',
                            color: '#64748B',
                        }}
                    >
                        <span>⚙️</span>
                    </button>
                    {hoveredId === 'settings' && (
                        <div style={{
                            position: 'absolute',
                            left: 54,
                            top: '50%',
                            transform: 'translateY(-50%)',
                            padding: '4px 10px',
                            borderRadius: 6,
                            fontSize: 11,
                            fontWeight: 500,
                            whiteSpace: 'nowrap',
                            background: '#1E293B',
                            color: '#94A3B8',
                            border: '1px solid rgba(255,255,255,0.06)',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
                            zIndex: 100,
                            pointerEvents: 'none',
                        }}>
                            Settings
                        </div>
                    )}
                </div>
            </div>
        </aside>
    );
}
