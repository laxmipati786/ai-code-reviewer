import React from 'react';

const levels = {
    'O(1)': { label: 'Constant', color: '#22C55E', width: 8, grade: 'A+' },
    'O(log n)': { label: 'Logarithmic', color: '#06B6D4', width: 20, grade: 'A' },
    'O(n)': { label: 'Linear', color: '#6366F1', width: 38, grade: 'B+' },
    'O(n log n)': { label: 'Linearithmic', color: '#8B5CF6', width: 52, grade: 'B' },
    'O(n²)': { label: 'Quadratic', color: '#F59E0B', width: 68, grade: 'C' },
    'O(n³)': { label: 'Cubic', color: '#F97316', width: 82, grade: 'D' },
    'O(2^n)': { label: 'Exponential', color: '#EF4444', width: 95, grade: 'F' },
};

export default function ComplexityChart({ results }) {
    if (!results) return null;
    const time = levels[results.time_complexity] || levels['O(n)'];
    const space = levels[results.space_complexity] || levels['O(1)'];

    const renderGauge = (label, complexity, info) => (
        <div className="glass-card p-4 glow-purple">
            <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-medium" style={{ color: 'var(--text-dim)' }}>{label}</span>
                <div className="flex items-center gap-2">
                    <span className="text-xs font-bold font-mono px-2 py-0.5 rounded-md" style={{ background: `${info.color}15`, color: info.color, border: `1px solid ${info.color}25` }}>
                        {complexity}
                    </span>
                </div>
            </div>
            <div className="gauge-bar mb-2">
                <div className="gauge-fill" style={{ width: `${info.width}%`, background: `linear-gradient(90deg, ${info.color}66, ${info.color})` }}></div>
            </div>
            <div className="flex items-center justify-between">
                <span className="text-[10px]" style={{ color: 'var(--text-dim)' }}>{info.label}</span>
                <span className="text-[10px] font-bold" style={{ color: info.color }}>Grade: {info.grade}</span>
            </div>
        </div>
    );

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-dim)' }}>
                    Complexity Analysis
                </h3>
            </div>
            {renderGauge('⏱ Time Complexity', results.time_complexity, time)}
            {renderGauge('💾 Space Complexity', results.space_complexity, space)}

            <div className="glass-card p-4">
                <div className="flex items-center justify-between">
                    <span className="text-[11px] font-medium" style={{ color: 'var(--text-dim)' }}>Cyclomatic Complexity</span>
                    <div className="flex items-center gap-2">
                        <span className={`text-sm font-bold font-mono ${results.cyclomatic_complexity > 20 ? 'text-red-400' : results.cyclomatic_complexity > 10 ? 'text-amber-400' : 'text-emerald-400'}`}>
                            {results.cyclomatic_complexity}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded-md" style={{
                            background: results.cyclomatic_complexity > 20 ? 'rgba(239,68,68,0.1)' : results.cyclomatic_complexity > 10 ? 'rgba(245,158,11,0.1)' : 'rgba(34,197,94,0.1)',
                            color: results.cyclomatic_complexity > 20 ? '#FCA5A5' : results.cyclomatic_complexity > 10 ? '#FCD34D' : '#86EFAC',
                        }}>
                            {results.cyclomatic_complexity > 20 ? 'Complex' : results.cyclomatic_complexity > 10 ? 'Moderate' : 'Simple'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
