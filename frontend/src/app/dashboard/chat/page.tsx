'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, MessageSquare, Trash2, Search } from 'lucide-react';
import DashboardLayout from '@/components/layout/dashboard-layout';
import { api, ApiError } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface Chat {
  id: number;
  title: string;
  created_at: string;
  messages: Message[];
  knowledge_base_ids: number[];
}

interface Message {
  id: number;
  content: string;
  is_bot: boolean;
  created_at: string;
}

export default function ChatPage() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [chatToDelete, setChatToDelete] = useState<Chat | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      const data = await api.get('/api/chat');
      setChats(data);
    } catch (error) {
      console.error('Failed to fetch chats:', error);
      if (error instanceof ApiError) {
        toast({
          title: 'Error',
          description: error.message,
          variant: 'destructive',
        });
      }
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/api/chat/${id}`);
      setChats((prev) => prev.filter((chat) => chat.id !== id));
      toast({
        title: 'Success',
        description: 'Chat deleted successfully',
      });
    } catch (error) {
      console.error('Failed to delete chat:', error);
      if (error instanceof ApiError) {
        toast({
          title: 'Error',
          description: error.message,
          variant: 'destructive',
        });
      }
    }
  };

  const filteredChats = chats.filter((chat) =>
    chat.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className='space-y-6'>
        <Card>
          <CardHeader className='flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4'>
            <div>
              <CardTitle className='text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent'>
                Your Conversations
              </CardTitle>
              <CardDescription className='mt-1'>
                Explore and manage your chat history
              </CardDescription>
            </div>
            <Button asChild>
              <Link href='/dashboard/chat/new'>
                <Plus className='mr-2 h-4 w-4' />
                Start New Chat
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className='relative'>
              <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground' />
              <Input
                type='text'
                placeholder='Search conversations...'
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className='w-full pl-10 pr-4 py-2 rounded-full border bg-background/50 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200'
              />
            </div>
          </CardContent>
        </Card>

        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
          {filteredChats.map((chat) => (
            <Card
              key={chat.id}
              className='group relative hover:shadow-md transition-all duration-200 overflow-hidden'
            >
              <Link href={`/dashboard/chat/${chat.id}`}>
                <CardHeader className='flex flex-row items-start gap-4 p-5'>
                  <div className='bg-primary/10 rounded-lg p-2'>
                    <MessageSquare className='h-6 w-6 text-primary' />
                  </div>
                  <div className='flex-1 min-w-0'>
                    <CardTitle className='text-lg truncate group-hover:text-primary transition-colors'>
                      {chat.title}
                    </CardTitle>
                    <CardDescription className='text-sm mt-1'>
                      {chat.messages.length} messages •{' '}
                      {new Date(chat.created_at).toLocaleDateString()}
                    </CardDescription>
                  </div>
                </CardHeader>
                {chat.messages.length > 0 && (
                  <CardContent className='p-5 pt-0'>
                    <p className='text-sm text-muted-foreground line-clamp-2'>
                      {chat.messages[chat.messages.length - 1].content.includes(
                        '__LLM_RESPONSE__'
                      )
                        ? chat.messages[chat.messages.length - 1].content.split(
                          '__LLM_RESPONSE__'
                        )[1]
                        : chat.messages[chat.messages.length - 1].content}
                    </p>
                  </CardContent>
                )}
              </Link>
              <Button
                variant='ghost'
                size='icon'
                onClick={(e) => {
                  e.preventDefault();
                  setChatToDelete(chat);
                }}
                className='absolute top-4 right-4 h-8 w-8 rounded-full group/delete'
              >
                <Trash2 className='h-4 w-4 text-muted-foreground group-hover/delete:text-destructive transition-colors' />
              </Button>
            </Card>
          ))}
        </div>

        {chats.length === 0 && (
          <Card className='text-center py-16'>
            <CardContent>
              <MessageSquare className='mx-auto h-12 w-12 text-muted-foreground/50' />
              <h3 className='mt-4 text-lg font-medium text-foreground'>
                No conversations yet
              </h3>
              <p className='mt-2 text-muted-foreground'>
                Start a new chat to begin exploring your knowledge base
              </p>
              <Button asChild className='mt-6'>
                <Link href='/dashboard/chat/new'>
                  <Plus className='mr-2 h-4 w-4' />
                  Start Your First Chat
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
      <AlertDialog
        open={!!chatToDelete}
        onOpenChange={(isOpen) => !isOpen && setChatToDelete(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete this
              chat.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (chatToDelete) {
                  handleDelete(chatToDelete.id);
                  setChatToDelete(null);
                }
              }}
            >
              Continue
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
}
