import React, { useEffect, useState } from 'react';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip } from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip);

export default function MetricsChart({ results }) {
    const [animated, setAnimated] = useState(false);
    useEffect(() => { setAnimated(false); setTimeout(() => setAnimated(true), 100); }, [results]);

    if (!results) return null;

    const values = [
        results.clean_code_score,
        results.maintainability_index,
        results.readability_score,
        Math.max(0, 100 - results.security_issues.length * 20),
        Math.max(0, 100 - results.performance_alerts.length * 15),
        Math.max(0, 100 - (results.cyclomatic_complexity - 1) * 5),
    ];

    const data = {
        labels: ['Clean Code', 'Maintainability', 'Readability', 'Security', 'Performance', 'Simplicity'],
        datasets: [{
            label: 'Code Quality',
            data: animated ? values : [0, 0, 0, 0, 0, 0],
            backgroundColor: 'rgba(124, 58, 237, 0.08)',
            borderColor: 'rgba(124, 58, 237, 0.6)',
            borderWidth: 2,
            pointBackgroundColor: '#7C3AED',
            pointBorderColor: 'rgba(124, 58, 237, 0.3)',
            pointBorderWidth: 3,
            pointRadius: 4,
            pointHoverRadius: 7,
            pointHoverBackgroundColor: '#A78BFA',
            fill: true,
        }],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 1200, easing: 'easeOutQuart' },
        scales: {
            r: {
                beginAtZero: true,
                max: 100,
                ticks: { stepSize: 25, color: '#334155', backdropColor: 'transparent', font: { size: 9 } },
                grid: { color: 'rgba(255, 255, 255, 0.03)' },
                pointLabels: { color: '#64748B', font: { size: 10, family: 'Inter', weight: '500' } },
                angleLines: { color: 'rgba(255, 255, 255, 0.03)' },
            },
        },
        plugins: {
            tooltip: {
                backgroundColor: '#1E293B',
                titleColor: '#F1F5F9',
                bodyColor: '#94A3B8',
                borderColor: 'rgba(124, 58, 237, 0.2)',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 10,
                titleFont: { weight: '600' },
            },
        },
    };

    return (
        <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-dim)' }}>
                    Quality Radar
                </h3>
                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full" style={{ background: 'rgba(124,58,237,0.08)', color: '#C4B5FD' }}>
                    6 dimensions
                </span>
            </div>
            <div style={{ height: 240 }}>
                <Radar data={data} options={options} />
            </div>
        </div>
    );
}
