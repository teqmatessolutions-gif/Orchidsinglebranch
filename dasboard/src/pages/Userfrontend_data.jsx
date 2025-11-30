import React, { useState, useEffect } from "react";
import DashboardLayout from "../layout/DashboardLayout";
import api from "../services/api";
import { toast } from "react-hot-toast";
import { FaStar, FaTrashAlt, FaPencilAlt, FaPlus, FaTimes, FaMapMarkerAlt, FaImage, FaInfoCircle, FaHeart, FaCamera, FaMapMarkedAlt } from "react-icons/fa";
import { AnimatePresence, motion } from "framer-motion";
import { getMediaBaseUrl } from "../utils/env";

// Get the correct base URL based on environment
const getImageUrl = (imagePath) => {
  if (!imagePath) return '';
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  const baseUrl = getMediaBaseUrl();
  let path = imagePath.trim().replace(/\\/g, '/').replace(/([^:])\/\/+/g, '$1/');
  if (!path.startsWith('/')) path = `/${path}`;
  if (!path.startsWith('/static/') && !path.startsWith('/uploads/')) {
    if (path.includes('/uploads/')) {
      path = path.replace(/^\/uploads\//, '/static/uploads/');
    } else if (path.includes('uploads/')) {
      path = `/static/${path}`;
    } else {
      const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'];
      if (imageExtensions.some(ext => path.toLowerCase().endsWith(ext))) {
        if (!path.includes('static') && !path.includes('uploads')) {
          const fileName = path.split('/').pop();
          path = `/static/uploads/${fileName}`;
        }
      }
    }
  }
  return `${baseUrl}${path}`;
};

const ensureHttpUrl = (url) => {
  if (!url) return "";
  return /^https?:\/\//i.test(url) ? url : `https://${url}`;
};

// Simplified Card Component
const ContentCard = ({ item, onEdit, onDelete, type }) => {
  const getIcon = () => {
    switch(type) {
      case 'banner': return <FaImage className="text-blue-500" />;
      case 'gallery': return <FaCamera className="text-purple-500" />;
      case 'review': return <FaStar className="text-yellow-500" />;
      case 'resortInfo': return <FaInfoCircle className="text-green-500" />;
      case 'signatureExperience': return <FaHeart className="text-pink-500" />;
      case 'planWedding': return <FaHeart className="text-red-500" />;
      case 'nearbyAttraction': return <FaMapMarkedAlt className="text-indigo-500" />;
      default: return <FaImage className="text-gray-500" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden group"
    >
      {item.image_url && (
        <div className="relative h-40 overflow-hidden">
          <img 
            src={getImageUrl(item.image_url)} 
            alt={item.title || item.caption || item.name || 'Content'} 
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            onError={(e) => {
              e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2YzZjRmNiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4=';
            }}
          />
          <div className="absolute top-2 right-2">
            {getIcon()}
          </div>
        </div>
      )}
      <div className="p-4">
        <h3 className="font-semibold text-gray-800 mb-2 line-clamp-1">
          {item.title || item.name || item.caption || 'Untitled'}
        </h3>
        {item.subtitle && <p className="text-sm text-gray-600 mb-2 line-clamp-2">{item.subtitle}</p>}
        {item.description && <p className="text-xs text-gray-500 mb-2 line-clamp-2">{item.description}</p>}
        {item.comment && <p className="text-sm text-gray-600 italic mb-2 line-clamp-2">"{item.comment}"</p>}
        {item.rating && (
          <div className="flex text-yellow-400 mb-2">
            {[...Array(5)].map((_, i) => (
              <FaStar key={i} className={i < item.rating ? 'fill-current' : 'text-gray-300'} />
            ))}
          </div>
        )}
        {item.is_active !== undefined && (
          <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold mb-2 ${
            item.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {item.is_active ? 'Active' : 'Inactive'}
          </span>
        )}
        <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100">
          <button 
            onClick={() => onEdit(item)} 
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
          >
            <FaPencilAlt size={12} /> Edit
          </button>
          <button 
            onClick={() => onDelete(item.id)} 
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
          >
            <FaTrashAlt size={12} /> Delete
          </button>
        </div>
      </div>
    </motion.div>
  );
};

// Simplified Modal
const SimpleModal = ({ isOpen, onClose, onSubmit, fields, initialData, title, isMultipart = false }) => {
  const [formState, setFormState] = useState({});
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormState(initialData);
      if (initialData.image_url) {
        setImagePreview(getImageUrl(initialData.image_url));
      }
    } else {
      setFormState({});
      setImagePreview(null);
    }
  }, [initialData, isOpen]);

  const handleFormChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    if (type === 'file' && files.length > 0) {
      setSelectedFile(files[0]);
      setImagePreview(URL.createObjectURL(files[0]));
      setFormState({ ...formState, [name]: files[0] });
    } else if (type === 'checkbox') {
      setFormState({ ...formState, [name]: checked });
    } else {
      setFormState({ ...formState, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await onSubmit(formState, selectedFile);
      onClose();
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-800">{title}</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <FaTimes size={20} />
            </button>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map(field => (
              <div key={field.name}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {field.placeholder}
                </label>
                {field.type === 'file' ? (
                  <input 
                    type="file" 
                    name={field.name} 
                    onChange={handleFormChange} 
                    accept="image/*"
                    className="w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" 
                  />
                ) : field.type === 'checkbox' ? (
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      name={field.name} 
                      checked={!!formState[field.name]} 
                      onChange={handleFormChange} 
                      className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500" 
                    />
                    <span className="text-sm text-gray-700">Active</span>
                  </label>
                ) : field.type === 'textarea' ? (
                  <textarea 
                    name={field.name} 
                    placeholder={field.placeholder} 
                    value={formState[field.name] || ''} 
                    onChange={handleFormChange} 
                    required={field.required !== false} 
                    rows={4} 
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors resize-none" 
                  />
                ) : (
                  <input 
                    type={field.type || "text"} 
                    name={field.name} 
                    placeholder={field.placeholder} 
                    value={formState[field.name] || ''} 
                    onChange={handleFormChange} 
                    required={field.required !== false} 
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors" 
                  />
                )}
              </div>
            ))}
            {imagePreview && (
              <div className="mt-4">
                <img src={imagePreview} alt="Preview" className="w-full h-48 object-cover rounded-lg shadow-md" />
              </div>
            )}
            <button 
              type="submit" 
              disabled={isLoading} 
              className="w-full mt-6 py-3 px-6 bg-indigo-600 text-white rounded-lg font-semibold shadow-md hover:bg-indigo-700 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? "Saving..." : "Save"}
            </button>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

// Main Component
export default function ResortCMS() {
  const [resortData, setResortData] = useState({
    banners: [],
    gallery: [],
    reviews: [],
    resortInfo: [],
    signatureExperiences: [],
    planWeddings: [],
    nearbyAttractions: [],
    nearbyAttractionBanners: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [modalState, setModalState] = useState({ isOpen: false, config: null, initialData: null });
  const [activeSection, setActiveSection] = useState('banners');

  const fetchAll = async () => {
    setIsLoading(true);
    try {
      const [
        bannersRes, galleryRes, reviewsRes, resortInfoRes,
        signatureExpRes, planWeddingRes, nearbyAttrRes, nearbyAttrBannerRes
      ] = await Promise.all([
        api.get("/header-banner/"),
        api.get("/gallery/"),
        api.get("/reviews/"),
        api.get("/resort-info/"),
        api.get("/signature-experiences/"),
        api.get("/plan-weddings/"),
        api.get("/nearby-attractions/"),
        api.get("/nearby-attraction-banners/"),
      ]);
      setResortData({
        banners: bannersRes.data || [],
        gallery: galleryRes.data || [],
        reviews: reviewsRes.data || [],
        resortInfo: resortInfoRes.data || [],
        signatureExperiences: signatureExpRes.data || [],
        planWeddings: planWeddingRes.data || [],
        nearbyAttractions: nearbyAttrRes.data || [],
        nearbyAttractionBanners: nearbyAttrBannerRes.data || [],
      });
    } catch (error) {
      console.error("Failed to fetch data:", error);
      toast.error("Failed to load data.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleDelete = async (endpoint, id, name) => {
    if (window.confirm(`Delete this ${name}?`)) {
      try {
        const cleanEndpoint = endpoint.endsWith('/') ? endpoint.slice(0, -1) : endpoint;
        await api.delete(`${cleanEndpoint}/${id}`);
        toast.success("Deleted successfully!");
        fetchAll();
      } catch (err) {
        toast.error(err.response?.data?.detail || `Failed to delete ${name}`);
      }
    }
  };

  const handleFormSubmit = async (config, initialData, formData, file) => {
    const isEditing = initialData && initialData.id;
    const endpoint = isEditing ? `${config.endpoint}/${initialData.id}` : config.endpoint;
    const method = isEditing ? 'put' : 'post';

    let payload = formData;
    if (config.isMultipart) {
      const data = new FormData();
      Object.keys(formData).forEach(key => {
        if (key !== 'image') {
          const value = formData[key];
          data.append(key, typeof value === 'boolean' ? String(value) : value);
        }
      });
      if (file) data.append('image', file);
      payload = data;
    } else {
      const cleanData = { ...formData };
      if (cleanData.rating !== undefined) cleanData.rating = parseInt(cleanData.rating, 10);
      if (cleanData.is_active !== undefined) {
        cleanData.is_active = cleanData.is_active === true || cleanData.is_active === 'true';
      }
      payload = cleanData;
    }

    try {
      await api({ method, url: endpoint, data: payload });
      toast.success(`${config.title} ${isEditing ? 'updated' : 'added'}!`);
      setModalState({ isOpen: false, config: null, initialData: null });
      fetchAll();
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to save ${config.title}`);
    }
  };

  const sectionConfigs = {
    banners: { 
      title: "Header Banner", 
      endpoint: "/header-banner/", 
      fields: [
        { name: "title", placeholder: "Banner Title" }, 
        { name: "subtitle", placeholder: "Banner Description" }, 
        { name: "image", type: "file" }, 
        { name: "is_active", type: "checkbox", placeholder: "Is Active?" }
      ], 
      isMultipart: true 
    },
    gallery: { 
      title: "Gallery Image", 
      endpoint: "/gallery/", 
      fields: [
        { name: "caption", placeholder: "Image Caption" }, 
        { name: "image", type: "file" }
      ], 
      isMultipart: true 
    },
    reviews: { 
      title: "Review", 
      endpoint: "/reviews/", 
      fields: [
        { name: "name", placeholder: "Customer Name" }, 
        { name: "comment", placeholder: "Review Comment", type: "textarea" }, 
        { name: "rating", placeholder: "Rating (1-5)", type: "number" }
      ], 
      isMultipart: false 
    },
    resortInfo: { 
      title: "Resort Info", 
      endpoint: "/resort-info/", 
      fields: [
        { name: "name", placeholder: "Resort Name" }, 
        { name: "address", placeholder: "Resort Address", type: "textarea" }, 
        { name: "facebook", placeholder: "Facebook URL" }, 
        { name: "instagram", placeholder: "Instagram URL" }, 
        { name: "twitter", placeholder: "Twitter URL" }, 
        { name: "linkedin", placeholder: "LinkedIn URL" }, 
        { name: "is_active", type: "checkbox", placeholder: "Is Active?" }
      ], 
      isMultipart: false 
    },
    signatureExperiences: { 
      title: "Signature Experience", 
      endpoint: "/signature-experiences/", 
      fields: [
        { name: "title", placeholder: "Experience Title" }, 
        { name: "description", placeholder: "Description", type: "textarea" }, 
        { name: "image", type: "file" }, 
        { name: "is_active", type: "checkbox", placeholder: "Is Active?" }
      ], 
      isMultipart: true 
    },
    planWeddings: { 
      title: "Plan Your Wedding", 
      endpoint: "/plan-weddings/", 
      fields: [
        { name: "title", placeholder: "Title" }, 
        { name: "description", placeholder: "Description", type: "textarea" }, 
        { name: "image", type: "file" }, 
        { name: "is_active", type: "checkbox", placeholder: "Is Active?" }
      ], 
      isMultipart: true 
    },
    nearbyAttractions: { 
      title: "Nearby Attraction", 
      endpoint: "/nearby-attractions/", 
      fields: [
        { name: "title", placeholder: "Attraction Title" }, 
        { name: "description", placeholder: "Description", type: "textarea" }, 
        { name: "map_link", placeholder: "Google Maps Link (optional)" }, 
        { name: "image", type: "file" }, 
        { name: "is_active", type: "checkbox", placeholder: "Is Active?" }
      ], 
      isMultipart: true 
    },
    nearbyAttractionBanners: { 
      title: "Nearby Attraction Banner", 
      endpoint: "/nearby-attraction-banners/", 
      fields: [
        { name: "title", placeholder: "Banner Title" }, 
        { name: "subtitle", placeholder: "Banner Subtitle", type: "textarea" }, 
        { name: "image", type: "file" }, 
        { name: "is_active", type: "checkbox", placeholder: "Is Active?" }
      ], 
      isMultipart: true 
    },
  };

  const sections = [
    { key: 'banners', label: 'Banners', icon: <FaImage />, data: resortData.banners },
    { key: 'gallery', label: 'Gallery', icon: <FaCamera />, data: resortData.gallery },
    { key: 'reviews', label: 'Reviews', icon: <FaStar />, data: resortData.reviews },
    { key: 'resortInfo', label: 'Resort Info', icon: <FaInfoCircle />, data: resortData.resortInfo },
    { key: 'signatureExperiences', label: 'Experiences', icon: <FaHeart />, data: resortData.signatureExperiences },
    { key: 'planWeddings', label: 'Weddings', icon: <FaHeart />, data: resortData.planWeddings },
    { key: 'nearbyAttractions', label: 'Attractions', icon: <FaMapMarkedAlt />, data: resortData.nearbyAttractions },
    { key: 'nearbyAttractionBanners', label: 'Attraction Banners', icon: <FaImage />, data: resortData.nearbyAttractionBanners },
  ];

  const currentSection = sections.find(s => s.key === activeSection);
  const currentConfig = sectionConfigs[activeSection];

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading content...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Website Content Management</h1>
          <p className="text-gray-600">Manage your resort website content easily</p>
        </div>

        {/* Section Tabs */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2 bg-white p-2 rounded-xl shadow-sm">
            {sections.map(section => (
              <button
                key={section.key}
                onClick={() => setActiveSection(section.key)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  activeSection === section.key
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {section.icon}
                <span>{section.label}</span>
                {section.data.length > 0 && (
                  <span className={`px-2 py-0.5 rounded-full text-xs ${
                    activeSection === section.key ? 'bg-white text-indigo-600' : 'bg-gray-200 text-gray-600'
                  }`}>
                    {section.data.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">{currentConfig?.title || 'Content'}</h2>
            <button
              onClick={() => setModalState({ isOpen: true, config: currentConfig, initialData: null })}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold shadow-md hover:bg-indigo-700 transition-all"
            >
              <FaPlus size={14} /> Add New
            </button>
          </div>

          {currentSection.data.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {currentSection.data.map(item => (
                <ContentCard
                  key={item.id}
                  item={item}
                  type={activeSection}
                  onEdit={(item) => setModalState({ isOpen: true, config: currentConfig, initialData: item })}
                  onDelete={(id) => handleDelete(currentConfig.endpoint, id, currentConfig.title)}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                {sections.find(s => s.key === activeSection)?.icon && (
                  <div className="text-6xl mb-4">
                    {sections.find(s => s.key === activeSection).icon}
                  </div>
                )}
              </div>
              <p className="text-gray-500 text-lg mb-2">No {currentConfig?.title.toLowerCase()} found</p>
              <p className="text-gray-400 text-sm">Click "Add New" to create your first item</p>
            </div>
          )}
        </div>

        {/* Modal */}
        <SimpleModal
          isOpen={modalState.isOpen}
          onClose={() => setModalState({ isOpen: false, config: null, initialData: null })}
          onSubmit={(data, file) => handleFormSubmit(modalState.config, modalState.initialData, data, file)}
          fields={modalState.config?.fields || []}
          initialData={modalState.initialData}
          title={`${modalState.initialData ? 'Edit' : 'Add'} ${modalState.config?.title}`}
          isMultipart={modalState.config?.isMultipart}
        />
      </div>
    </DashboardLayout>
  );
}
