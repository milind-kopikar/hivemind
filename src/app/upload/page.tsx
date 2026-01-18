"use client";
import React, { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/shared/Button';
import { API_BASE_URL } from '@/utils/api';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Create object URL for preview when an image file is selected
  React.useEffect(()=>{
    if (!file) {
      setFilePreview(null);
      return;
    }
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setFilePreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setFilePreview(null);
    }
  }, [file]);

  const [subjects, setSubjects] = useState<Array<{id:number,name:string}>>([]);
  const [newSubject, setNewSubject] = useState('');
  const [subjectId, setSubjectId] = useState<number | null>(null);
  const [chapter, setChapter] = useState<number | undefined>(undefined);

  React.useEffect(() => {
    fetch(`${API_BASE_URL}/subjects/`)
      .then((r) => r.json())
      .then((data) => setSubjects(data))
      .catch(() => setSubjects([]));
  }, []);

  async function handleAddSubject() {
    if (!newSubject) return;
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/subjects/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ name: newSubject }),
    });
    if (!res.ok) {
      const d = await res.json();
      setError(d.detail || 'Could not add subject');
      return;
    }
    const s = await res.json();
    setSubjects((prev) => [...prev, s]);
    setSubjectId(s.id);
    setNewSubject('');
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setResult(null);
    console.log('Submitting, current file state:', file);
    if (!file) return setError('Please select a file');
    if (!subjectId) return setError('Please select or create a subject');
    if (!chapter) return setError('Please specify a chapter');
    
    const token = localStorage.getItem('token');
    if (!token) return setError('Please login first');

    setLoading(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('subject_id', String(subjectId));
      if (chapter) fd.append('chapter', String(chapter));
      const res = await fetch(`${API_BASE_URL}/ingestion/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: fd,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Upload failed');
      } else {
        setResult(data);
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xl font-semibold">Upload a Note</h2>
        <Link href="/dashboard" className="text-sm text-blue-600 hover:underline">Back to Dashboard</Link>
      </div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="note-file" className="block mb-2 text-sm font-medium text-gray-700 cursor-pointer">Select file</label>
        {/* Visible control for users: a styled button that triggers the hidden file input */}
        <div className="flex items-center gap-3 mb-2">
          <button
            type="button"
            onClick={() => {
              // open the hidden file input
              const el = document.getElementById('note-file') as HTMLInputElement | null;
              console.log('Choose file clicked, inputEl=', !!el);
              el?.click();
            }}
            className="px-3 py-2 bg-gray-100 border rounded"
          >
            Choose file
          </button>
          <span className="text-sm text-gray-500">{file ? `${file.name} (${Math.round(file.size/1024)} KB)` : 'No file selected'}</span>
        </div>

        <input
          id="note-file"
          name="file"
          type="file"
          accept="image/*,.pdf,.txt"
          onClick={(e) => { /* Clear value so selecting the same file again fires onChange */ (e.currentTarget as HTMLInputElement).value = ''; }}
          onChange={(e) => {
            const f = e.currentTarget.files ? e.currentTarget.files[0] : null;
            console.log('file selected', f, 'filesLength=', e.currentTarget.files?.length);
            setFile(f);
          }}
          className="hidden"
        />
        <p className="text-xs text-gray-500 mb-2">If you don't see the file picker, try clicking the 'Choose file' button or check your browser popup blocker.</p>
        {file && (
          <div className="mb-3 text-sm text-gray-700">
            <div>Selected file: <strong>{file.name}</strong> ({Math.round(file.size/1024)} KB)</div>
            {filePreview && (
              <img src={filePreview} alt="preview" className="mt-2 max-w-xs border rounded" />
            )}
          </div>
        )}

        <div className="mb-3">
          <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
          <div className="flex gap-2">
            <select className="flex-1 px-3 py-2 border rounded" value={subjectId ?? ''} onChange={(e) => setSubjectId(Number(e.target.value))}>
              <option value="">Select subject</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            <input className="px-3 py-2 border rounded" placeholder="New subject" value={newSubject} onChange={(e)=>setNewSubject(e.target.value)} />
            <button type="button" onClick={handleAddSubject} className="px-3 py-2 bg-blue-600 text-white rounded">Add</button>
          </div>
        </div>

        <div className="mb-3">
          <label className="block text-sm font-medium text-gray-700 mb-1">Chapter (required)</label>
          <input type="number" required className="px-3 py-2 border rounded" value={chapter ?? ''} onChange={(e)=>setChapter(e.target.value ? Number(e.target.value) : undefined)} />
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}
        <Button type="submit" fullWidth disabled={loading} className="mt-2">
          {loading ? 'Uploading...' : 'Upload'}
        </Button>
      </form>

      {result && (
        <div className="mt-6 bg-gray-50 p-4 rounded">
          <h3 className="font-semibold">Result</h3>
          <pre className="whitespace-pre-wrap mt-2 text-sm">{result.content}</pre>
        </div>
      )}
    </div>
  );
}
