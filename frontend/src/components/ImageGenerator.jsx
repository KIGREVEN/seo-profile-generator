import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Image, Download, Trash2, CheckCircle, Eye } from 'lucide-react';

const ImageGenerator = () => {
  const [userInput, setUserInput] = useState('');
  const [imageType, setImageType] = useState('header');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [generatedImage, setGeneratedImage] = useState(null);
  const [imageHistory, setImageHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    fetchImageHistory();
  }, []);

  const fetchImageHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch('/api/images/history?page=1&per_page=10', {
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        setImageHistory(data.images || []);
      } else {
        console.error('Failed to fetch image history:', data.error);
      }
    } catch (error) {
      console.error('Error fetching image history:', error);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    setGeneratedImage(null);

    try {
      const response = await fetch('/api/images/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ 
          user_input: userInput,
          image_type: imageType 
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Bild erfolgreich generiert!');
        setGeneratedImage(data.image);
        setUserInput('');
        // Refresh history
        fetchImageHistory();
      } else {
        setError(data.error || 'Bildgenerierung fehlgeschlagen');
      }
    } catch (error) {
      console.error('Image generation error:', error);
      setError('Netzwerkfehler bei der Bildgenerierung');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteImage = async (imageId) => {
    try {
      const response = await fetch(`/api/images/delete/${imageId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      if (response.ok) {
        // Remove from history
        setImageHistory(prev => prev.filter(img => img.id !== imageId));
        setSuccess('Bild erfolgreich gelöscht');
      } else {
        const data = await response.json();
        setError(data.error || 'Fehler beim Löschen des Bildes');
      }
    } catch (error) {
      console.error('Delete error:', error);
      setError('Netzwerkfehler beim Löschen');
    }
  };

  const downloadImage = async (imageUrl, filename) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || 'generated-image.png';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      setError('Fehler beim Herunterladen des Bildes');
    }
  };

  const getImageTypeLabel = (type) => {
    return type === 'header' ? 'Header (16:9)' : 'Kachel (4:3)';
  };

  const getImageTypeBadgeColor = (type) => {
    return type === 'header' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800';
  };

  return (
    <div className="space-y-6">
      {/* Generator Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Image className="h-5 w-5 text-orange-500" />
            <span>Bild-Erstellung</span>
          </CardTitle>
          <CardDescription>
            Generieren Sie professionelle Bilder mit KI für Ihre Website oder Präsentationen
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
              <Label htmlFor="imageType">Bildtyp</Label>
              <Select value={imageType} onValueChange={setImageType}>
                <SelectTrigger>
                  <SelectValue placeholder="Bildtyp auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="header">Header (16:9)</SelectItem>
                  <SelectItem value="kachel">Kachel (4:3)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="userInput">Was soll dargestellt werden?</Label>
              <Textarea
                id="userInput"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                required
                disabled={loading}
                placeholder="z. B. Klempner der eine Heizung repariert"
                rows={3}
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full text-white font-medium hover:opacity-90 transition-opacity" 
              disabled={loading || !userInput.trim()}
              style={{background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)'}}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generiere Bild...
                </>
              ) : (
                'Bild generieren'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Generated Image Display */}
      {generatedImage && (
        <Card>
          <CardHeader>
            <CardTitle>Generiertes Bild</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Badge className={getImageTypeBadgeColor(generatedImage.image_type)}>
                  {getImageTypeLabel(generatedImage.image_type)}
                </Badge>
                <span className="text-sm text-gray-600">
                  {generatedImage.image_size}
                </span>
              </div>
              
              <div className="relative">
                <img 
                  src={generatedImage.image_url} 
                  alt={generatedImage.user_input}
                  className="w-full rounded-lg shadow-lg"
                />
              </div>
              
              <div className="flex space-x-2">
                <Button 
                  onClick={() => downloadImage(generatedImage.image_url, `generated-${generatedImage.image_type}-${Date.now()}.png`)}
                  variant="outline"
                  size="sm"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Herunterladen
                </Button>
              </div>
              
              <div className="text-sm text-gray-600">
                <strong>Beschreibung:</strong> {generatedImage.user_input}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Image History */}
      <Card>
        <CardHeader>
          <CardTitle>Verlauf</CardTitle>
          <CardDescription>
            Ihre zuletzt generierten Bilder
          </CardDescription>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span className="ml-2">Lade Verlauf...</span>
            </div>
          ) : imageHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Noch keine Bilder generiert
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {imageHistory.map((image) => (
                <div key={image.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge className={getImageTypeBadgeColor(image.image_type)}>
                      {getImageTypeLabel(image.image_type)}
                    </Badge>
                    <Button
                      onClick={() => handleDeleteImage(image.id)}
                      variant="outline"
                      size="sm"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <div className="relative">
                    <img 
                      src={image.image_url} 
                      alt={image.user_input}
                      className="w-full h-32 object-cover rounded"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm font-medium truncate">
                      {image.user_input}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(image.created_at).toLocaleDateString('de-DE')}
                    </div>
                    <div className="flex space-x-1">
                      <Button 
                        onClick={() => downloadImage(image.image_url, `generated-${image.image_type}-${image.id}.png`)}
                        variant="outline"
                        size="sm"
                        className="flex-1"
                      >
                        <Download className="h-3 w-3 mr-1" />
                        Download
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ImageGenerator;

