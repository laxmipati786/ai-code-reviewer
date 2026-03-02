import React, { useState, useEffect } from 'react';
import MetricsChart from './MetricsChart';
import ComplexityChart from './ComplexityChart';
import SecurityPanel from './SecurityPanel';
import RefactoringPanel from './RefactoringPanel';

/* ── Animated Score Ring ── */
function ScoreRing({ score, label, size = 88 }) {
    const [animatedScore, setAnimatedScore] = useState(0);
    const radius = (size - 10) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (animatedScore / 100) * circumference;
    const color = animatedScore >= 80 ? '#22C55E' : animatedScore >= 60 ? '#F59E0B' : animatedScore >= 40 ? '#F97316' : '#EF4444';

    useEffect(() => {
        setAnimatedScore(0);
        const timer = setTimeout(() => setAnimatedScore(score), 100);
        return () => clearTimeout(timer);
    }, [score]);

    return (
        <div className="flex flex-col items-center gap-1.5">
            <div className="score-ring-container" style={{ width: size, height: size }}>
                <svg width={size} height={size} className="transform -rotate-90">
                    <circle cx={size / 2} cy={size / 2} r={radius} fill="transparent" stroke="rgba(255,255,255,0.03)" strokeWidth="5" />
                    <circle cx={size / 2} cy={size / 2} r={radius} fill="transparent" stroke={color} strokeWidth="5"
                        strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
                        style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s ease', filter: `drop-shadow(0 0 6px ${color}50)` }} />
                </svg>
                <div className="score-ring-label">
                    <span className="text-xl font-bold font-mono" style={{ color }}>{Math.round(animatedScore)}</span>
                </div>
            </div>
            <span className="text-[10px] font-medium" style={{ color: 'var(--text-dim)' }}>{label}</span>
        </div>
    );
}

/* ── Stat Card ── */
function StatCard({ icon, value, label, color = '#7C3AED' }) {
    return (
        <div className="glass-card p-3 text-center group cursor-default">
            <div className="text-lg mb-0.5" style={{ filter: `drop-shadow(0 0 4px ${color}40)` }}>{icon}</div>
            <div className="text-base font-bold font-mono" style={{ color: 'var(--text-primary)' }}>{value}</div>
            <div className="text-[10px] font-medium" style={{ color: 'var(--text-dim)' }}>{label}</div>
        </div>
    );
}

export default function AnalysisPanel({ results, forcedTab }) {
    const [activeTab, setActiveTab] = useState('overview');

    // Sync tab when sidebar forces a specific view
    useEffect(() => {
        if (forcedTab && ['overview', 'issues', 'security', 'refactor'].includes(forcedTab)) {
            setActiveTab(forcedTab);
        }
    }, [forcedTab]);

    if (!results) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center animate-fade-in px-8">
                    <div className="w-20 h-20 mx-auto mb-5 rounded-2xl flex items-center justify-center"
                        style={{ background: 'rgba(124,58,237,0.06)', border: '1px solid rgba(124,58,237,0.1)' }}>
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" strokeWidth="1.5" strokeLinecap="round" opacity="0.5">
                            <path d="M16 18l6-6-6-6" /><path d="M8 6l-6 6 6 6" />
                        </svg>
                    </div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                        Paste code and click <span className="gradient-text font-semibold">Analyze</span>
                    </p>
                    <p className="text-xs mt-1.5" style={{ color: 'var(--text-dim)' }}>
                        13 analysis dimensions • Real-time feedback
                    </p>
                    <div className="flex flex-wrap justify-center gap-1.5 mt-4">
                        {['Syntax', 'Complexity', 'Security', 'Quality', 'Similarity'].map(t => (
                            <span key={t} className="text-[10px] font-medium px-2 py-0.5 rounded-full"
                                style={{ background: 'rgba(124,58,237,0.05)', color: 'var(--text-dim)', border: '1px solid var(--border-subtle)' }}>
                                {t}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    const tabs = [
        { id: 'overview', label: '📊 Overview' },
        { id: 'issues', label: `⚠️ Issues (${(results.syntax_errors?.length || 0) + (results.logical_warnings?.length || 0)})` },
        { id: 'security', label: `🛡️ Security (${results.security_issues?.length || 0})` },
        { id: 'refactor', label: `🔧 Refactor (${(results.refactoring_suggestions?.length || 0) + (results.code_smells?.length || 0)})` },
    ];

    return (
        <div className="h-full flex flex-col overflow-hidden">
            {/* Tab bar */}
            <div className="flex items-center gap-1 px-4 py-2 overflow-x-auto flex-shrink-0"
                style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                {tabs.map(tab => (
                    <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`tab ${activeTab === tab.id ? 'active' : ''}`}>
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {activeTab === 'overview' && (
                    <div className="space-y-4 animate-fade-in">
                        {/* AI Explanation */}
                        {results.ai_explanation && (
                            <div className="glass-card p-4" style={{ borderColor: 'rgba(124,58,237,0.12)' }}>
                                <div className="flex items-start gap-3">
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                                        style={{ background: 'rgba(124,58,237,0.1)' }}>
                                        <span className="text-sm">🤖</span>
                                    </div>
                                    <div>
                                        <p className="text-[11px] font-semibold mb-1" style={{ color: '#C4B5FD' }}>AI Analysis</p>
                                        <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{results.ai_explanation}</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Score Rings */}
                        <div className="grid grid-cols-3 gap-3">
                            <div className="glass-card p-4 flex flex-col items-center glow-purple">
                                <ScoreRing score={results.clean_code_score} label="Clean Code" />
                            </div>
                            <div className="glass-card p-4 flex flex-col items-center glow-cyan">
                                <ScoreRing score={results.maintainability_index} label="Maintainability" />
                            </div>
                            <div className="glass-card p-4 flex flex-col items-center glow-green">
                                <ScoreRing score={results.readability_score} label="Readability" />
                            </div>
                        </div>

                        {/* Stats Row */}
                        <div className="grid grid-cols-4 gap-2">
                            <StatCard icon="📄" value={results.loc} label="Lines" color="#6366F1" />
                            <StatCard icon="⚡" value={results.function_count} label="Functions" color="#06B6D4" />
                            <StatCard icon="💬" value={`${Math.round(results.comment_ratio * 100)}%`} label="Comments" color="#22C55E" />
                            <StatCard icon="🔄" value={`${results.similarity_score}%`} label="Similarity" color="#F59E0B" />
                        </div>

                        <MetricsChart results={results} />
                        <ComplexityChart results={results} />

                        {/* Performance Alerts */}
                        {results.performance_alerts?.length > 0 && (
                            <div className="space-y-2">
                                <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-dim)' }}>
                                    🚨 Performance Risks
                                </h3>
                                {results.performance_alerts.map((alert, i) => (
                                    <div key={i} className="glass-card p-3 animate-fade-in" style={{ animationDelay: `${i * 40}ms`, animationFillMode: 'backwards' }}>
                                        <div className="flex items-start gap-2">
                                            <span className={`badge text-[10px] badge-${alert.risk_level === 'high' ? 'critical' : alert.risk_level}`}>{alert.risk_level}</span>
                                            <div>
                                                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{alert.message}</p>
                                                {alert.line && <span className="text-[10px] font-mono" style={{ color: 'var(--text-dim)' }}>Line {alert.line}</span>}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'issues' && (
                    <div className="space-y-3 animate-fade-in">
                        {/* Syntax Errors */}
                        <div>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 flex items-center gap-2" style={{ color: 'var(--text-dim)' }}>
                                Syntax Errors
                                {results.syntax_errors.length === 0 && <span className="badge badge-low text-[9px]">✓ Clean</span>}
                            </h3>
                            {results.syntax_errors.length > 0 ? (
                                <div className="space-y-1.5">
                                    {results.syntax_errors.map((err, i) => (
                                        <div key={i} className="glass-card p-3 text-xs" style={{ borderColor: 'rgba(239,68,68,0.15)' }}>
                                            <span className="font-mono font-bold text-red-400">L{err.line}:{err.column}</span>
                                            <span className="ml-2" style={{ color: 'var(--text-secondary)' }}>{err.message}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : null}
                        </div>

                        {/* Logical Warnings */}
                        <div>
                            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 flex items-center gap-2" style={{ color: 'var(--text-dim)' }}>
                                Logical Warnings
                                {results.logical_warnings.length === 0 && <span className="badge badge-low text-[9px]">✓ Clean</span>}
                            </h3>
                            {results.logical_warnings.length > 0 ? (
                                <div className="space-y-1.5">
                                    {results.logical_warnings.map((warn, i) => (
                                        <div key={i} className="glass-card p-3 text-xs animate-fade-in" style={{ animationDelay: `${i * 40}ms`, animationFillMode: 'backwards' }}>
                                            {warn.line && <span className="font-mono font-bold text-amber-400">L{warn.line} </span>}
                                            <span className={`badge text-[9px] mr-1.5 badge-info`}>{warn.category}</span>
                                            <span style={{ color: 'var(--text-secondary)' }}>{warn.message}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : null}
                        </div>
                    </div>
                )}

                {activeTab === 'security' && (
                    <div className="animate-fade-in">
                        <SecurityPanel issues={results.security_issues} />
                    </div>
                )}

                {activeTab === 'refactor' && (
                    <div className="animate-fade-in">
                        <RefactoringPanel suggestions={results.refactoring_suggestions} smells={results.code_smells} />
                    </div>
                )}
            </div>
        </div>
    );
}
