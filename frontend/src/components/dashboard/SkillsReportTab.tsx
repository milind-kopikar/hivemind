"use client";
import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/utils/api';

export default function SkillsReportTab() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch(`${API_BASE_URL}/analytics/report`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-10 text-center">Loading your progress...</div>;

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-8">Performance & Contributions</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-blue-900">Information Synthesis</h3>
            <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-bold">LVL {stats?.prep_level || 3}</span>
          </div>
          <p className="text-sm text-blue-800 mb-6">Measures how well you understand the collective knowledge based on quiz results.</p>
          <div className="w-full bg-blue-200 rounded-full h-4">
            <div className="bg-blue-600 h-4 rounded-full" style={{ width: `${stats?.prep_score || 65}%` }}></div>
          </div>
          <div className="flex justify-between mt-2 text-xs text-blue-700 font-bold">
            <span>BEGINNER</span>
            <span> {stats?.prep_score || 65}% Mastery</span>
            <span>EXPERT</span>
          </div>
        </div>

        <div className="bg-purple-50 p-6 rounded-2xl border border-purple-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-purple-900">Institutional Memory</h3>
            <span className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-bold">HERO</span>
          </div>
          <p className="text-sm text-purple-800 mb-6">Measures your contribution to the community Master Note through uploads.</p>
          <div className="w-full bg-purple-200 rounded-full h-4">
            <div className="bg-purple-600 h-4 rounded-full" style={{ width: `${stats?.contribution_score || 82}%` }}></div>
          </div>
          <div className="flex justify-between mt-2 text-xs text-purple-700 font-bold">
            <span>SILENT</span>
            <span>{stats?.contribution_score || 82}% Active</span>
            <span>TOP CONTRIBUTOR</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 p-8 rounded-2xl border border-gray-100">
        <h3 className="font-bold text-gray-800 mb-4">Upcoming Goals</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-4 bg-white p-4 rounded-xl border">
            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600">✓</div>
            <div>
              <p className="text-sm font-bold">Upload Chapter 9 Notes</p>
              <p className="text-xs text-gray-500">Contribute to the consensus early!</p>
            </div>
          </div>
          <div className="flex items-center gap-4 bg-white p-4 rounded-xl border">
            <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-600">!</div>
            <div>
              <p className="text-sm font-bold">Perfect Chapter 8 Quiz</p>
              <p className="text-xs text-gray-500">Current high score is 75%. Try again in Test Prep.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
