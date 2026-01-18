"use client";
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/shared/Button';
import UploadPage from '@/app/upload/page'; // We can reuse the upload logic or make it a component

export default function MyNotesTab() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [subjectId, setSubjectId] = useState<number | null>(null);
  const [notes, setNotes] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/subjects/')
      .then(r => r.json())
      .then(setSubjects)
      .catch(() => setSubjects([]));
  }, []);

  useEffect(() => {
    if (subjectId) {
      loadNotes();
    }
  }, [subjectId]);

  async function loadNotes() {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`http://localhost:8000/notes/my?subject_id=${subjectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setNotes(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  // Group notes by chapter
  const groupedNotes = notes.reduce((acc: any, note: any) => {
    const ch = note.chapter || 'Unspecified';
    if (!acc[ch]) acc[ch] = [];
    acc[ch].push(note);
    return acc;
  }, {});

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-4 items-center">
          <label className="text-sm font-medium text-gray-700">Filter by Subject:</label>
          <select 
            className="px-3 py-2 border rounded-lg text-sm"
            value={subjectId ?? ''}
            onChange={(e) => setSubjectId(Number(e.target.value) || null)}
          >
            <option value="">Select Subject</option>
            {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <Button onClick={() => setIsUploading(!isUploading)} variant={isUploading ? 'outline' : 'primary'}>
          {isUploading ? 'Back to Notes' : 'Upload New Note'}
        </Button>
      </div>

      {isUploading ? (
        <div className="border rounded-xl p-4 bg-gray-50">
          <UploadPage />
        </div>
      ) : (
        <div className="space-y-8">
          {!subjectId && <p className="text-gray-500 text-center py-10">Please select a subject to view your notes.</p>}
          {subjectId && notes.length === 0 && !loading && <p className="text-gray-500 text-center py-10">No notes found for this subject.</p>}
          
          {Object.keys(groupedNotes).sort((a, b) => Number(a) - Number(b)).map(chapter => (
            <div key={chapter} className="border-l-4 border-blue-500 pl-4">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Chapter {chapter}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {groupedNotes[chapter].map((note: any) => (
                  <div key={note.id} className="p-4 border rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex justify-between text-xs text-gray-400 mb-2">
                      <span>ID: #{note.id}</span>
                      <span>{new Date(note.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="prose prose-sm max-w-none line-clamp-6 text-gray-700">
                      {note.content}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
