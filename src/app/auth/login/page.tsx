"use client";
import React, { useState } from "react";
import { Input } from '@/components/shared/Input';
import { Button } from '@/components/shared/Button';
import Link from 'next/link';

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        // Handle FastAPI validation errors which return an array/object in 'detail'
        const errorMessage = typeof data.detail === 'string' 
          ? data.detail 
          : Array.isArray(data.detail) 
            ? data.detail[0].msg 
            : JSON.stringify(data.detail) || "Login failed";
        setError(errorMessage);
        return;
      }
      // store token
      localStorage.setItem("token", data.access_token);
      window.location.href = "/dashboard";
    } catch (err) {
      setError("Network error");
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Sign in</h2>
      <form onSubmit={handleSubmit}>
        <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <Button type="submit" fullWidth className="mt-4">Sign in</Button>
      </form>

      <div className="mt-6 flex justify-between text-sm">
        <Link href="/" className="text-blue-600 hover:underline">
          &larr; Back to Home
        </Link>
        <Link href="/auth/register" className="text-blue-600 hover:underline">
          Need an account? Register
        </Link>
      </div>
    </div>
  );
}
