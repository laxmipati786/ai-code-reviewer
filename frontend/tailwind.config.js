/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                dark: { 900: '#0F172A', 800: '#111827', 700: '#1E293B', 600: '#334155', 500: '#475569' },
            },
            fontFamily: {
                sans: ['Inter', '-apple-system', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
        },
    },
    plugins: [],
}
