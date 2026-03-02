import React from 'react';

export default function LoadingOverlay() {
    const steps = ['Parsing AST', 'Complexity', 'Security', 'Quality', 'Similarity'];

    return (
        <div className="absolute inset-0 z-40 flex items-center justify-center" style={{ background: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(8px)' }}>
            <div className="glass-card-static p-10 flex flex-col items-center gap-5 animate-fade-in" style={{ maxWidth: 340 }}>
                {/* Animated Logo */}
                <div className="relative">
                    <div className="spinner" style={{ width: 64, height: 64, borderWidth: 3, borderColor: 'rgba(124,58,237,0.1)', borderTopColor: '#7C3AED' }}></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" strokeWidth="2" strokeLinecap="round">
                            <path d="M16 18l6-6-6-6" /><path d="M8 6l-6 6 6 6" />
                        </svg>
                    </div>
                </div>

                <div className="text-center">
                    <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Analyzing Your Code</p>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-dim)' }}>Running 13 analysis dimensions...</p>
                </div>

                {/* Animated steps */}
                <div className="flex flex-wrap items-center justify-center gap-1.5">
                    {steps.map((step, i) => (
                        <span key={step} className="text-[10px] font-medium px-2.5 py-1 rounded-full animate-fade-in"
                            style={{
                                background: 'rgba(124,58,237,0.08)',
                                color: '#C4B5FD',
                                border: '1px solid rgba(124,58,237,0.15)',
                                animationDelay: `${i * 150}ms`,
                                animationFillMode: 'backwards'
                            }}>
                            {step}
                        </span>
                    ))}
                </div>

                {/* Progress bar */}
                <div className="w-full gauge-bar" style={{ height: 3 }}>
                    <div className="gauge-fill shimmer" style={{ width: '100%', background: 'var(--gradient-primary)' }}></div>
                </div>
            </div>
        </div>
    );
}
