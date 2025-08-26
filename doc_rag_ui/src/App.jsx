import { useState, useEffect } from 'react';
import { Search, Plus, Trash2, FileText, Database, AlertCircle, CheckCircle, Eye, X, ChevronDown, ChevronUp } from 'lucide-react';

function App() {
  // API Base URL - easily changeable
  const API_BASE_URL = 'http://34.162.154.217:6700';
  
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('search');
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [expandedChunks, setExpandedChunks] = useState(new Set());

  // Form state for new document
  const [newDoc, setNewDoc] = useState({
    title: '',
    content: ''
  });

  // Show notification
  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification({ message: '', type: '' }), 3000);
  };

  // Fetch all documents
  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/documents`, {
        headers: { 'accept': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      } else {
        throw new Error('Failed to fetch documents');
      }
    } catch (error) {
      showNotification(`Error fetching documents: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Search documents
  const searchDocuments = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const encodedQuery = encodeURIComponent(searchQuery);
      const response = await fetch(
        `${API_BASE_URL}/documents/search?query=${encodedQuery}&limit=5`,
        { headers: { 'accept': 'application/json' } }
      );
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data);
        showNotification(`Found ${data.length} results`, 'success');
      } else {
        throw new Error('Search failed');
      }
    } catch (error) {
      showNotification(`Search error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Ingest new document
  const ingestDocument = async () => {
    if (!newDoc.title.trim() || !newDoc.content.trim()) {
      showNotification('Please fill in both title and content', 'error');
      return;
    }

    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('title', newDoc.title);
      formData.append('content', newDoc.content);

      const response = await fetch(`${API_BASE_URL}/documents/ingest/json`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });

      if (response.ok) {
        showNotification('Document ingested successfully!', 'success');
        setNewDoc({ title: '', content: '' });
        if (activeTab === 'documents') {
          fetchDocuments();
        }
      } else {
        throw new Error('Failed to ingest document');
      }
    } catch (error) {
      showNotification(`Ingestion error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Delete document
  const deleteDocument = async (docId) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${docId}`, {
        method: 'DELETE',
        headers: { 'accept': 'application/json' }
      });

      if (response.ok) {
        showNotification('Document deleted successfully!', 'success');
        setDocuments(documents.filter(doc => doc.doc_id !== docId));
        setSearchResults(searchResults.filter(doc => doc.doc_id !== docId));
      } else {
        throw new Error('Failed to delete document');
      }
    } catch (error) {
      showNotification(`Delete error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // View document details
  const viewDocument = (doc) => {
    setSelectedDoc(doc);
    setShowModal(true);
    setExpandedChunks(new Set());
  };

  // Toggle chunk expansion
  const toggleChunk = (index) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedChunks(newExpanded);
  };

  // Load documents when switching to documents tab
  useEffect(() => {
    if (activeTab === 'documents') {
      fetchDocuments();
    }
  }, [activeTab]);

  // Document card component
  const DocumentCard = ({ doc, showScore = false }) => (
    <div className="group bg-white border border-gray-100 rounded-xl p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-base font-semibold text-gray-900 leading-snug pr-2">{doc.title}</h3>
       
      </div>
      <p className="text-sm text-gray-600 mb-4 leading-relaxed line-clamp-2">{doc.summary}</p>
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-400 font-mono">
          {doc.doc_id.substring(0, 8)}
        </span>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => viewDocument(doc)}
            className="p-1.5 text-gray-400 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            title="View"
          >
            <Eye size={14} />
          </button>
          <button
            onClick={() => deleteDocument(doc.doc_id)}
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            disabled={loading}
            title="Delete"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-white">
      {/* Slim Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Database size={20} className="text-gray-900" />
              <h1 className="text-lg font-bold text-gray-900">Quantum Docs</h1>
            </div>
            <span className="text-xs text-gray-500 font-mono">{API_BASE_URL}</span>
          </div>
        </div>
      </div>

      {/* Notification */}
      {notification.message && (
        <div className="max-w-5xl mx-auto px-4 py-3">
          <div className={`flex items-center gap-2 p-3 rounded-lg text-sm ${
            notification.type === 'error' ? 'bg-red-50 text-red-700' :
            notification.type === 'success' ? 'bg-green-50 text-green-700' :
            'bg-blue-50 text-blue-700'
          }`}>
            {notification.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
            {notification.message}
          </div>
        </div>
      )}

      {/* Slim Navigation */}
      <div className="max-w-5xl mx-auto px-4 py-4">
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
          {[
            { id: 'search', label: 'Search', icon: Search },
            { id: 'ingest', label: 'Add', icon: Plus },
            { id: 'documents', label: 'All', icon: FileText }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === tab.id 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 pb-8">
        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="space-y-6">
            <div className="bg-gray-50 rounded-xl p-6">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search quantum computing documents..."
                  className="flex-1 px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent text-sm"
                  onKeyPress={(e) => e.key === 'Enter' && searchDocuments()}
                />
                <button
                  onClick={searchDocuments}
                  disabled={loading}
                  className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-colors text-sm font-medium"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>

            {searchResults.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-4">
                  {searchResults.length} Results
                </h3>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {searchResults.map(doc => (
                    <DocumentCard key={doc.doc_id} doc={doc} showScore={true} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Add Document Tab */}
        {activeTab === 'ingest' && (
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">Title</label>
                <input
                  type="text"
                  value={newDoc.title}
                  onChange={(e) => setNewDoc({...newDoc, title: e.target.value})}
                  className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent text-sm"
                  placeholder="Document title..."
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">Content</label>
                <textarea
                  value={newDoc.content}
                  onChange={(e) => setNewDoc({...newDoc, content: e.target.value})}
                  rows={8}
                  className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent text-sm leading-relaxed resize-none"
                  placeholder="Document content..."
                />
              </div>
              <button
                onClick={ingestDocument}
                disabled={loading}
                className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-colors text-sm font-medium"
              >
                {loading ? 'Adding...' : 'Add Document'}
              </button>
            </div>
          </div>
        )}

        {/* All Documents Tab */}
        {activeTab === 'documents' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-base font-semibold text-gray-900">
                {documents.length} Documents
              </h2>
              <button
                onClick={fetchDocuments}
                disabled={loading}
                className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 text-sm font-medium transition-colors"
              >
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
            
            {documents.length === 0 ? (
              <div className="text-center py-12">
                <FileText size={32} className="mx-auto mb-3 text-gray-300" />
                <p className="text-sm text-gray-500">No documents yet</p>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {documents.map(doc => (
                  <DocumentCard key={doc.doc_id} doc={doc} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Slim Modal */}
      {showModal && selectedDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-3xl w-full max-h-[85vh] overflow-hidden">
            {/* Modal Header */}
            <div className="border-b border-gray-200 p-4 flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-900">{selectedDoc.title}</h3>
                <p className="text-xs text-gray-500 font-mono mt-1">{selectedDoc.doc_id}</p>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-4 overflow-y-auto max-h-[calc(85vh-80px)]">
              {/* Summary */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-2">Summary</h4>
                <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg">
                  {selectedDoc.summary}
                </p>
              </div>

              {/* Chunks */}
              {selectedDoc.chunks && selectedDoc.chunks.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">
                    Content Chunks ({selectedDoc.chunks.length})
                  </h4>
                  <div className="space-y-2">
                    {selectedDoc.chunks.map((chunk, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                        <button
                          onClick={() => toggleChunk(index)}
                          className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex justify-between items-center text-left transition-colors"
                        >
                          <span className="text-sm font-medium text-gray-900">
                            Chunk {index + 1}
                          </span>
                          {expandedChunks.has(index) ? (
                            <ChevronUp size={16} className="text-gray-500" />
                          ) : (
                            <ChevronDown size={16} className="text-gray-500" />
                          )}
                        </button>
                        {expandedChunks.has(index) && (
                          <div className="px-4 py-3 bg-white border-t border-gray-200">
                            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                              {chunk}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(!selectedDoc.chunks || selectedDoc.chunks.length === 0) && (
                <div className="text-center py-8 text-gray-400">
                  <FileText size={24} className="mx-auto mb-2" />
                  <p className="text-sm">No chunks available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;