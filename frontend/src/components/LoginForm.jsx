import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(username, password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)'}}>
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="space-y-1 text-center" style={{background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)', color: 'white', borderRadius: '0.5rem 0.5rem 0 0'}}>
          <CardTitle className="text-3xl font-bold">
            GREVEN
          </CardTitle>
          <CardDescription className="text-orange-100 text-lg font-medium">
            Content Generator
          </CardDescription>
        </CardHeader>
        <CardContent className="bg-white p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="username" className="text-gray-700 font-medium">Benutzername</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
                placeholder="Benutzername eingeben"
                className="border-gray-300 focus:border-orange-500 focus:ring-orange-500"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-gray-700 font-medium">Passwort</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                placeholder="Passwort eingeben"
                className="border-gray-300 focus:border-orange-500 focus:ring-orange-500"
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full font-medium text-white hover:opacity-90 transition-opacity" 
              disabled={loading}
              style={{background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)'}}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Anmelden...
                </>
              ) : (
                'Anmelden'
              )}
            </Button>
          </form>
          
          <div className="mt-4 text-sm text-gray-500 text-center">
            <p>Standard Admin: admin / admin123</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LoginForm;

