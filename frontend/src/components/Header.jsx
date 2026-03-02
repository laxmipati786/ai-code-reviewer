import React from 'react';

const languages = [
    { value: 'python', label: 'Python', icon: '🐍' },
    { value: 'javascript', label: 'JavaScript', icon: '⚡' },
    { value: 'java', label: 'Java', icon: '☕' },
    { value: 'cpp', label: 'C++', icon: '⚙️' },
    { value: 'typescript', label: 'TypeScript', icon: '🔷' },
    { value: 'go', label: 'Go', icon: '🐹' },
];

export default function Header({ language, setLanguage, onAnalyze, isLoading, analysisTime }) {
    return (
        <header className="glass h-14 flex items-center justify-between px-5 sticky top-0 z-50"
            style={{ borderBottom: '1px solid var(--border-subtle)' }}>

            {/* Left: Branding */}
            <div className="flex items-center gap-3">
                <div>
                    <h1 className="text-sm font-bold tracking-tight gradient-text">AI Code Reviewer</h1>
                    <p className="text-[9px] font-medium tracking-[0.2em] uppercase" style={{ color: 'var(--text-dim)' }}>
                        Complexity Analyzer
                    </p>
                </div>
            </div>

            {/* Center: Language Selector */}
            <div className="navbar-center flex items-center gap-1 p-1 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)' }}>
                {languages.map(lang => (
                    <button
                        key={lang.value}
                        onClick={() => setLanguage(lang.value)}
                        className={`lang-pill ${language === lang.value ? 'active' : ''}`}
                    >
                        <span className="lang-icon text-sm">{lang.icon}</span>
                        <span className="hidden sm:inline">{lang.label}</span>
                    </button>
                ))}
            </div>

            {/* Right: Status + Analyze */}
            <div className="flex items-center gap-4">
                {analysisTime > 0 && (
                    <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-dim)' }}>
                        <div className="pulse-dot" style={{ background: 'var(--accent-green)' }}></div>
                        <span className="font-mono">{analysisTime.toFixed(0)}ms</span>
                    </div>
                )}

                <button
                    onClick={onAnalyze}
                    disabled={isLoading}
                    className="btn-primary flex items-center gap-2"
                    style={{ height: 40 }}
                >
                    {isLoading ? (
                        <>
                            <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}></div>
                            <span>Analyzing...</span>
                        </>
                    ) : (
                        <>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                                <polygon points="5 3 19 12 5 21 5 3" />
                            </svg>
                            <span>Analyze</span>
                        </>
                    )}
                </button>
            </div>
        </header>
    );
}
