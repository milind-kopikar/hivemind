"use client";
import React, { useState, useEffect } from 'react';
import MyNotesTab from '@/components/dashboard/MyNotesTab';
import MasterNoteTab from '@/components/dashboard/MasterNoteTab';
import TestPrepTab from '@/components/dashboard/TestPrepTab';
import SkillsReportTab from '@/components/dashboard/SkillsReportTab';
import { Layout } from '@/components/shared/Layout';

const TABS = [
  { id: 'notes', label: 'My Notes' },
  { id: 'master', label: 'Master Note' },
  { id: 'prep', label: 'Test Prep' },
  { id: 'skills', label: 'Skills Report' },
];

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('notes');

  return (
    <Layout>
      <div className="max-w-6xl mx-auto py-6 px-4">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">Student Dashboard</h1>
        
        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 mb-8 overflow-x-auto whitespace-nowrap">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-6 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 min-h-[500px]">
          {activeTab === 'notes' && <MyNotesTab />}
          {activeTab === 'master' && <MasterNoteTab />}
          {activeTab === 'prep' && <TestPrepTab />}
          {activeTab === 'skills' && <SkillsReportTab />}
        </div>
      </div>
    </Layout>
  );
}
