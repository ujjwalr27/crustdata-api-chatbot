// src/App.js
import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

// Styled Components
const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', sans-serif;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  color: #2c3e50;
  font-size: 2.5em;
`;

const ChatContainer = styled.div`
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 900px;
  margin: 0 auto;
`;

const MessagesContainer = styled.div`
  height: 500px;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
`;

const MessageWrapper = styled.div`
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: ${props => props.isUser ? 'flex-end' : 'flex-start'};
`;

const MessageContent = styled.div`
  background: ${props => props.isUser ? '#007bff' : '#ffffff'};
  color: ${props => props.isUser ? '#ffffff' : '#2c3e50'};
  padding: 12px 18px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 80%;
  white-space: pre-wrap;
`;

const Sources = styled.div`
  margin-top: 8px;
  font-size: 0.85em;
  color: #6c757d;
  max-width: 80%;
`;

const SourceItem = styled.div`
  margin-top: 4px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
`;

const InputContainer = styled.div`
  display: flex;
  padding: 20px;
  background: #ffffff;
  border-top: 1px solid #e9ecef;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  margin-right: 10px;
  font-size: 16px;
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Button = styled.button`
  background: #007bff;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  &:hover {
    background: #0056b3;
  }
  &:disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
`;

const RefreshButton = styled(Button)`
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 8px 16px;
  font-size: 14px;
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: #dc3545;
  color: white;
  padding: 10px;
  border-radius: 6px;
  margin: 10px 0;
  text-align: center;
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      text: inputMessage,
      type: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`/api/chat`, {
        message: inputMessage
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      const botMessage = {
        text: response.data.answer,
        sources: response.data.sources || [],
        type: 'bot'
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      setError(error.message || 'An error occurred while processing your request');
      const errorMessage = {
        text: error.message || 'Sorry, I encountered an error. Please try again.',
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setError(null);

    try {
      const response = await axios.post(`/api/refresh`);
      
      if (response.data.status === 'error') {
        throw new Error(response.data.message);
      }

      setMessages(prev => [...prev, { 
        text: 'Knowledge base has been refreshed successfully!',
        type: 'bot'
      }]);
    } catch (err) {
      console.error('Error refreshing data:', err);
      setError(err.message || 'Failed to refresh knowledge base. Please try again.');
      setMessages(prev => [...prev, { 
        text: err.message || 'Failed to refresh knowledge base. Please try again.',
        type: 'error'
      }]);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <Container>
      <Header>
        <Title>Crustdata Support Chat</Title>
        <RefreshButton 
          onClick={handleRefresh} 
          disabled={isRefreshing}
        >
          {isRefreshing ? <><LoadingSpinner />Refreshing...</> : 'Refresh Knowledge'}
        </RefreshButton>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      <ChatContainer>
        <MessagesContainer>
          {messages.map((message, index) => (
            <MessageWrapper key={index} isUser={message.type === 'user'}>
              <MessageContent isUser={message.type === 'user'}>
                {message.text}
              </MessageContent>
              {message.sources && message.sources.length > 0 && (
                <Sources>
                  <div>Sources:</div>
                  {message.sources.map((source, idx) => (
                    <SourceItem key={idx}>
                      <div>{source.text}</div>
                      <div style={{ fontSize: '0.9em', marginTop: '4px', color: '#0056b3' }}>
                        {source.source}
                      </div>
                    </SourceItem>
                  ))}
                </Sources>
              )}
            </MessageWrapper>
          ))}
          {isLoading && (
            <MessageWrapper>
              <MessageContent isUser={false}>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </MessageContent>
            </MessageWrapper>
          )}
          <div ref={messagesEndRef} />
        </MessagesContainer>

        <InputContainer>
          <Input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSubmit(e)}
            placeholder="Ask a question about Crustdata APIs..."
            disabled={isLoading}
          />
          <Button onClick={handleSubmit} disabled={isLoading || !inputMessage.trim()}>
            {isLoading ? <><LoadingSpinner />Sending...</> : 'Send'}
          </Button>
        </InputContainer>
      </ChatContainer>
    </Container>
  );
}

export default App;