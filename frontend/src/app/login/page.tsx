'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const username = formData.get('username');
    const password = formData.get('password');

    try {
      const formUrlEncoded = new URLSearchParams();
      formUrlEncoded.append('username', username as string);
      formUrlEncoded.append('password', password as string);

      const data = await api.post('/api/auth/token', formUrlEncoded, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      localStorage.setItem('token', data.access_token);
      router.push('/dashboard');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className='min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12'>
      <Card className='w-full max-w-md'>
        <CardHeader className='space-y-1 text-center'>
          <CardTitle className='text-3xl font-bold'>Welcome back</CardTitle>
          <CardDescription>Login to your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className='space-y-4'>
            <div className='space-y-2'>
              <Label htmlFor='username'>Username</Label>
              <Input
                id='username'
                name='username'
                type='text'
                required
                disabled={loading}
                placeholder='Enter your username'
              />
            </div>
            <div className='space-y-2'>
              <Label htmlFor='password'>Password</Label>
              <Input
                id='password'
                name='password'
                type='password'
                required
                disabled={loading}
                placeholder='Enter your password'
              />
            </div>

            {error && (
              <div className='p-3 rounded-md bg-red-50 text-red-700 text-sm'>
                {error}
              </div>
            )}

            <Button type='submit' className='w-full' disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className='flex justify-center'>
          <Link
            href='/register'
            className='text-sm font-medium text-gray-600 hover:text-gray-500'
          >
            Don't have an account? Sign up
          </Link>
        </CardFooter>
      </Card>
    </main>
  );
}
