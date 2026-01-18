"use client";
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/shared/Button';
import { API_BASE_URL } from '@/utils/api';

export default function TestPrepTab() {
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'chat' | 'quiz'>('chat');
  const [activeNoteInfo, setActiveNoteInfo] = useState<string | null>(null);
  const [currentQuiz, setCurrentQuiz] = useState<{question: string, options: Record<string,string>} | null>(null);

  // When switching to quiz mode, try to load an active quiz (if it exists)
  useEffect(() => {
    if (mode !== 'quiz') {
      setCurrentQuiz(null);
      return;
    }
    async function loadLatestQuiz() {
      try {
        const token = localStorage.getItem('token');
        console.debug('[TestPrep] loadLatestQuiz token:', !!token);
        if (!token) { setCurrentQuiz(null); return; }
        const url = `${API_BASE_URL}/rag/quiz/latest`;
        console.debug('[TestPrep] fetch', url);
        const res = await fetch(url, {
          headers: { Authorization: `Bearer ${token}` }
        });
        console.debug('[TestPrep] response status', res.status);
        if (!res.ok) {
          setCurrentQuiz(null);
          return;
        }
        const q = await res.json();
        console.debug('[TestPrep] quiz', q);
        setCurrentQuiz(q);
      } catch (e) {
        console.error('[TestPrep] loadLatestQuiz error', e);
        setCurrentQuiz(null);
      }
    }
    loadLatestQuiz();

    // Check AI health
    (async function fetchAIHealth(){
      try {
        const res = await fetch(`${API_BASE_URL}/ai/health`);
        const data = await res.json();
        console.debug('[TestPrep] AI health', data);
      } catch (e) {
        console.debug('[TestPrep] AI health error', e);
      }
    })();
  }, [mode]);
  // Check if there is an active master note to use as context
  useEffect(() => {
    async function checkActiveNote() {
      try {
        const token = localStorage.getItem('token');
        if (!token) { setActiveNoteInfo(null); return; }
        const res = await fetch(`${API_BASE_URL}/consensus/master/latest`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        console.debug('[TestPrep] checkActiveNote status', res.status);
        if (res.status === 204) {
            setActiveNoteInfo("No specific study guide selected. I'll use my general knowledge!");
        } else if (res.ok) {
            const data = await res.json();
            setActiveNoteInfo(`Using context from: ${data.topic}`);
        } else {
            setActiveNoteInfo("No specific study guide selected. I'll use my general knowledge!");
        }
      } catch (e) {
        setActiveNoteInfo(null);
      }
    }
    checkActiveNote();
  }, []);

  async function handleSend() {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/rag/tutor`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          subject_id: 0, 
          chapter: 0,
          question: userMsg,
          mode: mode
        })
      });
      const data = await res.json();
      const assistantText = data?.answer || "I'm sorry, I'm having a bit of a brain fog. Could you try asking that again?";
      setMessages(prev => [...prev, { role: 'assistant', content: assistantText }]);

      // If we're in quiz mode, try to refresh the active quiz (agent may have just generated one)
      if (mode === 'quiz') {
        try {
          const qres = await fetch(`${API_BASE_URL}/rag/quiz/latest`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
          });
          if (qres.ok) {
            const q = await qres.json();
            setCurrentQuiz(q);
          }
        } catch (e) {
          // ignore
        }
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I am having trouble connecting to my central knowledge right now. Please check your connection.' }]);
    } finally {
      setLoading(false);
    }
  }

  async function evaluateAnswer(choice: string) {
    // append user choice
    setMessages(prev => [...prev, { role: 'user', content: choice }]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/rag/tutor`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          subject_id: 0, 
          chapter: 0,
          question: choice,
          mode: 'quiz'
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data?.answer || "I couldn't evaluate that right now." }]);
      // After evaluation, clear current quiz so user can request another or generate a new one
      setCurrentQuiz(null);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error evaluating answer.' }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 h-[600px] flex flex-col">
      <div className="mb-4 flex items-center gap-3">
        <div className={`px-3 py-1 rounded-full text-sm cursor-pointer ${mode === 'chat' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`} onClick={() => setMode('chat')}>Chat</div>
        <div className={`px-3 py-1 rounded-full text-sm cursor-pointer ${mode === 'quiz' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`} onClick={() => setMode('quiz')}>Quiz</div>
        {activeNoteInfo && <div className="ml-auto text-xs italic text-gray-500">{activeNoteInfo}</div>}
      </div>

      {currentQuiz && (
        <div className="bg-white border rounded-md p-4 mb-4">
          <div className="font-medium mb-2">{currentQuiz.question}</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(currentQuiz.options).map(([k,v]) => (
              <button key={k} onClick={() => evaluateAnswer(k)} className="px-3 py-2 rounded bg-blue-50 hover:bg-blue-100 text-sm text-left">{k}) {v}</button>
            ))}
          </div>
        </div>
      )}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 border rounded-xl bg-gray-50/30">
        {messages.length === 0 && (
          <div className="text-gray-400 text-center mt-20 italic">
            Hi! I'm your HiveMind AI Tutor. <br/> 
            Tell me what subject and chapter you want to study, or ask me a question!
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-4 py-2 rounded-2xl ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              <p className="text-sm whitespace-pre-wrap">{m.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-2 rounded-2xl animate-pulse text-gray-400 text-sm">Thinking...</div>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input 
          className="flex-1 px-4 py-2 border rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g. Help me prep for Biology Chapter 8..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <Button onClick={handleSend} disabled={loading} className="rounded-full px-6">Send</Button>
      </div>
    </div>
  );
}
