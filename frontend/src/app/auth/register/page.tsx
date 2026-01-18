"use client";
import React, { useState } from "react";
import { Input } from '@/components/shared/Input';
import { Button } from '@/components/shared/Button';
import Link from 'next/link';
import { API_BASE_URL } from '@/utils/api';

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pseudoName, setPseudoName] = useState("");
  const [teacher, setTeacher] = useState("");
  const [year, setYear] = useState(new Date().getFullYear());
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          email, 
          password, 
          pseudo_name: pseudoName,
          teacher: teacher,
          year: Number(year)
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        const errorMessage = typeof data.detail === 'string' 
          ? data.detail 
          : Array.isArray(data.detail) 
            ? data.detail[0].msg 
            : JSON.stringify(data.detail) || "Registration failed";
        setError(errorMessage);
        return;
      }
      setSuccess("Registered successfully. Please log in.");
    } catch (err) {
      setError("Network error");
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Create account</h2>
      <form onSubmit={handleSubmit}>
        <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <Input label="Pseudo Name (e.g. BioWizard)" type="text" value={pseudoName} onChange={(e) => setPseudoName(e.target.value)} required />
        <Input label="Teacher Name" type="text" value={teacher} onChange={(e) => setTeacher(e.target.value)} required />
        <Input label="Year Taken" type="number" value={String(year)} onChange={(e) => setYear(Number(e.target.value))} required />
        {error && <p className="text-red-500 text-sm">{error}</p>}
        {success && <p className="text-green-600 text-sm">{success}</p>}
        <Button type="submit" fullWidth className="mt-4">Register</Button>
      </form>
      
      <div className="mt-6 flex justify-between text-sm">
        <Link href="/" className="text-blue-600 hover:underline">
          &larr; Back to Home
        </Link>
        <Link href="/auth/login" className="text-blue-600 hover:underline">
          Already have an account? Sign in
        </Link>
      </div>
    </div>
  );
}
