import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Users, Plus, Edit, Trash2, Shield, User, Loader2 } from 'lucide-react';

const UserManagement = () => {
  const { token } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'user'
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setUsers(data);
      } else {
        setError(data.error || 'Fehler beim Laden der Benutzer');
      }
    } catch (error) {
      console.error('Fetch users error:', error);
      setError('Netzwerkfehler beim Laden der Benutzer');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const url = editingUser ? `/api/users/${editingUser.id}` : '/api/users';
      const method = editingUser ? 'PUT' : 'POST';
      
      const body = { ...formData };
      if (editingUser && !body.password) {
        delete body.password; // Don't send empty password for updates
      }

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(editingUser ? 'Benutzer erfolgreich aktualisiert' : 'Benutzer erfolgreich erstellt');
        setFormData({ username: '', email: '', password: '', role: 'user' });
        setShowCreateDialog(false);
        setEditingUser(null);
        fetchUsers();
      } else {
        setError(data.error || 'Fehler beim Speichern des Benutzers');
      }
    } catch (error) {
      console.error('Save user error:', error);
      setError('Netzwerkfehler beim Speichern des Benutzers');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '',
      role: user.role
    });
    setShowCreateDialog(true);
  };

  const handleDelete = async (userId) => {
    if (!window.confirm('Sind Sie sicher, dass Sie diesen Benutzer löschen möchten?')) {
      return;
    }

    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setSuccess('Benutzer erfolgreich gelöscht');
        fetchUsers();
      } else {
        const data = await response.json();
        setError(data.error || 'Fehler beim Löschen des Benutzers');
      }
    } catch (error) {
      console.error('Delete user error:', error);
      setError('Netzwerkfehler beim Löschen des Benutzers');
    }
  };

  const resetForm = () => {
    setFormData({ username: '', email: '', password: '', role: 'user' });
    setEditingUser(null);
    setShowCreateDialog(false);
    setError('');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Benutzerverwaltung</span>
          </div>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button onClick={() => resetForm()}>
                <Plus className="h-4 w-4 mr-2" />
                Neuer Benutzer
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingUser ? 'Benutzer bearbeiten' : 'Neuen Benutzer erstellen'}
                </DialogTitle>
                <DialogDescription>
                  {editingUser 
                    ? 'Bearbeiten Sie die Benutzerdaten. Lassen Sie das Passwort leer, um es unverändert zu lassen.'
                    : 'Erstellen Sie einen neuen Benutzer für das System.'
                  }
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Benutzername</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                    disabled={loading}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">E-Mail</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    disabled={loading}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password">
                    Passwort {editingUser && '(leer lassen für keine Änderung)'}
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required={!editingUser}
                    disabled={loading}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="role">Rolle</Label>
                  <Select 
                    value={formData.role} 
                    onValueChange={(value) => setFormData({ ...formData, role: value })}
                    disabled={loading}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Rolle auswählen" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user">Benutzer</SelectItem>
                      <SelectItem value="admin">Administrator</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={resetForm}
                    disabled={loading}
                  >
                    Abbrechen
                  </Button>
                  <Button type="submit" disabled={loading}>
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Speichern...
                      </>
                    ) : (
                      editingUser ? 'Aktualisieren' : 'Erstellen'
                    )}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </CardTitle>
        <CardDescription>
          Verwalten Sie Benutzerkonten und deren Berechtigungen
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {success && (
          <Alert className="mb-4">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {loading && !users.length ? (
          <div className="text-center py-8">
            <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
            <p className="text-sm text-gray-600">Lade Benutzer...</p>
          </div>
        ) : (
          <div className="space-y-3">
            {users.map((user) => (
              <div key={user.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  {user.role === 'admin' ? (
                    <Shield className="h-5 w-5 text-blue-600" />
                  ) : (
                    <User className="h-5 w-5 text-gray-600" />
                  )}
                  <div>
                    <p className="font-medium">{user.username}</p>
                    <p className="text-sm text-gray-600">{user.email}</p>
                  </div>
                  <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                    {user.role === 'admin' ? 'Administrator' : 'Benutzer'}
                  </Badge>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(user)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(user.id)}
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UserManagement;

