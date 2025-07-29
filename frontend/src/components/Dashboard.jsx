import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from './Header';
import DomainAnalysisForm from './DomainAnalysisForm';
import SEOResultDisplay from './SEOResultDisplay';
import UserManagement from './UserManagement';
import ImageGenerator from './ImageGenerator';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Search, RefreshCw, Eye, Trash2, Users, Settings, ArrowLeft, Image, Globe } from 'lucide-react';

const Dashboard = () => {
  const { token, isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState('seo'); // 'seo' or 'images'
  const [results, setResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showUserManagement, setShowUserManagement] = useState(false);

  useEffect(() => {
    fetchResults();
  }, [currentPage, searchTerm]);

  const fetchResults = async () => {
    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams({
        page: currentPage,
        per_page: 10,
        ...(searchTerm && { search: searchTerm })
      });

      const response = await fetch(`/api/seo/results?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setResults(data.results);
        setTotalPages(data.pages);
      } else {
        setError(data.error || 'Fehler beim Laden der Ergebnisse');
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setError('Netzwerkfehler beim Laden der Ergebnisse');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysisComplete = (newResult) => {
    setSelectedResult(newResult);
    fetchResults(); // Refresh the list
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchResults();
  };

  const viewResult = async (resultId) => {
    try {
      const response = await fetch(`/api/seo/results/${resultId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setSelectedResult(data);
      } else {
        setError(data.error || 'Fehler beim Laden des Ergebnisses');
      }
    } catch (error) {
      console.error('View error:', error);
      setError('Netzwerkfehler beim Laden des Ergebnisses');
    }
  };

  const deleteResult = async (resultId) => {
    if (!window.confirm('Sind Sie sicher, dass Sie dieses Ergebnis löschen möchten?')) {
      return;
    }

    try {
      const response = await fetch(`/api/seo/results/${resultId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        fetchResults();
        if (selectedResult && selectedResult.id === resultId) {
          setSelectedResult(null);
        }
      } else {
        const data = await response.json();
        setError(data.error || 'Fehler beim Löschen des Ergebnisses');
      }
    } catch (error) {
      console.error('Delete error:', error);
      setError('Netzwerkfehler beim Löschen des Ergebnisses');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('seo')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'seo'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Globe className="h-4 w-4 inline mr-2" />
                SEO-Analyse
              </button>
              <button
                onClick={() => setActiveTab('images')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'images'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Image className="h-4 w-4 inline mr-2" />
                AI-Bildgenerator
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'seo' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Analysis Form and Search */}
          <div className="lg:col-span-1 space-y-6">
            <DomainAnalysisForm onAnalysisComplete={handleAnalysisComplete} />
            
            {/* Search and Results List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="h-5 w-5" />
                  <span>Ergebnisse durchsuchen</span>
                </CardTitle>
                <CardDescription>
                  Suchen Sie nach Domain-Namen
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <form onSubmit={handleSearch} className="flex space-x-2">
                  <Input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Domain suchen..."
                    className="flex-1"
                  />
                  <Button type="submit" size="sm">
                    <Search className="h-4 w-4" />
                  </Button>
                </form>

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {loading ? (
                    <div className="text-center py-4">
                      <RefreshCw className="h-6 w-6 animate-spin mx-auto" />
                      <p className="text-sm text-gray-600 mt-2">Lade Ergebnisse...</p>
                    </div>
                  ) : results.length === 0 ? (
                    <p className="text-center text-gray-600 py-4">
                      Keine Ergebnisse gefunden
                    </p>
                  ) : (
                    results.map((result) => (
                      <div
                        key={result.id}
                        className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                        onClick={() => viewResult(result.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-sm">{result.domain}</p>
                            <p className="text-xs text-gray-600">
                              {new Date(result.created_at).toLocaleDateString('de-DE')}
                            </p>
                            <p className="text-xs text-gray-500">von {result.username}</p>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                viewResult(result.id);
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {isAdmin() && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  deleteResult(result.id);
                                }}
                              >
                                <Trash2 className="h-4 w-4 text-red-600" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex justify-between items-center pt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                    >
                      Zurück
                    </Button>
                    <span className="text-sm text-gray-600">
                      Seite {currentPage} von {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                    >
                      Weiter
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Admin Panel */}
            {isAdmin() && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="h-5 w-5" />
                    <span>Admin-Bereich</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    onClick={() => setShowUserManagement(!showUserManagement)}
                    className="w-full flex items-center space-x-2"
                  >
                    {showUserManagement ? (
                      <>
                        <ArrowLeft className="h-4 w-4" />
                        <span>Zurück zur Übersicht</span>
                      </>
                    ) : (
                      <>
                        <Users className="h-4 w-4" />
                        <span>Benutzerverwaltung</span>
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Result Display */}
          <div className="lg:col-span-2">
            {showUserManagement && isAdmin() ? (
              <UserManagement />
            ) : selectedResult ? (
              <SEOResultDisplay result={selectedResult} />
            ) : (
              <Card>
                <CardContent className="py-12">
                  <div className="text-center text-gray-600">
                    <Search className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <h3 className="text-lg font-medium mb-2">Kein Ergebnis ausgewählt</h3>
                    <p>Wählen Sie ein Ergebnis aus der Liste oder erstellen Sie eine neue Analyse.</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
        ) : (
          /* AI-Bildgenerator Tab */
          <ImageGenerator />
        )}
      </div>
    </div>
  );
};

export default Dashboard;

