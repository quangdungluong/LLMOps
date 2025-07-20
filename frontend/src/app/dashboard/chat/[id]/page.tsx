'use client';

import { useEffect, useRef, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useChat } from '@ai-sdk/react';
import { Send, User, Bot } from 'lucide-react';
import DashboardLayout from '@/components/layout/dashboard-layout';
import { api, ApiError } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { Answer } from '@/components/chat/answer';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';

interface Message {
  id: string;
  role: 'assistant' | 'user' | 'system' | 'data';
  content: string;
  citations?: Citation[];
}

interface ChatMessage {
  id: number;
  content: string;
  role: 'assistant' | 'user';
  created_at: string;
}

interface Chat {
  id: number;
  title: string;
  messages: ChatMessage[];
}

interface Citation {
  id: number;
  text: string;
  metadata: Record<string, any>;
}

export default function ChatPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  const {
    messages,
    data,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    setMessages,
  } = useChat({
    api: `/api/chat/${params.id}/messages`,
    headers: {
      Authorization: `Bearer ${typeof window !== 'undefined'
        ? window.localStorage.getItem('token')
        : ''
        }`,
    },
  });

  useEffect(() => {
    if (isInitialLoad) {
      fetchChat();
      setIsInitialLoad(false);
    }
  }, [isInitialLoad]);

  useEffect(() => {
    if (!isInitialLoad) {
      scrollToBottom();
    }
  }, [messages, isInitialLoad]);

  const processMessage = (msg: ChatMessage | Message): Message => {
    const messageId = 'id' in msg ? msg.id.toString() : '';

    if (msg.role !== 'assistant' || !msg.content) {
      return {
        id: messageId,
        role: msg.role,
        content: msg.content,
      };
    }

    try {
      if (!msg.content.includes('__LLM_RESPONSE__')) {
        return {
          id: messageId,
          role: msg.role,
          content: msg.content,
        };
      }

      const [base64Part, responseText] = msg.content.split('__LLM_RESPONSE__');

      const contextData = base64Part
        ? (JSON.parse(atob(base64Part.trim())) as {
          context: Array<{
            page_content: string;
            metadata: Record<string, any>;
          }>;
        })
        : null;

      const citations: Citation[] =
        contextData?.context.map((citation, index) => ({
          id: index + 1,
          text: citation.page_content,
          metadata: citation.metadata,
        })) || [];

      return {
        id: messageId,
        role: msg.role,
        content: responseText || '',
        citations,
      };
    } catch (e) {
      console.error('Failed to process message:', e);
      return {
        id: messageId,
        role: msg.role,
        content: msg.content,
      };
    }
  };

  const fetchChat = async () => {
    try {
      const data: Chat = await api.get(`/api/chat/${params.id}`);
      const formattedMessages = data.messages.map(processMessage);
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Failed to fetch chat:', error);
      if (error instanceof ApiError) {
        toast({
          title: 'Error',
          description: error.message,
          variant: 'destructive',
        });
      }
      router.push('/dashboard/chat');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const markdownParse = (text: string) => {
    return text
      .replace(/\[\[([cC])itation/g, '[citation')
      .replace(/[cC]itation:(\d+)]]/g, 'citation:$1]')
      .replace(/\[\[([cC]itation:\d+)]](?!])/g, `[$1]`)
      .replace(/\[[cC]itation:(\d+)]/g, '[citation]($1)');
  };

  const processedMessages = useMemo(() => {
    return messages.map((message) => {
      const processed = processMessage(message);
      return {
        ...processed,
        content: markdownParse(processed.content),
      };
    });
  }, [messages]);

  return (
    <DashboardLayout>
      <div className='flex flex-col h-[calc(100vh-5rem)] relative'>
        <div className='flex-1 overflow-y-auto p-4 space-y-4 pb-[80px]'>
          {processedMessages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-4 ${message.role === 'user' ? 'justify-end' : ''
                }`}
            >
              {message.role === 'assistant' && (
                <Avatar>
                  <AvatarImage src='/logo.png' alt='logo' />
                  <AvatarFallback>
                    <Bot />
                  </AvatarFallback>
                </Avatar>
              )}
              <Card
                className={`max-w-[80%] ${message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : ''
                  }`}
              >
                <CardContent className='p-4'>
                  {message.role === 'assistant' ? (
                    <Answer
                      key={message.id}
                      markdown={message.content}
                      citations={message.citations}
                    />
                  ) : (
                    message.content
                  )}
                </CardContent>
              </Card>
              {message.role === 'user' && (
                <Avatar>
                  <AvatarFallback>
                    <User />
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
          <div className='flex justify-start'>
            {isLoading &&
              processedMessages[processedMessages.length - 1]?.role !=
              'assistant' && (
                <Card>
                  <CardContent className='p-4'>
                    <div className='flex items-center space-x-1'>
                      <div className='w-2 h-2 rounded-full bg-primary animate-bounce' />
                      <div className='w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.2s]' />
                      <div className='w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.4s]' />
                    </div>
                  </CardContent>
                </Card>
              )}
          </div>
          <div ref={messagesEndRef} />
        </div>
        <form
          onSubmit={handleSubmit}
          className='border-t p-4 flex items-center space-x-4 bg-background absolute bottom-0 left-0 right-0'
        >
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder='Type your message...'
            className='flex-1'
          />
          <Button type='submit' disabled={isLoading || !input.trim()}>
            <Send className='h-4 w-4' />
          </Button>
        </form>
      </div>
    </DashboardLayout>
  );
}
