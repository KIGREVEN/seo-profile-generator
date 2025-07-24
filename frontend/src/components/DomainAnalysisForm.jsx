import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Globe, CheckCircle } from 'lucide-react';

const DomainAnalysisForm = ({ onAnalysisComplete }) => {
  const [domain, setDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { token } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/seo/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(data.message);
        setDomain('');
        if (onAnalysisComplete) {
          onAnalysisComplete(data.result);
        }
      } else {
        setError(data.error || 'Analyse fehlgeschlagen');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setError('Netzwerkfehler bei der Analyse');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Globe className="h-5 w-5" />
          <span>Domain-Analyse</span>
        </CardTitle>
        <CardDescription>
          Geben Sie eine Domain ein, um eine SEO-optimierte Unternehmensbeschreibung zu generieren
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {success && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="domain">Domain</Label>
            <Input
              id="domain"
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              required
              disabled={loading}
              placeholder="z.B. example.com oder https://example.com"
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full" 
            disabled={loading || !domain.trim()}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analysiere Domain...
              </>
            ) : (
              'Domain analysieren'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default DomainAnalysisForm;

