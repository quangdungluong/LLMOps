'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card';

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState({
    email: '',
    password: '',
    confirmPassword: '',
  });

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setValidationErrors((prev) => ({
        ...prev,
        email: 'Please enter a valid email address',
      }));
      return false;
    }
    setValidationErrors((prev) => ({ ...prev, email: '' }));
    return true;
  };

  const validatePassword = (password: string) => {
    if (password.length < 8) {
      setValidationErrors((prev) => ({
        ...prev,
        password: 'Password must be at least 8 characters long',
      }));
      return false;
    }
    if (!/[A-Z]/.test(password)) {
      setValidationErrors((prev) => ({
        ...prev,
        password: 'Password must contain at least one uppercase letter',
      }));
      return false;
    }
    if (!/[a-z]/.test(password)) {
      setValidationErrors((prev) => ({
        ...prev,
        password: 'Password must contain at least one lowercase letter',
      }));
      return false;
    }
    if (!/[0-9]/.test(password)) {
      setValidationErrors((prev) => ({
        ...prev,
        password: 'Password must contain at least one number',
      }));
      return false;
    }
    setValidationErrors((prev) => ({ ...prev, password: '' }));
    return true;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setValidationErrors({ email: '', password: '', confirmPassword: '' });

    const formData = new FormData(e.currentTarget);
    const username = formData.get('username') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const confirmPassword = formData.get('confirmPassword') as string;

    // Validate email and password
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);

    if (password !== confirmPassword) {
      setValidationErrors((prev) => ({
        ...prev,
        confirmPassword: 'Passwords do not match',
      }));
      return;
    }

    if (!isEmailValid || !isPasswordValid) {
      return;
    }

    try {
      await api.post('/api/auth/register', {
        username,
        email,
        password,
      });

      router.push('/login');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Registration failed');
      }
    }
  };

  return (
    <main className='min-h-screen bg-gray-50 flex items-center justify-center px-4 sm:px-6 lg:px-8'>
      <div className='w-full max-w-md'>
        <Card>
          <CardHeader className='text-center'>
            <CardTitle>Create an account</CardTitle>
            <CardDescription>
              Fill in the details below to create your account.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className='space-y-6' onSubmit={handleSubmit}>
              <div className='space-y-4'>
                <div className='space-y-2'>
                  <Label htmlFor='username'>Username</Label>
                  <Input
                    id='username'
                    name='username'
                    type='text'
                    required
                    placeholder='Enter your username'
                  />
                </div>

                <div className='space-y-2'>
                  <Label htmlFor='email'>Email</Label>
                  <Input
                    id='email'
                    name='email'
                    type='email'
                    required
                    className={validationErrors.email ? 'border-red-300' : ''}
                    placeholder='Enter your email'
                    onChange={(e) => validateEmail(e.target.value)}
                  />
                  {validationErrors.email && (
                    <p className='text-sm text-red-600'>
                      {validationErrors.email}
                    </p>
                  )}
                </div>

                <div className='space-y-2'>
                  <Label htmlFor='password'>Password</Label>
                  <Input
                    id='password'
                    name='password'
                    type='password'
                    required
                    className={
                      validationErrors.password ? 'border-red-300' : ''
                    }
                    placeholder='Create a password'
                    onChange={(e) => validatePassword(e.target.value)}
                  />
                  {validationErrors.password && (
                    <p className='text-sm text-red-600'>
                      {validationErrors.password}
                    </p>
                  )}
                </div>

                <div className='space-y-2'>
                  <Label htmlFor='confirmPassword'>Confirm Password</Label>
                  <Input
                    id='confirmPassword'
                    name='confirmPassword'
                    type='password'
                    required
                    className={
                      validationErrors.confirmPassword ? 'border-red-300' : ''
                    }
                    placeholder='Confirm your password'
                  />
                  {validationErrors.confirmPassword && (
                    <p className='text-sm text-red-600'>
                      {validationErrors.confirmPassword}
                    </p>
                  )}
                </div>
              </div>

              {error && (
                <div className='p-3 rounded-md bg-red-50 text-red-700 text-sm'>
                  {error}
                </div>
              )}

              <Button type='submit' className='w-full'>
                Sign up
              </Button>
            </form>
          </CardContent>
          <CardFooter className='flex justify-center'>
            <Link
              href='/login'
              className='text-sm font-medium text-gray-600 hover:text-gray-500'
            >
              Already have an account? Sign in
            </Link>
          </CardFooter>
        </Card>
      </div>
    </main>
  );
}
