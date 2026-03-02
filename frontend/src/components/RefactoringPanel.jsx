import React from 'react';

const icons = {
    extract_method: '✂️', reduce_nesting: '📐', reduce_parameters: '📦',
    documentation: '📝', line_length: '📏', extract_constant: '🔤',
    dead_code: '💀', duplication: '📋', simplify_condition: '🔀',
    god_function: '👹', long_param_list: '📜', feature_envy: '👀',
    global_state: '🌍', wildcard_import: '⭐', boolean_param: '🔘',
    unreachable_code: '🚫', long_chain: '🔗',
};

export default function RefactoringPanel({ suggestions, smells }) {
    const items = [
        ...(suggestions || []).map(s => ({ ...s, type: 'refactor' })),
        ...(smells || []).map(s => ({ ...s, type: 'smell', category: s.smell_type })),
    ];

    if (items.length === 0) {
        return (
            <div className="glass-card p-5 glow-green">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.15)' }}>
                        <span className="text-xl">✨</span>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-emerald-300">Clean Code</p>
                        <p className="text-[11px]" style={{ color: 'var(--text-dim)' }}>No refactoring needed</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {items.map((item, i) => (
                <div key={i} className="glass-card p-3.5 animate-fade-in group"
                    style={{ animationDelay: `${i * 30}ms`, animationFillMode: 'backwards' }}>
                    <div className="flex items-start gap-2.5">
                        <span className="text-base mt-0.5 flex-shrink-0">{icons[item.category] || '💡'}</span>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{item.message}</p>
                            {item.suggestion && (
                                <div className="mt-2 p-2 rounded-lg text-[11px]"
                                    style={{ background: 'rgba(124,58,237,0.05)', border: '1px solid rgba(124,58,237,0.1)', color: '#C4B5FD' }}>
                                    💡 {item.suggestion}
                                </div>
                            )}
                            <div className="flex items-center gap-2 mt-2">
                                {item.line && <span className="text-[10px] font-mono" style={{ color: 'var(--text-dim)' }}>Line {item.line}</span>}
                                <span className={`badge text-[9px] ${item.type === 'smell' ? 'badge-high' : 'badge-medium'}`}>
                                    {item.type}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
