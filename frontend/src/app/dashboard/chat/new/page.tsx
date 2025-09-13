'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '@/components/layout/dashboard-layout';
import { api, ApiError } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
}

export default function NewChatPage() {
  const router = useRouter();
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKB, setSelectedKB] = useState<number | null>(null);
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchKnowledgeBases();
  }, []);

  const fetchKnowledgeBases = async () => {
    try {
      const data = await api.get('/api/knowledge-base');
      setKnowledgeBases(data);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch knowledge bases:', error);
      if (error instanceof ApiError) {
        toast({
          title: 'Error',
          description: error.message,
          variant: 'destructive',
        });
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedKB) {
      setError('Please select a knowledge base');
      return;
    }

    setError('');
    setIsSubmitting(true);

    try {
      const data = await api.post('/api/chat', {
        title,
        knowledge_base_ids: [selectedKB],
      });

      router.push(`/dashboard/chat/${data.id}`);
    } catch (error) {
      console.error('Failed to create chat:', error);
      if (error instanceof ApiError) {
        setError(error.message);
        toast({
          title: 'Error',
          description: error.message,
          variant: 'destructive',
        });
      } else {
        setError('Failed to create chat');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectKnowledgeBase = (id: number) => {
    setSelectedKB(id);
  };

  if (!isLoading && knowledgeBases.length === 0) {
    return (
      <DashboardLayout>
        <div className='flex items-center justify-center h-[calc(100vh-5rem)]'>
          <Card className='max-w-2xl mx-auto text-center'>
            <CardHeader>
              <CardTitle className='text-3xl font-bold tracking-tight'>
                No Knowledge Bases Found
              </CardTitle>
              <CardDescription className='text-muted-foreground'>
                You need to create at least one knowledge base before starting a
                chat.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild>
                <Link href='/dashboard/knowledge/new'>
                  <Plus className='mr-2 h-4 w-4' />
                  Create Knowledge Base
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className='max-w-2xl mx-auto space-y-8'>
        <div>
          <h2 className='text-3xl font-bold tracking-tight'>Start New Chat</h2>
          <p className='text-muted-foreground'>
            Select a knowledge base to chat with
          </p>
        </div>

        <form onSubmit={handleSubmit} className='space-y-6'>
          <div className='space-y-2'>
            <Label htmlFor='title'>Chat Title</Label>
            <Input
              id='title'
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              type='text'
              required
              placeholder='Enter chat title'
            />
          </div>

          <div className='space-y-2'>
            <Label>Knowledge Base</Label>
            <div className='text-xs text-muted-foreground'>
              Multiple selection coming soon...
            </div>
            <RadioGroup
              value={selectedKB?.toString()}
              onValueChange={(value: string) =>
                selectKnowledgeBase(parseInt(value))
              }
              className='grid gap-4 md:grid-cols-2'
            >
              {isLoading ? (
                <div className='col-span-2 flex justify-center py-8'>
                  <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary'></div>
                </div>
              ) : (
                knowledgeBases.map((kb) => (
                  <Label
                    key={kb.id}
                    htmlFor={kb.id.toString()}
                    className='group flex items-center space-x-3 rounded-lg border p-4 cursor-pointer transition-all duration-200 hover:shadow-md has-[:checked]:border-primary has-[:checked]:bg-primary/5 has-[:checked]:shadow-sm'
                  >
                    <RadioGroupItem
                      value={kb.id.toString()}
                      id={kb.id.toString()}
                    />
                    <div className='flex-1 space-y-1'>
                      <p className='font-medium group-hover:text-primary transition-colors'>
                        {kb.name}
                      </p>
                      <p className='text-sm text-muted-foreground line-clamp-2'>
                        {kb.description || 'No description provided'}
                      </p>
                    </div>
                  </Label>
                ))
              )}
            </RadioGroup>
          </div>

          {error && <div className='text-sm text-red-500'>{error}</div>}

          <div className='flex justify-end space-x-4'>
            <Button
              type='button'
              variant='outline'
              onClick={() => router.back()}
            >
              Cancel
            </Button>
            <Button type='submit' disabled={isSubmitting || !selectedKB}>
              {isSubmitting ? 'Creating...' : 'Start Chat'}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
