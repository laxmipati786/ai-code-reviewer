import React from 'react';

export default function SecurityPanel({ issues }) {
    if (!issues || issues.length === 0) {
        return (
            <div className="glass-card p-5 glow-green">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.15)' }}>
                        <span className="text-xl">✓</span>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-emerald-300">All Clear</p>
                        <p className="text-[11px]" style={{ color: 'var(--text-dim)' }}>No security vulnerabilities detected</p>
                    </div>
                </div>
            </div>
        );
    }

    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    const sorted = [...issues].sort((a, b) => (severityOrder[a.severity] || 3) - (severityOrder[b.severity] || 3));
    const counts = { critical: 0, high: 0, medium: 0, low: 0 };
    issues.forEach(i => { counts[i.severity] = (counts[i.severity] || 0) + 1; });

    return (
        <div className="space-y-3">
            {/* Summary bar */}
            <div className="flex items-center gap-2">
                {Object.entries(counts).filter(([, v]) => v > 0).map(([sev, count]) => (
                    <span key={sev} className={`badge badge-${sev}`}>{count} {sev}</span>
                ))}
            </div>

            {/* Issues list */}
            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                {sorted.map((issue, i) => (
                    <div key={i} className="glass-card p-3 animate-fade-in"
                        style={{
                            animationDelay: `${i * 40}ms`, animationFillMode: 'backwards',
                            borderColor: issue.severity === 'critical' ? 'rgba(239,68,68,0.15)' : issue.severity === 'high' ? 'rgba(245,158,11,0.15)' : 'var(--border-subtle)'
                        }}>
                        <div className="flex items-start gap-2.5">
                            <span className={`badge badge-${issue.severity} text-[10px] flex-shrink-0 mt-0.5`}>{issue.severity}</span>
                            <div className="flex-1 min-w-0">
                                <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{issue.message}</p>
                                <div className="flex items-center gap-3 mt-1.5">
                                    {issue.line && <span className="text-[10px] font-mono" style={{ color: 'var(--text-dim)' }}>Line {issue.line}</span>}
                                    {issue.cwe && <span className="text-[10px] font-mono" style={{ color: '#C4B5FD' }}>{issue.cwe}</span>}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
