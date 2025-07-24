import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { LogOut, User, Shield } from 'lucide-react';

const Header = () => {
  const { user, logout, isAdmin } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-gray-900">
              SEO Profile Generator
            </h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              {isAdmin() ? (
                <Shield className="h-4 w-4 text-blue-600" />
              ) : (
                <User className="h-4 w-4" />
              )}
              <span>{user?.username}</span>
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                {user?.role}
              </span>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={logout}
              className="flex items-center space-x-2"
            >
              <LogOut className="h-4 w-4" />
              <span>Abmelden</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

