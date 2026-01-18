"use client";
import React, { useState, useEffect } from 'react';
import { Input } from '@/components/shared/Input';
import { Button } from '@/components/shared/Button';
import { API_BASE_URL } from '@/utils/api';

export default function NotesPage() {
  const [subjects, setSubjects] = useState<Array<{id:number,name:string}>>([]);
  const [subjectId, setSubjectId] = useState<number | null>(null);
  const [notes, setNotes] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(()=>{
    fetch(`${API_BASE_URL}/subjects/`).then(r=>r.json()).then(setSubjects).catch(()=>setSubjects([]));
  },[]);

  async function loadNotes() {
    if (!subjectId) return setError('Select subject first');
    setError('');
    try{
      // Use token for current user
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE_URL}/notes/my?subject_id=${subjectId}`, { headers: { Authorization: 'Bearer ' + token } });
      if (!res.ok) {
        const d = await res.json();
        setError(d.detail || 'Failed to load notes');
        return;
      }
      const data = await res.json();
      // group by chapter
      const grouped: Record<string, any[]> = {};
      data.forEach((n: any) => {
        const ch = n.chapter ?? 'Unspecified';
        grouped[ch] = grouped[ch] || [];
        grouped[ch].push(n);
      });
      // sort chapters numerically (where possible)
      const chapters = Object.keys(grouped).sort((a,b)=>{
        if (a === 'Unspecified') return 1;
        if (b === 'Unspecified') return -1;
        return Number(a) - Number(b);
      });
      const ordered: any[] = [];
      chapters.forEach(c=>{ ordered.push({ chapter: c, notes: grouped[c] }) });
      setNotes(ordered);
    }catch(e){
      setError('Network error');
    }
  }

  return (
    <div className="max-w-3xl mx-auto bg-white p-6 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">My Notes</h2>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
        <select className="px-3 py-2 border rounded w-full" value={subjectId ?? ''} onChange={(e)=>setSubjectId(Number(e.target.value))}>
          <option value="">Choose subject</option>
          {subjects.map(s=> <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>
      <Button onClick={loadNotes} fullWidth>Load Notes</Button>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {notes.map(group=> (
        <div key={group.chapter} className="mt-6">
          <h3 className="font-semibold">Chapter: {group.chapter}</h3>
          <ul className="mt-2">
            {group.notes.map((n: any) => (
              <li key={n.id} className="p-3 border rounded mb-2">
                <div className="text-sm text-gray-500">Uploaded: {new Date(n.created_at).toLocaleString()}</div>
                <pre className="whitespace-pre-wrap mt-2 text-sm">{n.content}</pre>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
