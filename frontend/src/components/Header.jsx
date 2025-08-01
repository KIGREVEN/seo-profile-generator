import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { LogOut, User, Shield } from 'lucide-react';
import grevenLogo from '../assets/logo_greven.png';

const Header = () => {
  const { user, logout, isAdmin } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex items-center space-x-3">
              <img 
                src={grevenLogo} 
                alt="Greven Medien Logo" 
                className="h-10 w-auto"
              />
              <div>
                <p className="text-sm text-gray-500 font-medium">Content Generator</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              {isAdmin() ? (
                <Shield className="h-4 w-4 text-orange-500" />
              ) : (
                <User className="h-4 w-4 text-orange-500" />
              )}
              <span>{user?.username}</span>
              <span className="text-xs px-2 py-1 rounded text-white" style={{background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)'}}>
                {user?.role}
              </span>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={logout}
              className="flex items-center space-x-2 border-orange-300 text-orange-600 hover:bg-orange-50"
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

