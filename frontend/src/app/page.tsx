"use client";
import React, { useEffect, useState } from "react";
import { Layout } from "@/components/shared/Layout";
import { Button } from "@/components/shared/Button";
import Image from "next/image";
import Link from "next/link";

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <Layout>
      <div className="flex flex-col items-center text-center py-12">
        {/* Logo */}
        <div className="mb-8">
          <Image 
            src="/logo.jpg" 
            alt="HiveMind Logo" 
            width={200} 
            height={200} 
            className="rounded-2xl shadow-lg"
            priority
          />
        </div>

        {/* Hero Section */}
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl mb-6">
          Welcome to <span className="text-blue-600">HiveMind</span>
        </h1>
        
        <p className="text-xl text-gray-600 max-w-2xl mb-10 leading-relaxed">
          Ending Educational Amnesia through collaborative intelligence. 
          HiveMind turns your individual notes into a collective "Master Note," 
          creating lasting institutional memory for your class.
        </p>

        {/* Feature Cards / Writeup */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12 text-left">
          <div className="p-6 border border-gray-100 rounded-2xl bg-gray-50">
            <h3 className="text-lg font-bold mb-2">Synthesize Knowledge</h3>
            <p className="text-gray-600">
              Upload your handwritten and typed notes. Our AI analyzes and identifies 
              consensus across the class to build the most accurate record.
            </p>
          </div>
          <div className="p-6 border border-gray-100 rounded-2xl bg-gray-50">
            <h3 className="text-lg font-bold mb-2">Institutional Memory</h3>
            <p className="text-gray-600">
              Access previous years\' notes and insights. Track how concepts evolve 
              under different teachers and semesters.
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
          {!isLoggedIn ? (
            <>
              <Link href="/auth/login" className="flex-1">
                <Button fullWidth variant="primary" className="py-4 text-lg">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/register" className="flex-1">
                <Button fullWidth variant="outline" className="py-4 text-lg">
                  Register
                </Button>
              </Link>
            </>
          ) : (
            <Link href="/dashboard" className="w-full" onClick={() => { (window as any).__allowNavigateToDashboard = true; }}>
              <Button fullWidth variant="primary" className="py-4 text-lg">
                Go to Dashboard
              </Button>
            </Link>
          )}
        </div>
      </div>
    </Layout>
  );
}
