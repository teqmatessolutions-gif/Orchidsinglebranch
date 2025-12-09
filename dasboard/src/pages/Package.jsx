import React, { useEffect, useState } from "react";
import api from "../services/api";
import { toast } from "react-hot-toast";
import DashboardLayout from "../layout/DashboardLayout";
import { motion } from "framer-motion";
import { getMediaBaseUrl } from "../utils/env";
import {
  Package as PackageIcon, Plus, Calendar, DollarSign,
  Save, ArrowRight, ArrowLeft, Trash2, X, Edit, Image as ImageIcon
} from 'lucide-react';

const getImageUrl = (imagePath) => {
  if (!imagePath) return 'https://placehold.co/400x300/e2e8f0/a0aec0?text=No+Image';
  if (imagePath.startsWith('http')) return imagePath;
  const baseUrl = getMediaBaseUrl();
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  return `${baseUrl}${path}`;
};

const KpiCard = ({ title, value, icon, color }) => (
  <div className={`p-6 rounded-2xl text-white shadow-lg flex items-center justify-between transition-transform duration-300 transform hover:scale-105 ${color}`}>
    <div className="flex-1">
      <h4 className="text-lg font-medium">{title}</h4>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
    <div className="text-4xl opacity-80">{icon}</div>
  </div>
);

const Card = ({ children, title, className = "" }) => (
  <div className={`bg-white p-6 rounded-2xl shadow-lg border border-gray-200 transition-shadow duration-300 hover:shadow-xl ${className}`}>
    {title && <h3 className="text-2xl font-bold text-gray-800 mb-6">{title}</h3>}
    {children}
  </div>
);

const Packages = ({ noLayout = false }) => {
  const [view, setView] = useState('list');
  const [packages, setPackages] = useState([]);
  const [allRooms, setAllRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: 0,
    booking_type: 'room_type',
    selected_room_types: [],
    theme: '',
    default_adults: 2,
    default_children: 0,
    max_stay_days: null,
    food_included: [],
    food_timing: {},
    images: []
  });
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [selectedPackageImages, setSelectedPackageImages] = useState(null);

  const fetchData = async () => {
    try {
      const [packageRes, roomRes, bookingRes] = await Promise.all([
        api.get(`/packages/?_t=${Date.now()}`),
        api.get("/rooms/"),
        api.get("/packages/bookingsall")
      ]);
      setPackages(packageRes.data || []);
      setAllRooms(roomRes.data || []);
      setBookings(bookingRes.data || []);
    } catch (err) {
      toast.error("Failed to load data.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleImageChange = e => {
    const files = Array.from(e.target.files);
    setSelectedFiles(prev => [...prev, ...files]);
    setImagePreviews(prev => [...prev, ...files.map(f => URL.createObjectURL(f))]);
  };

  const handleRemoveImage = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleWizardSubmit = async () => {
    try {
      const data = new FormData();
      data.append("title", formData.title);
      data.append("description", formData.description);
      data.append("price", formData.price);
      data.append("booking_type", formData.booking_type);

      if (view === 'create' && selectedFiles.length === 0 && (!formData.images || formData.images.length === 0)) {
        toast.error("Please upload at least one image for the package.");
        return;
      }

      if (formData.booking_type === "room_type") {
        if (!formData.selected_room_types || formData.selected_room_types.length === 0) {
          toast.error("Please select at least one room type");
          return;
        }
        data.append("room_types", formData.selected_room_types.join(","));
      }

      if (formData.theme) data.append("theme", formData.theme);
      data.append("default_adults", formData.default_adults || 2);
      data.append("default_children", formData.default_children || 0);
      if (formData.max_stay_days) data.append("max_stay_days", formData.max_stay_days);
      if (formData.food_included && formData.food_included.length > 0) {
        data.append("food_included", formData.food_included.join(","));
        // Send timing as JSON string
        data.append("food_timing", JSON.stringify(formData.food_timing));
      }

      selectedFiles.forEach(img => data.append("images", img));

      if (view === 'edit' && formData.id) {
        await api.put(`/packages/${formData.id}`, data);
        toast.success("Package updated successfully!");
      } else {
        await api.post("/packages/", data);
        toast.success("Package created successfully!");
      }

      setView('list');
      setStep(1);
      setSelectedFiles([]);
      setImagePreviews([]);
      fetchData();
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.detail || "Failed to save package");
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Package Name *</label>
          <input type="text" value={formData.title} onChange={(e) => handleInputChange('title', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="e.g. Honeymoon Package" />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea value={formData.description} onChange={(e) => handleInputChange('description', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" rows="3" placeholder="Describe what's included in this package..." />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
          <select value={formData.theme} onChange={(e) => handleInputChange('theme', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
            <option value="">Select Theme (Optional)</option>
            <option value="Romance">Romance</option>
            <option value="Wellness">Wellness</option>
            <option value="Adventure">Adventure</option>
            <option value="Family">Family</option>
            <option value="Business">Business</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Booking Type</label>
          <select value={formData.booking_type} onChange={(e) => handleInputChange('booking_type', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
            <option value="room_type">Selected Room Types</option>
            <option value="whole_property">Whole Property</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Default Adults</label>
          <input type="number" min="1" value={formData.default_adults} onChange={(e) => handleInputChange('default_adults', parseInt(e.target.value) || 1)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" />
          <p className="text-xs text-gray-500 mt-1">Suggested number of adults</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Default Children</label>
          <input type="number" min="0" value={formData.default_children} onChange={(e) => handleInputChange('default_children', parseInt(e.target.value) || 0)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" />
          <p className="text-xs text-gray-500 mt-1">Suggested number of children</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Maximum Stay (Days)</label>
          <input type="number" min="1" value={formData.max_stay_days || ''} onChange={(e) => handleInputChange('max_stay_days', e.target.value ? parseInt(e.target.value) : null)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Leave empty for unlimited" />
          <p className="text-xs text-gray-500 mt-1">Maximum booking duration</p>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Food Included</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {['Breakfast', 'Lunch', 'Dinner', 'Snacks'].map(meal => (
              <div key={meal} className="flex flex-col gap-2 p-2 border rounded-lg hover:bg-gray-50 transition-colors">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={formData.food_included.includes(meal)} onChange={(e) => {
                    const newMeals = e.target.checked ? [...formData.food_included, meal] : formData.food_included.filter(m => m !== meal);
                    handleInputChange('food_included', newMeals);
                    // Set default time if checked
                    if (e.target.checked && !formData.food_timing?.[meal]) {
                      const defaults = { 'Breakfast': '08:00', 'Lunch': '13:00', 'Dinner': '20:00', 'Snacks': '16:00' };
                      handleInputChange('food_timing', { ...formData.food_timing, [meal]: defaults[meal] || '08:00' });
                    }
                  }} className="rounded text-indigo-600 focus:ring-indigo-500" />
                  <span className="text-sm font-medium text-gray-700">{meal}</span>
                </label>
                {formData.food_included.includes(meal) && (
                  <div className="pl-6 animate-fadeIn">
                    <label className="text-xs text-gray-500 block mb-1">Schedule Time</label>
                    <input
                      type="time"
                      value={formData.food_timing?.[meal] || ''}
                      onChange={(e) => handleInputChange('food_timing', { ...formData.food_timing, [meal]: e.target.value })}
                      className="w-full text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-1">Select meals included in this package</p>
        </div>
        {formData.booking_type === 'room_type' && (
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Room Types *</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 p-3 bg-gray-50 rounded-lg border">
              {Array.from(new Set(allRooms.map(r => r.type))).map(type => (
                <label key={type} className="flex items-center space-x-2">
                  <input type="checkbox" checked={formData.selected_room_types.includes(type)} onChange={(e) => {
                    const newTypes = e.target.checked ? [...formData.selected_room_types, type] : formData.selected_room_types.filter(t => t !== type);
                    handleInputChange('selected_room_types', newTypes);
                  }} className="rounded text-indigo-600" />
                  <span className="text-sm">{type}</span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Package Price (₹) *</label>
          <input type="number" value={formData.price} onChange={(e) => handleInputChange('price', parseFloat(e.target.value))} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Enter package price" />
          <p className="text-xs text-gray-500 mt-1">{formData.booking_type === 'whole_property' ? 'Total price for the entire property' : 'Price per room per night'}</p>
          <p className="text-xs text-gray-400 mt-1">Tax will be calculated during billing</p>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Package Images * {view === 'edit' && '(Upload new images to add more)'}</label>
          <input type="file" multiple accept="image/*" onChange={handleImageChange} className="w-full mb-4" />
          <div className="flex gap-4 flex-wrap">
            {view === 'edit' && formData.images && formData.images.map((img, idx) => (
              <div key={`existing-${idx}`} className="relative w-24 h-24 group">
                <img src={getImageUrl(img.image_url)} alt="Existing" className="w-full h-full object-cover rounded-lg border border-gray-200" />
              </div>
            ))}
            {imagePreviews.map((src, index) => (
              <div key={`new-${index}`} className="relative w-24 h-24 group">
                <img src={src} alt="Preview" className="w-full h-full object-cover rounded-lg border border-indigo-200 shadow-sm" />
                <button onClick={() => handleRemoveImage(index)} className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs shadow-md hover:bg-red-600 transition-colors">
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
          {selectedFiles.length === 0 && (!formData.images || formData.images.length === 0) && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-2">
              <ImageIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-yellow-800">Please upload at least one image for the package</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const content = (
    <>
      {selectedPackageImages && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" onClick={() => setSelectedPackageImages(null)}>
          <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-800">{selectedPackageImages.title}</h2>
                <button onClick={() => setSelectedPackageImages(null)} className="text-gray-500 hover:text-gray-800"><X className="w-6 h-6" /></button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedPackageImages.images.map((img, idx) => (
                  <img key={idx} src={getImageUrl(img.image_url)} alt="" className="w-full h-64 object-cover rounded-lg" />
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      )}
      {view === 'list' ? (
        <>
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800">Package Management</h1>
            <button onClick={() => { setView('create'); setFormData({ title: '', description: '', price: 0, booking_type: 'room_type', selected_room_types: [], theme: '', default_adults: 2, default_children: 0, max_stay_days: null, food_included: [], images: [] }); setSelectedFiles([]); setImagePreviews([]); }} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 shadow-sm">
              <Plus className="w-5 h-5" /> Create Package
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <KpiCard title="Total Packages" value={packages.length} color="bg-gradient-to-r from-blue-500 to-blue-700" icon={<PackageIcon />} />
            <KpiCard title="Total Bookings" value={bookings.length} color="bg-gradient-to-r from-green-500 to-green-700" icon={<Calendar />} />
            <KpiCard title="Total Revenue" value={`₹${bookings.reduce((sum, b) => sum + (b.package?.price || 0), 0).toLocaleString()}`} color="bg-gradient-to-r from-purple-500 to-purple-700" icon={<DollarSign />} />
          </div>
          <Card title="Available Packages">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {packages.map(pkg => (
                <motion.div key={pkg.id} whileHover={{ y: -5 }} className="bg-gray-50 rounded-xl shadow-md overflow-hidden border border-gray-200 hover:shadow-lg transition-all duration-300 flex flex-col">
                  {pkg.images && pkg.images.length > 0 ? (
                    <img className="h-48 w-full object-cover cursor-pointer" src={getImageUrl(pkg.images[0].image_url)} alt={pkg.title} onClick={() => setSelectedPackageImages(pkg)} />
                  ) : (
                    <div className="h-48 w-full bg-gray-200 flex items-center justify-center"><span className="text-gray-500">No Image</span></div>
                  )}
                  <div className="p-6 flex flex-col flex-grow">
                    <h4 className="font-bold text-xl mb-2 text-gray-800">{pkg.title}</h4>
                    <p className="text-gray-600 text-base mb-3 flex-grow">{pkg.description}</p>
                    <div className="text-sm text-gray-500 mb-3">
                      {pkg.theme && <div><span className="font-medium">Theme:</span> {pkg.theme}</div>}
                      <div><span className="font-medium">Type:</span> {pkg.booking_type === 'whole_property' ? 'Whole Property' : 'Room Type'}</div>
                      {pkg.room_types && <div><span className="font-medium">Rooms:</span> {pkg.room_types}</div>}
                      {pkg.food_included && <div><span className="font-medium">Food:</span> {pkg.food_included}</div>}
                      <div><span className="font-medium">Guests:</span> {pkg.default_adults || 2} Adults, {pkg.default_children || 0} Children</div>
                      {pkg.max_stay_days && <div><span className="font-medium">Max Stay:</span> {pkg.max_stay_days} days</div>}
                    </div>
                    <div className="flex justify-between items-center mt-auto pt-4 border-t border-gray-200">
                      <p className="text-green-600 font-bold text-2xl">₹{pkg.price.toLocaleString()}</p>
                      <div className="flex gap-2">
                        <button onClick={() => {
                          let timing = {};
                          try { timing = pkg.food_timing ? JSON.parse(pkg.food_timing) : {}; } catch (e) { console.error("Error parsing timing", e); }

                          setView('edit');
                          setFormData({
                            ...pkg,
                            selected_room_types: pkg.room_types ? pkg.room_types.split(',') : [],
                            food_included: pkg.food_included ? pkg.food_included.split(',') : [],
                            food_timing: timing,
                            theme: pkg.theme || '',
                            default_adults: pkg.default_adults || 2,
                            default_children: pkg.default_children || 0,
                            max_stay_days: pkg.max_stay_days || null
                          });
                          setSelectedFiles([]);
                          setImagePreviews([]);
                        }} className="text-blue-500 hover:text-blue-700 font-semibold">Edit</button>
                        <button onClick={() => { if (window.confirm('Delete this package?')) api.delete(`/packages/${pkg.id}`).then(fetchData); }} className="text-red-500 hover:text-red-700 font-semibold">Delete</button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
          <Card title="All Package Bookings" className="mt-8">
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guest</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Package</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check-in</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check-out</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {bookings.map(b => (
                    <tr key={b.id}>
                      <td className="px-4 py-3">{b.guest_name}</td>
                      <td className="px-4 py-3">{b.package?.title}</td>
                      <td className="px-4 py-3">{b.check_in}</td>
                      <td className="px-4 py-3">{b.check_out}</td>
                      <td className="px-4 py-3 capitalize">{b.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      ) : (
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <button onClick={() => { setView('list'); setSelectedFiles([]); setImagePreviews([]); }} className="text-gray-500 hover:text-gray-700 flex items-center gap-1 mb-4">
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <h1 className="text-2xl font-bold text-gray-800">{view === 'create' ? 'Create New Package' : 'Edit Package'}</h1>
            <div className="mt-6 flex items-center justify-between relative">
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1 bg-gray-200 -z-10"></div>
              {[{ num: 1, label: 'Details', icon: Edit }, { num: 2, label: 'Pricing & Images', icon: DollarSign }].map((s) => (
                <div key={s.num} className="flex flex-col items-center bg-white px-2">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${step >= s.num ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white border-gray-300 text-gray-400'}`}>
                    <s.icon className="w-5 h-5" />
                  </div>
                  <span className={`text-xs font-medium mt-2 ${step >= s.num ? 'text-indigo-600' : 'text-gray-400'}`}>{s.label}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 min-h-[400px]">
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
          </div>
          <div className="mt-6 flex justify-between">
            <button onClick={() => setStep(prev => Math.max(1, prev - 1))} disabled={step === 1} className={`px-6 py-2 rounded-lg font-medium ${step === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}>Previous</button>
            {step < 2 ? (
              <button onClick={() => setStep(prev => Math.min(2, prev + 1))} className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium flex items-center gap-2">
                Next <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button onClick={handleWizardSubmit} className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center gap-2">
                <Save className="w-4 h-4" /> {view === 'create' ? 'Create' : 'Update'} Package
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );

  if (noLayout) return content;
  return <DashboardLayout>{content}</DashboardLayout>;
};

export default Packages;
