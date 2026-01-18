"use client";
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/shared/Button';

export default function MasterNoteTab() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [subjectId, setSubjectId] = useState<number | null>(null);
  const [chapter, setChapter] = useState<number | ''>('');
  const [allNotes, setAllNotes] = useState<any[]>([]);
  const [selectedNoteIds, setSelectedNoteIds] = useState<number[]>([]);
  const [masterNote, setMasterNote] = useState<any>(null);
  const [latestMaster, setLatestMaster] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [consensusLoading, setConsensusLoading] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/subjects/')
      .then(r => r.json())
      .then(setSubjects)
      .catch(() => setSubjects([]));

    // Also fetch the user's most recent master note so we can offer a quick link
    async function loadLatestMaster() {
      try {
        const res = await fetch('http://localhost:8000/consensus/master/latest', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        if (!res.ok) return;
        const data = await res.json();
        setLatestMaster(data);
      } catch (e) {
        // ignore
      }
    }
    loadLatestMaster();
  }, []);

  async function fetchAllNotes() {
    if (!subjectId) return;
    setLoading(true);
    setAllNotes([]);
    setMasterNote(null);
    try {
      const chapterQuery = chapter !== '' ? `&chapter=${chapter}` : '';
      const res = await fetch(`http://localhost:8000/notes/all?subject_id=${subjectId}${chapterQuery}`);
      const data = await res.json();
      setAllNotes(data);
      // Try to fetch existing master note if a chapter is specified
      if (chapter !== '') {
        fetchMasterNoteInternal();
      }
    } catch (e) {
      setError('Failed to fetch notes.');
    } finally {
      setLoading(false);
    }
  }

  async function fetchMasterNoteInternal(overrideSubjectId?: number, overrideChapter?: string | number) {
    const sId = overrideSubjectId ?? subjectId;
    const ch = overrideChapter ?? chapter;
    if (!sId || ch === '') return;
    try {
      const res = await fetch(`http://localhost:8000/consensus/master/${sId}/${ch}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setMasterNote(data);
        setLatestMaster(data);
      } else {
        setMasterNote(null);
      }
    } catch (e) {
      setMasterNote(null);
    }
  }

  async function handleCreateConsensus() {
    if (!subjectId) return alert('Please select a subject first.');
    if (selectedNoteIds.length === 0) return alert('Please select notes to create consensus.');
    setConsensusLoading(true);
    try {
      const res = await fetch('http://localhost:8000/consensus/process', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          subject_id: subjectId,
          chapter: chapter === '' ? null : chapter,
          note_ids: selectedNoteIds
        })
      });
      if (res.ok) {
        const result = await res.json();
        alert('Consensus created! Fetching master note...');
        
        let finalChapter = chapter;
        if (chapter === '' && result.chapter) {
          finalChapter = result.chapter;
          setChapter(result.chapter);
        }
        
        // Pass the explicit values to avoid waiting for state update
        fetchMasterNoteInternal(subjectId || undefined, finalChapter);
      } else {
        const errData = await res.json();
        const errorMessage = typeof errData.detail === 'string' 
          ? errData.detail 
          : JSON.stringify(errData.detail);
        alert(`Error: ${errorMessage || 'Failed to create consensus'}`);
      }
    } catch (e: any) {
      console.error('Consensus Error:', e);
      alert(`Error creating consensus: ${e.message || 'Check network connection'}`);
    } finally {
      setConsensusLoading(false);
    }
  }

  async function handleDownloadPDF() {
    if (!subjectId || chapter === '') return;
    try {
      const res = await fetch(`http://localhost:8000/consensus/master/${subjectId}/${chapter}/pdf`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `MasterNote_Ch${chapter}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      } else {
        alert('Failed to download PDF');
      }
    } catch (e) {
      alert('Error downloading PDF');
    }
  }

  function toggleNoteSelection(id: number) {
    setSelectedNoteIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  }

  function handleSelectAll() {
    if (selectedNoteIds.length === allNotes.length) {
      setSelectedNoteIds([]);
    } else {
      setSelectedNoteIds(allNotes.map(n => n.id));
    }
  }

  return (
    <div className="p-6">
      <div className="flex flex-wrap gap-4 items-end mb-8 border-b pb-6">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Subject</label>
          <select 
            className="px-3 py-2 border rounded-lg text-sm min-w-[200px]"
            value={subjectId ?? ''}
            onChange={(e) => setSubjectId(Number(e.target.value) || null)}
          >
            <option value="">Select Subject</option>
            {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Chapter</label>
          <div className="flex items-center gap-2">
            <input 
              type="text" 
              placeholder="All"
              className="px-3 py-2 border rounded-lg text-sm w-24" 
              value={chapter}
              onChange={(e) => {
                const val = e.target.value;
                if (val === '') setChapter('');
                else if (!isNaN(Number(val))) setChapter(Number(val));
              }}
            />
            {chapter === '' && <span className="text-xs text-gray-400 italic">(Showing All)</span>}
          </div>
        </div>
        <Button onClick={fetchAllNotes} disabled={!subjectId || loading}>
          {loading ? 'Searching...' : 'Search Notes'}
        </Button>
      </div>

      <div className="max-w-5xl mx-auto space-y-10">
        {latestMaster && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md text-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="font-medium text-yellow-800">Last Master Note: <span className="font-bold">{latestMaster.topic}</span></div>
                <div className="text-xs text-yellow-700">Chapter {latestMaster.chapter} • Version {latestMaster.version}</div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setSubjectId(latestMaster.subject_id);
                    setChapter(latestMaster.chapter);
                    setMasterNote(latestMaster);
                  }}
                  className="px-3 py-1 bg-yellow-400 text-white rounded-md text-sm"
                >
                  Open Last Master Note
                </button>
                <button
                  onClick={() => setLatestMaster(null)}
                  className="px-2 py-1 text-xs text-yellow-700 underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {allNotes.length > 0 && (
          <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-gray-800">Available Notes ({allNotes.length})</h3>
                <button 
                  onClick={handleSelectAll}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium underline mt-1"
                >
                  {selectedNoteIds.length === allNotes.length ? 'Deselect All' : 'Select All Notes'}
                </button>
              </div>
              <Button
                variant="primary"
                onClick={handleCreateConsensus}
                disabled={consensusLoading}
                className="shadow-lg border-2 border-blue-700"
              >
                {consensusLoading ? 'Synthesizing Master Note...' : 'Create Consensus'}
              </Button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-700 uppercase bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 w-10"></th>
                    <th className="px-4 py-3">Chapter</th>
                    <th className="px-4 py-3">Teacher</th>
                    <th className="px-4 py-3">Year</th>
                    <th className="px-4 py-3">Pseudo Name</th>
                    <th className="px-4 py-3 text-right">Preview</th>
                  </tr>
                </thead>
                <tbody>
                  {allNotes.map(n => (
                    <tr key={n.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <input 
                          type="checkbox" 
                          checked={selectedNoteIds.includes(n.id)}
                          onChange={() => toggleNoteSelection(n.id)}
                        />
                      </td>
                      <td className="px-4 py-3">Ch {n.chapter}</td>
                      <td className="px-4 py-3 font-medium">{n.teacher || 'N/A'}</td>
                      <td className="px-4 py-3">{n.year || 'N/A'}</td>
                      <td className="px-4 py-3 text-blue-600">{n.pseudo_name || `User#${n.user_id}`}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="text-gray-500 text-xs line-clamp-2 max-w-[250px] ml-auto">
                          {n.content}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {masterNote ? (
          <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
            <div className="bg-blue-600 px-6 py-4 text-white flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold">{masterNote.topic}</h2>
                <p className="text-blue-100 text-sm">Version {masterNote.version} • Sync Date: {new Date(masterNote.created_at).toLocaleDateString()}</p>
              </div>
              <button 
                onClick={handleDownloadPDF}
                className="bg-white text-blue-600 px-4 py-2 rounded-lg text-sm font-bold shadow hover:bg-blue-50 transition-colors"
              >
                Download PDF
              </button>
            </div>
            <div className="p-10 prose prose-blue max-w-none">
              <div className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed bg-white border p-6 rounded shadow-inner min-h-[400px]">
                {masterNote.content}
              </div>
            </div>
          </div>
        ) : (
          subjectId && chapter !== '' && !loading && (
            <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
              <p className="text-gray-500">No Master Note found for this chapter yet.</p>
              <p className="text-sm text-gray-400 mt-2">Select peer notes above and click "Create Consensus" to generate one.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
