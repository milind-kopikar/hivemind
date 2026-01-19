\"use client\";
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { API_BASE_URL } from '@/utils/api';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [pseudo, setPseudo] = useState<string | null>(null);

  useEffect(() => {
    async function loadProfile() {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;
        const res = await fetch(\/auth/me, { headers: { Authorization: Bearer \ } });
        if (!res.ok) return;
        const data = await res.json();
        setPseudo(data.pseudo_name || null);
      } catch (e) {
        console.error('[Layout] loadProfile error', e);
      }
    }
    loadProfile();
  }, []);

  return (
    <div className=\"min-h-screen bg-gray-50 flex flex-col\">
      <header className=\"bg-white border-b px-4 py-3 flex justify-between items-center sticky top-0 z-10\">
        <div className=\"flex items-center gap-6\">
          {pseudo ? (
            <span className=\"text-xl font-bold text-blue-800 cursor-default\">HiveMind</span>
          ) : (
            <Link href=\"/\" className=\"text-xl font-bold text-blue-800\">HiveMind</Link>
          )}
          <nav className=\"hidden md:flex gap-4\">
            {pseudo ? (
              <span className=\"text-sm font-medium text-gray-600\">Home</span>
            ) : (
              <Link href=\"/\" className=\"text-sm font-medium text-gray-600 hover:text-blue-600\">Home</Link>
            )}
            <Link href=\"/dashboard\" className=\"text-sm font-medium text-gray-600 hover:text-blue-600\">Dashboard</Link>
            <Link href=\"/upload\" className=\"text-sm font-medium text-gray-600 hover:text-blue-600\">Quick Upload</Link>
          </nav>
        </div>
        <div className=\"flex items-center gap-4\">
          {pseudo ? (
            <div className=\"flex items-center gap-3\">
              <div className=\"text-sm text-gray-700 mr-2\">{pseudo}</div>
              <div 
                className=\"w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-800 font-bold cursor-pointer relative group\"
                title={pseudo}
              >
                {pseudo.charAt(0).toUpperCase()}
                <div className=\"absolute right-0 top-full pt-2 hidden group-hover:block min-w-[140px] z-50\">
                  <div className=\"bg-white border rounded-xl shadow-xl p-2 overflow-hidden\">
                    <div className=\"px-3 py-2 border-b mb-1\">
                      <p className=\"text-xs text-gray-400 uppercase font-bold tracking-wider\">Account</p>
                      <p className=\"text-sm font-medium\">{pseudo}</p>
                    </div>
                    <button 
                      onClick={() => {
                        localStorage.removeItem('token');
                        window.location.href = '/auth/login';
                      }}
                      className=\"w-full text-left px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2\"
                    >
                      <span>Log Out</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <Link href=\"/auth/login\">
              <button className=\"text-sm font-medium text-blue-600 hover:text-blue-800\">Sign In</button>
            </Link>
          )}
        </div>
      </header>
      
      <main className=\"flex-grow p-4 md:max-w-6xl md:mx-auto w-full\">
        {children}
      </main>
      
      <footer className=\"bg-white border-t p-4 text-center text-sm text-gray-500\">
         2026 HiveMind Education
      </footer>
    </div>
  );
};
