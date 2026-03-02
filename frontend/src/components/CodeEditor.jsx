import React from 'react';
import Editor from '@monaco-editor/react';

const languageMap = { python: 'python', javascript: 'javascript', java: 'java', cpp: 'cpp', typescript: 'typescript', go: 'go' };

const defaultCode = {
    python: `# AI Code Reviewer — Paste your Python code here
def bubble_sort(arr):
    """Sort array using bubble sort algorithm."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def find_duplicates(lst):
    seen = set()
    duplicates = []
    for item in lst:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    return duplicates

# Example usage
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = bubble_sort(data)
print(f"Sorted: {sorted_data}")
`,
    javascript: `// AI Code Reviewer — Paste your JavaScript code here
function bubbleSort(arr) {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
      }
    }
  }
  return arr;
}

const data = [64, 34, 25, 12, 22, 11, 90];
console.log(bubbleSort(data));
`,
    java: `// AI Code Reviewer — Paste your Java code here
public class BubbleSort {
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
}
`,
    cpp: `// AI Code Reviewer — Paste your C++ code here
#include <iostream>
#include <vector>
using namespace std;

void bubbleSort(vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
}
`,
    typescript: `// AI Code Reviewer — Paste your TypeScript code here
function bubbleSort(arr: number[]): number[] {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
      }
    }
  }
  return arr;
}
`,
    go: `// AI Code Reviewer — Paste your Go code here
package main

import "fmt"

func bubbleSort(arr []int) []int {
    n := len(arr)
    for i := 0; i < n; i++ {
        for j := 0; j < n-i-1; j++ {
            if arr[j] > arr[j+1] {
                arr[j], arr[j+1] = arr[j+1], arr[j]
            }
        }
    }
    return arr
}

func main() {
    data := []int{64, 34, 25, 12, 22, 11, 90}
    fmt.Println(bubbleSort(data))
}
`,
};

const extMap = { python: 'py', javascript: 'js', java: 'java', cpp: 'cpp', typescript: 'ts', go: 'go' };

export default function CodeEditor({ code, setCode, language }) {
    return (
        <div className="h-full flex flex-col rounded-2xl overflow-hidden" style={{ border: '1px solid var(--border-subtle)', background: '#0c1222' }}>
            {/* Tab bar */}
            <div className="flex items-center justify-between px-4 py-2" style={{ borderBottom: '1px solid var(--border-subtle)', background: 'rgba(15, 23, 42, 0.95)' }}>
                <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full" style={{ background: '#EF4444' }}></div>
                        <div className="w-3 h-3 rounded-full" style={{ background: '#F59E0B' }}></div>
                        <div className="w-3 h-3 rounded-full" style={{ background: '#22C55E' }}></div>
                    </div>
                    <div className="flex items-center gap-1 px-3 py-1 rounded-lg" style={{ background: 'rgba(124, 58, 237, 0.08)', border: '1px solid rgba(124, 58, 237, 0.15)' }}>
                        <span className="text-[11px] font-mono font-medium" style={{ color: '#C4B5FD' }}>
                            main.{extMap[language] || 'py'}
                        </span>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button onClick={() => setCode(defaultCode[language] || '')}
                        className="text-[11px] font-medium px-2 py-0.5 rounded-md transition-colors"
                        style={{ color: 'var(--text-dim)' }}
                        onMouseOver={e => { e.target.style.color = '#C4B5FD'; e.target.style.background = 'rgba(124,58,237,0.08)'; }}
                        onMouseOut={e => { e.target.style.color = 'var(--text-dim)'; e.target.style.background = 'transparent'; }}>
                        Load Example
                    </button>
                    <button onClick={() => setCode('')}
                        className="text-[11px] font-medium px-2 py-0.5 rounded-md transition-colors"
                        style={{ color: 'var(--text-dim)' }}
                        onMouseOver={e => { e.target.style.color = '#FCA5A5'; e.target.style.background = 'rgba(239,68,68,0.08)'; }}
                        onMouseOut={e => { e.target.style.color = 'var(--text-dim)'; e.target.style.background = 'transparent'; }}>
                        Clear
                    </button>
                </div>
            </div>

            {/* Editor */}
            <div className="flex-1">
                <Editor
                    height="100%"
                    language={languageMap[language] || 'python'}
                    value={code}
                    onChange={(val) => setCode(val || '')}
                    onMount={(editor) => editor.focus()}
                    theme="vs-dark"
                    options={{
                        fontSize: 14,
                        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                        minimap: { enabled: true, maxColumn: 80, renderCharacters: false },
                        padding: { top: 16, bottom: 16 },
                        lineNumbers: 'on',
                        lineNumbersMinChars: 3,
                        renderLineHighlight: 'all',
                        renderLineHighlightOnlyWhenFocus: false,
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        bracketPairColorization: { enabled: true },
                        cursorBlinking: 'smooth',
                        cursorSmoothCaretAnimation: 'on',
                        smoothScrolling: true,
                        wordWrap: 'on',
                        tabSize: 4,
                        glyphMargin: false,
                        folding: true,
                        lineDecorationsWidth: 8,
                    }}
                />
            </div>
        </div>
    );
}

export { defaultCode };
