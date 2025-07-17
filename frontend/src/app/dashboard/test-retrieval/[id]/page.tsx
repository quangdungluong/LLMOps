'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { api, ApiError } from '@/lib/api';
import DashboardLayout from '@/components/layout/dashboard-layout';
import { Search, ArrowRight, Sparkles } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
}

export default function TestPage({ params }: { params: { id: string } }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState('3');
  const { toast } = useToast();

  useEffect(() => {
    const fetchKnowledgeBase = async () => {
      try {
        const data = await api.get(`/api/knowledge-base/${params.id}`);
        setKnowledgeBase(data);
      } catch (error) {
        console.error('Failed to fetch knowledge base:', error);
        if (error instanceof ApiError) {
          toast({
            title: 'Error',
            description: error.message,
            variant: 'destructive',
          });
        }
      }
    };

    fetchKnowledgeBase();
  }, [params.id]);

  const handleTest = async () => {
    if (!query) {
      toast({
        title: 'Please fill in all fields',
        description: 'Please enter query text',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const data = await api.post('/api/knowledge-base/test-retrieval', {
        query,
        kb_id: parseInt(params.id),
        top_k: parseInt(topK),
      });

      setResults(data.results);
    } catch (error) {
      toast({
        title: 'Test Failed',
        description:
          error instanceof Error ? error.message : 'An unknown error occurred.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (!knowledgeBase) {
    return (
      <DashboardLayout>
        <div className='flex items-center justify-center h-full'>
          <Sparkles className='h-8 w-8 animate-spin text-primary' />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className='space-y-8'>
        <div className='text-center'>
          <h1 className='text-4xl font-bold tracking-tighter'>
            Knowledge Base Retrieval Test
          </h1>
          <p className='mt-2 text-lg text-muted-foreground'>
            Test the retrieval performance for{' '}
            <span className='font-semibold text-foreground'>
              {knowledgeBase.name}
            </span>
          </p>
        </div>

        <Card>
          <CardContent className='p-6'>
            <div className='flex flex-col sm:flex-row gap-4'>
              <div className='relative flex-grow'>
                <Search className='absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground' />
                <Input
                  placeholder='Enter your query...'
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className='pl-10 h-12 text-base'
                  onKeyDown={(e) => e.key === 'Enter' && handleTest()}
                  disabled={loading}
                />
              </div>
              <Select value={topK} onValueChange={setTopK}>
                <SelectTrigger className='w-full sm:w-[140px] h-12'>
                  <SelectValue placeholder='Top K' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='1'>Top 1</SelectItem>
                  <SelectItem value='3'>Top 3</SelectItem>
                  <SelectItem value='5'>Top 5</SelectItem>
                  <SelectItem value='10'>Top 10</SelectItem>
                </SelectContent>
              </Select>
              <Button
                onClick={handleTest}
                size='lg'
                className='h-12'
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Sparkles className='animate-spin mr-2 h-4 w-4' />
                    Searching...
                  </>
                ) : (
                  <>
                    Search
                    <ArrowRight className='ml-2 h-4 w-4' />
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {results.length > 0 && (
          <div className='space-y-4'>
            <h2 className='text-2xl font-semibold flex items-center gap-2'>
              <Sparkles className='h-6 w-6 text-primary' />
              Search Results
            </h2>
            <div className='grid gap-4'>
              {results.map((result, index) => (
                <Card key={index} className='overflow-hidden'>
                  <CardHeader className='flex flex-row justify-between items-center bg-muted/50 p-4'>
                    <div className='flex items-center gap-4 flex-wrap'>
                      <span className='text-sm font-medium'>
                        Relevance: {(result.score * 100).toFixed(2)}%
                      </span>
                      <span className='text-sm text-muted-foreground flex items-center gap-2'>
                        <Search className='h-4 w-4' />
                        Source: {result.metadata.source}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className='p-4'>
                    <p className='text-base leading-relaxed whitespace-pre-wrap'>
                      {result.document}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
