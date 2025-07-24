import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Copy, CheckCircle, Globe, Calendar, Building, Clock, Users } from 'lucide-react';

const SEOResultDisplay = ({ result }) => {
  const [copiedField, setCopiedField] = useState('');

  const copyToClipboard = async (text, fieldName) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(fieldName);
      setTimeout(() => setCopiedField(''), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!result) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="h-5 w-5" />
            <span>{result.domain}</span>
          </CardTitle>
          <CardDescription className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <Calendar className="h-4 w-4" />
              <span>{formatDate(result.created_at)}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Users className="h-4 w-4" />
              <span>{result.username}</span>
            </span>
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Short Description */}
      {result.short_description && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Kurzbeschreibung (max. 150 Zeichen)</CardTitle>
            <CardDescription>
              Aktuelle Länge: {result.short_description.length} Zeichen
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              value={result.short_description}
              readOnly
              className="min-h-[80px]"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(result.short_description, 'short')}
              className="flex items-center space-x-2"
            >
              {copiedField === 'short' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>{copiedField === 'short' ? 'Kopiert!' : 'Kopieren'}</span>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Long Description */}
      {result.long_description && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Langbeschreibung (ca. 750 Zeichen)</CardTitle>
            <CardDescription>
              Aktuelle Länge: {result.long_description.length} Zeichen
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              value={result.long_description}
              readOnly
              className="min-h-[120px]"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(result.long_description, 'long')}
              className="flex items-center space-x-2"
            >
              {copiedField === 'long' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>{copiedField === 'long' ? 'Kopiert!' : 'Kopieren'}</span>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Keywords */}
      {result.keywords && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">SEO Keywords</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              value={result.keywords}
              readOnly
              className="min-h-[80px]"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(result.keywords, 'keywords')}
              className="flex items-center space-x-2"
            >
              {copiedField === 'keywords' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>{copiedField === 'keywords' ? 'Kopiert!' : 'Kopieren'}</span>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Opening Hours */}
      {result.opening_hours && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-lg">
              <Clock className="h-5 w-5" />
              <span>Öffnungszeiten</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              value={result.opening_hours}
              readOnly
              className="min-h-[100px]"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(result.opening_hours, 'hours')}
              className="flex items-center space-x-2"
            >
              {copiedField === 'hours' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>{copiedField === 'hours' ? 'Kopiert!' : 'Kopieren'}</span>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Company Info */}
      {result.company_info && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-lg">
              <Building className="h-5 w-5" />
              <span>Impressum</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              value={result.company_info}
              readOnly
              className="min-h-[120px]"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(result.company_info, 'company')}
              className="flex items-center space-x-2"
            >
              {copiedField === 'company' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>{copiedField === 'company' ? 'Kopiert!' : 'Kopieren'}</span>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Copy All */}
      <Card>
        <CardContent className="pt-6">
          <Button
            onClick={() => {
              const allText = [
                `Domain: ${result.domain}`,
                result.short_description ? `Kurzbeschreibung:\n${result.short_description}` : '',
                result.long_description ? `Langbeschreibung:\n${result.long_description}` : '',
                result.keywords ? `Keywords:\n${result.keywords}` : '',
                result.opening_hours ? `Öffnungszeiten:\n${result.opening_hours}` : '',
                result.company_info ? `Impressum:\n${result.company_info}` : ''
              ].filter(Boolean).join('\n\n');
              copyToClipboard(allText, 'all');
            }}
            className="w-full"
            variant="default"
          >
            {copiedField === 'all' ? (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                Alle Daten kopiert!
              </>
            ) : (
              <>
                <Copy className="mr-2 h-4 w-4" />
                Alle Daten kopieren
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default SEOResultDisplay;

