import React, { useState, useCallback, useMemo } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import CodeEditor, { defaultCode } from './components/CodeEditor';
import AnalysisPanel from './components/AnalysisPanel';
import LoadingOverlay from './components/LoadingOverlay';
import { analyzeCode } from './utils/api';

/* ── Particle Background ── */
function Particles() {
    const particles = useMemo(() =>
        Array.from({ length: 30 }, (_, i) => ({
            id: i,
            size: Math.random() * 3 + 1,
            x: Math.random() * 100,
            y: Math.random() * 100,
            delay: Math.random() * 8,
            duration: Math.random() * 6 + 6,
            color: ['#7C3AED', '#4F46E5', '#06B6D4', '#22C55E'][Math.floor(Math.random() * 4)],
        })), []);

    return (
        <div className="particles">
            {particles.map(p => (
                <div key={p.id} className="particle" style={{
                    width: p.size, height: p.size,
                    left: `${p.x}%`, top: `${p.y}%`,
                    background: p.color,
                    animationDelay: `${p.delay}s`,
                    animationDuration: `${p.duration}s`,
                    boxShadow: `0 0 ${p.size * 3}px ${p.color}40`,
                }} />
            ))}
        </div>
    );
}

export default function App() {
    const [language, setLanguage] = useState('python');
    const [code, setCode] = useState(defaultCode.python);
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [analysisTime, setAnalysisTime] = useState(0);
    const [activeView, setActiveView] = useState('editor');

    const handleLanguageChange = useCallback((lang) => {
        setLanguage(lang);
        if (!code.trim() || code === defaultCode[language]) {
            setCode(defaultCode[lang] || '');
        }
    }, [code, language]);

    const handleAnalyze = useCallback(async () => {
        if (!code.trim()) return;
        setIsLoading(true);
        setError(null);
        try {
            const data = await analyzeCode(code, language);
            setResults(data);
            setAnalysisTime(data.analysis_time_ms || 0);
            // Auto-switch to overview after analysis completes
            setActiveView('overview');
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Analysis failed. Is the backend running?');
        } finally {
            setIsLoading(false);
        }
    }, [code, language]);

    // Handle sidebar navigation - switch analysis tab when clicking sidebar items
    const handleViewChange = useCallback((view) => {
        setActiveView(view);
    }, []);

    // Map sidebar view to analysis panel tab
    const getAnalysisTab = () => {
        switch (activeView) {
            case 'overview': return 'overview';
            case 'security': return 'security';
            case 'refactor': return 'refactor';
            default: return null; // editor, history — don't force a tab
        }
    };

    // Determine panel visibility
    const showEditor = true; // Always show editor
    const showAnalysis = activeView !== 'editor' || results !== null;
    const analysisTab = getAnalysisTab();

    // Layout widths depend on active view
    const editorWidth = activeView === 'editor' && !results ? '100%' : '55%';
    const analysisWidth = '45%';

    return (
        <div className="h-screen flex flex-col noise-bg" style={{ background: 'var(--bg-primary)' }}>
            <Particles />

            <Header
                language={language}
                setLanguage={handleLanguageChange}
                onAnalyze={handleAnalyze}
                isLoading={isLoading}
                analysisTime={analysisTime}
            />

            {/* Error Banner */}
            {error && (
                <div className="mx-4 mt-2 p-3 rounded-xl flex items-center gap-3 animate-slide-up z-10"
                    style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)' }}>
                    <span className="text-red-400 text-sm">⚠️</span>
                    <span className="text-xs flex-1" style={{ color: '#FCA5A5' }}>{error}</span>
                    <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300 text-sm transition-colors">✕</button>
                </div>
            )}

            {/* Main Layout: Sidebar + Editor + Analysis */}
            <div className="flex-1 flex overflow-hidden relative z-10 main-layout">
                <Sidebar activeView={activeView} setActiveView={handleViewChange} />

                {isLoading && <LoadingOverlay />}

                {/* Editor Panel */}
                <div className="editor-panel flex flex-col p-3 transition-all duration-300" style={{ width: editorWidth }}>
                    <CodeEditor code={code} setCode={setCode} language={language} />
                </div>

                {/* Analysis Panel - shows when we have results or user navigated to a view */}
                {showAnalysis && (
                    <div className="analysis-panel flex flex-col animate-fade-in transition-all duration-300"
                        style={{ width: analysisWidth, borderLeft: '1px solid var(--border-subtle)', background: 'rgba(17, 24, 39, 0.5)' }}>
                        <AnalysisPanel results={results} forcedTab={analysisTab} />
                    </div>
                )}
            </div>

            {/* Status Bar */}
            <footer className="glass flex items-center justify-between px-5 py-1.5 z-10 flex-shrink-0"
                style={{ borderTop: '1px solid var(--border-subtle)' }}>
                <div className="flex items-center gap-3 text-[10px] font-medium" style={{ color: 'var(--text-dim)' }}>
                    <span className="flex items-center gap-1.5">
                        <span className="pulse-dot" style={{ background: 'var(--accent-green)', width: 5, height: 5 }}></span>
                        Ready
                    </span>
                    <span style={{ color: 'var(--border-subtle)' }}>|</span>
                    <span>{language.charAt(0).toUpperCase() + language.slice(1)}</span>
                    <span style={{ color: 'var(--border-subtle)' }}>|</span>
                    <span>{code.split('\n').length} lines</span>
                    <span style={{ color: 'var(--border-subtle)' }}>|</span>
                    <span className="font-mono">{new Blob([code]).size} bytes</span>
                </div>
                <div className="flex items-center gap-3 text-[10px] font-medium" style={{ color: 'var(--text-dim)' }}>
                    <span>AI Code Reviewer v1.0</span>
                    <span className="px-1.5 py-0.5 rounded-md" style={{ background: 'rgba(124,58,237,0.06)', color: '#C4B5FD' }}>
                        13 Dimensions
                    </span>
                </div>
            </footer>
        </div>
    );
}
