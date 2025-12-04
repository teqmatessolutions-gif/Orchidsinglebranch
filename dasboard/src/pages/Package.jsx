import React, { useEffect, useState, useMemo } from "react";
import api from "../services/api";
import { toast } from "react-hot-toast";
import DashboardLayout from "../layout/DashboardLayout";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import { motion } from "framer-motion";
import { getMediaBaseUrl } from "../utils/env";
import {
  Package as PackageIcon, Plus, Calendar, DollarSign, Box, Layers, Settings,
  Save, ArrowRight, ArrowLeft, Check, Trash2, Clock, AlertCircle,
  Utensils, BedDouble, Sparkles, Coffee, Printer, Gift, X
} from 'lucide-react';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement);
// Helper function to construct image URLs
const getImageUrl = (imagePath) => {
  if (!imagePath) return 'https://placehold.co/400x300/e2e8f0/a0aec0?text=No+Image';
  if (imagePath.startsWith('http')) return imagePath;
  const baseUrl = getMediaBaseUrl();
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  return `${baseUrl}${path}`;
};

// KPI Card
const KpiCard = ({ title, value, icon, color }) => (
  <div className={`p-6 rounded-2xl text-white shadow-lg flex items-center justify-between transition-transform duration-300 transform hover:scale-105 ${color}`}>
    <div className="flex-1">
      <h4 className="text-lg font-medium">{title}</h4>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
    <div className="text-4xl opacity-80">{icon}</div>
  </div>
);

// Card Wrapper
const Card = ({ children, title, className = "" }) => (
  <div className={`bg-white p-6 rounded-2xl shadow-lg border border-gray-200 transition-shadow duration-300 hover:shadow-xl ${className}`}>
    {title && <h3 className="text-2xl font-bold text-gray-800 mb-6">{title}</h3>}
    {children}
  </div>
);

// Check-in Modal Component
const CheckInModal = ({ booking, onSave, onClose, isSubmitting, resources }) => {
  const [idCardImage, setIdCardImage] = useState(null);
  const [guestPhoto, setGuestPhoto] = useState(null);
  const [idCardPreview, setIdCardPreview] = useState(null);
  const [guestPhotoPreview, setGuestPhotoPreview] = useState(null);
  const [amenityAllocations, setAmenityAllocations] = useState([]);

  useEffect(() => {
    if (booking?.package?.inclusions) {
      let inclusions = [];
      try {
        inclusions = typeof booking.package.inclusions === 'string'
          ? JSON.parse(booking.package.inclusions)
          : booking.package.inclusions;
      } catch (e) { inclusions = []; }

      const initialAllocations = inclusions
        .filter(inc => inc.type === 'Amenity' || inc.type === 'Complimentary')
        .map(inc => ({
          item_id: inc.item_id,
          frequency: inc.schedule_type === 'Daily' ? 'Per Night' : 'Per Stay',
          comp_night: inc.schedule_type === 'Daily' ? 1 : 0,
          comp_stay: inc.schedule_type !== 'Daily' ? 1 : 0,
          extra_price: 0
        }));
      setAmenityAllocations(initialAllocations);
    }
  }, [booking]);

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (!file) return;

    const previewUrl = URL.createObjectURL(file);
    if (type === 'id') {
      setIdCardImage(file);
      setIdCardPreview(previewUrl);
    } else {
      setGuestPhoto(file);
      setGuestPhotoPreview(previewUrl);
    }
  };

  const handleAddAmenity = () => {
    setAmenityAllocations([...amenityAllocations, { item_id: '', frequency: 'Per Stay', comp_night: 0, comp_stay: 1, extra_price: 0 }]);
  };

  const handleAllocationChange = (index, field, value) => {
    const newAllocations = [...amenityAllocations];
    newAllocations[index][field] = value;
    setAmenityAllocations(newAllocations);
  };

  const handleRemoveAmenity = (index) => {
    const newAllocations = amenityAllocations.filter((_, i) => i !== index);
    setAmenityAllocations(newAllocations);
  };

  const handleSave = () => {
    if (!idCardImage || !guestPhoto) {
      toast.error("Please upload both ID card and guest photo.");
      return;
    }
    // Include amenity allocations in the save payload if needed, or just proceed with check-in
    onSave(booking.id, { id_card_image: idCardImage, guest_photo: guestPhoto, amenity_allocations: JSON.stringify(amenityAllocations) });
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center p-4 z-50">
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">Check-in Guest: {booking.guest_name}</h3>

          {/* Top Section: File Uploads */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="flex flex-col items-center">
              <label className="font-medium text-gray-700 mb-2">ID Card Image</label>
              <div className="flex items-center gap-4 w-full">
                <label className="flex-shrink-0 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg cursor-pointer hover:bg-indigo-100 font-medium transition-colors">
                  Choose File
                  <input type="file" accept="image/*" onChange={(e) => handleFileChange(e, 'id')} className="hidden" />
                </label>
                <span className="text-sm text-gray-500 truncate">{idCardImage ? idCardImage.name : "No file chosen"}</span>
              </div>
              {idCardPreview && <img src={idCardPreview} alt="ID Preview" className="mt-4 w-full h-48 object-contain rounded-lg border border-gray-200 bg-gray-50" />}
            </div>
            <div className="flex flex-col items-center">
              <label className="font-medium text-gray-700 mb-2">Guest Photo</label>
              <div className="flex items-center gap-4 w-full">
                <label className="flex-shrink-0 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg cursor-pointer hover:bg-indigo-100 font-medium transition-colors">
                  Choose File
                  <input type="file" accept="image/*" onChange={(e) => handleFileChange(e, 'guest')} className="hidden" />
                </label>
                <span className="text-sm text-gray-500 truncate">{guestPhoto ? guestPhoto.name : "No file chosen"}</span>
              </div>
              {guestPhotoPreview && <img src={guestPhotoPreview} alt="Guest Preview" className="mt-4 w-full h-48 object-contain rounded-lg border border-gray-200 bg-gray-50" />}
            </div>
          </div>

          <hr className="border-gray-200 mb-8" />

          {/* Middle Section: Amenity Allocation */}
          <div className="mb-8">
            <h4 className="text-lg font-bold text-gray-800 mb-2">Amenity Allocation for this Stay</h4>
            <p className="text-sm text-gray-500 mb-6">
              Based on package <span className="font-semibold text-gray-700">{booking.package?.title}</span>.
              Complimentary quantities are defined by the package. You can adjust limits and add extra amenities here.
            </p>

            <div className="overflow-x-auto">
              <table className="min-w-full text-sm text-left">
                <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 w-1/3">Item</th>
                    <th className="px-4 py-3">Frequency</th>
                    <th className="px-4 py-3 w-24">Comp / Night</th>
                    <th className="px-4 py-3 w-24">Comp / Stay</th>
                    <th className="px-4 py-3 w-32">Extra Price (Payable)</th>
                    <th className="px-4 py-3 w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {amenityAllocations.map((alloc, idx) => (
                    <tr key={idx} className="group hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-2">
                        <select
                          value={alloc.item_id}
                          onChange={(e) => handleAllocationChange(idx, 'item_id', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        >
                          <option value="">Select item from inventory</option>
                          {resources?.inventory?.map(item => (
                            <option key={item.id} value={item.id}>{item.name}</option>
                          ))}
                        </select>
                      </td>
                      <td className="px-4 py-2">
                        <select
                          value={alloc.frequency}
                          onChange={(e) => handleAllocationChange(idx, 'frequency', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        >
                          <option value="Per Night">Per Night</option>
                          <option value="Per Stay">Per Stay</option>
                        </select>
                      </td>
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          value={alloc.comp_night}
                          onChange={(e) => handleAllocationChange(idx, 'comp_night', parseInt(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                          disabled={alloc.frequency === 'Per Stay'}
                        />
                      </td>
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          value={alloc.comp_stay}
                          onChange={(e) => handleAllocationChange(idx, 'comp_stay', parseInt(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        />
                      </td>
                      <td className="px-4 py-2 relative">
                        <span className="absolute left-7 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
                        <input
                          type="number"
                          value={alloc.extra_price}
                          onChange={(e) => handleAllocationChange(idx, 'extra_price', parseFloat(e.target.value) || 0)}
                          className="w-full pl-6 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        />
                      </td>
                      <td className="px-4 py-2 text-center">
                        <button onClick={() => handleRemoveAmenity(idx)} className="text-gray-400 hover:text-red-500 transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <button onClick={handleAddAmenity} className="mt-4 px-4 py-2 border border-dashed border-indigo-300 text-indigo-600 rounded-lg hover:bg-indigo-50 font-medium flex items-center gap-2 transition-colors">
              <Plus className="w-4 h-4" /> Add Amenity
            </button>

            <p className="mt-4 text-xs text-gray-400 italic">
              These settings control only the allocation logic; actual stock and charges are handled from the Inventory & Billing modules.
            </p>
          </div>

          {/* Bottom Actions */}
          <div className="flex gap-4 pt-4 border-t border-gray-100">
            <button onClick={onClose} className="flex-1 bg-gray-100 text-gray-700 font-semibold py-3 rounded-xl hover:bg-gray-200 transition-colors">
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSubmitting || !idCardImage || !guestPhoto}
              className="flex-1 bg-gray-800 text-white font-semibold py-3 rounded-xl hover:bg-gray-900 transition-colors disabled:bg-gray-400 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              {isSubmitting ? "Processing..." : "Confirm Check-in"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// ... (previous imports)

// Daily Report Component
const DailyReport = ({ bookings, onClose }) => {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const reportData = useMemo(() => {
    const activeBookings = bookings.filter(b => {
      // Filter bookings that overlap with the selected date
      return b.check_in <= date && b.check_out >= date;
    });

    const stats = {
      guests: 0,
      packages: activeBookings.length,
      food: {},
      services: {},
      amenities: {},
      complimentary: {}
    };

    activeBookings.forEach(b => {
      stats.guests += (parseInt(b.adults) || 0) + (parseInt(b.children) || 0);

      let inclusions = [];
      try {
        inclusions = typeof b.package?.inclusions === 'string'
          ? JSON.parse(b.package.inclusions)
          : (b.package?.inclusions || []);
      } catch (e) { console.error("Error parsing inclusions", e); }

      inclusions.forEach(inc => {
        let shouldCount = false;
        // Logic to determine if inclusion applies to this specific date
        if (inc.schedule_type === 'Daily') {
          // Exclude check-out day for daily items usually, but let's keep it simple: active days
          if (b.check_in <= date && b.check_out > date) shouldCount = true;
        }
        else if (inc.schedule_type === 'Check-In' && b.check_in === date) shouldCount = true;
        else if (inc.schedule_type === 'Check-Out' && b.check_out === date) shouldCount = true;

        if (shouldCount) {
          const typeMap = {
            'Food': stats.food,
            'Service': stats.services,
            'Amenity': stats.amenities,
            'Complimentary': stats.complimentary
          };
          const target = typeMap[inc.type] || stats.amenities;
          target[inc.name] = (target[inc.name] || 0) + 1;
        }
      });
    });

    return stats;
  }, [bookings, date]);

  const renderSection = (title, data, icon, colorClass) => {
    const items = Object.entries(data);
    if (items.length === 0) return null;
    return (
      <div className={`bg-white p-4 rounded-xl border border-gray-100 shadow-sm ${colorClass}`}>
        <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">{icon} {title}</h4>
        <ul className="space-y-2">
          {items.map(([name, count]) => (
            <li key={name} className="flex justify-between items-center text-sm">
              <span className="text-gray-600">{name}</span>
              <span className="font-bold bg-white px-2 py-1 rounded border shadow-sm">{count}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center p-4 z-50">
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Daily Operations Report</h2>
            <p className="text-sm text-gray-500">Forecast for department heads</p>
          </div>
          <div className="flex items-center gap-4">
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="px-4 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1 hover:bg-gray-100 rounded-full transition-colors">
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto flex-1 bg-gray-50/50">
          {/* High Level Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-500 text-white p-4 rounded-xl shadow-lg">
              <div className="text-blue-100 text-xs font-medium uppercase tracking-wider">Active Packages</div>
              <div className="text-3xl font-bold mt-1">{reportData.packages}</div>
            </div>
            <div className="bg-indigo-500 text-white p-4 rounded-xl shadow-lg">
              <div className="text-indigo-100 text-xs font-medium uppercase tracking-wider">Total Guests</div>
              <div className="text-3xl font-bold mt-1">{reportData.guests}</div>
            </div>
          </div>

          {/* Department Breakdowns */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {renderSection("Kitchen / F&B", reportData.food, <Utensils className="w-5 h-5 text-orange-500" />, "border-l-4 border-l-orange-500")}
            {renderSection("Spa & Services", reportData.services, <Sparkles className="w-5 h-5 text-purple-500" />, "border-l-4 border-l-purple-500")}
            {renderSection("Housekeeping (Amenities)", reportData.amenities, <BedDouble className="w-5 h-5 text-blue-500" />, "border-l-4 border-l-blue-500")}
            {renderSection("Front Desk (Complimentary)", reportData.complimentary, <Gift className="w-5 h-5 text-green-500" />, "border-l-4 border-l-green-500")}
          </div>

          {Object.keys(reportData.food).length === 0 && Object.keys(reportData.services).length === 0 && Object.keys(reportData.amenities).length === 0 && (
            <div className="text-center py-12 text-gray-400">
              <div className="mb-2"><Calendar className="w-12 h-12 mx-auto opacity-20" /></div>
              <p>No operational requirements found for this date.</p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-100 bg-white flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition-colors">
            Close
          </button>
          <button onClick={() => window.print()} className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 flex items-center gap-2 transition-colors">
            <Printer className="w-4 h-4" /> Print Report
          </button>
        </div>
      </motion.div>
    </div>
  );
};

// --- Chart Configurations ---
const CHART_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];
const commonChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top', labels: { font: { family: 'Inter, sans-serif', size: 12 }, color: '#4b5563' } },
    tooltip: { enabled: true, backgroundColor: 'rgba(0, 0, 0, 0.8)', titleFont: { size: 14, weight: 'bold' }, bodyFont: { size: 12 }, padding: 10, cornerRadius: 8, boxPadding: 4 },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6b7280' }, border: { color: '#e5e7eb' } },
    y: { grid: { color: '#f3f4f6' }, ticks: { color: '#6b7280' }, border: { display: false } },
  },
};

const Packages = ({ noLayout = false }) => {
  // View State
  const [view, setView] = useState('list'); // 'list', 'create', 'edit'

  // Data State
  const [packages, setPackages] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [allRooms, setAllRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [resources, setResources] = useState({ inventory: [], services: [], food: [] });
  const [loading, setLoading] = useState(true);

  // Wizard State
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Hook
    title: '', // name
    code: '',
    description: '',
    theme: '',
    target_audience: '',
    booking_type: 'room_type',
    selected_room_types: [],
    default_adults: 2, // Default number of adults for this package
    default_children: 0, // Default number of children for this package

    // Step 2: Pricing
    price: 0, // base_price
    tax_rate: 18,
    revenue_split: { room: 0, fnb: 0, service: 0, other: 0 },

    // Step 3: Inclusions
    inclusions: [],

    // Step 4: Rules
    min_stay_days: 1,
    lead_time_days: 0,
    max_daily_cap: 0,
    valid_from: '',
    valid_to: '',

    images: [] // For file uploads
  });
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);

  // Booking State
  const [bookingForm, setBookingForm] = useState({
    package_id: "", guest_name: "", guest_email: "", guest_mobile: "",
    check_in: "", check_out: "", adults: 2, children: 0, room_ids: []
  });
  const [editingBooking, setEditingBooking] = useState(null);
  const [bookingToCheckIn, setBookingToCheckIn] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedPackageImages, setSelectedPackageImages] = useState(null);
  const [showReport, setShowReport] = useState(false);

  // Filters
  const [packageFilter, setPackageFilter] = useState("");
  const [bookingFilter, setBookingFilter] = useState({ guestName: "", status: "all", checkIn: "", checkOut: "" });

  // Fetch Data
  const fetchData = async () => {
    try {
      const [packageRes, roomRes, bookingRes, itemsRes, servicesRes, foodRes] = await Promise.all([
        api.get("/packages/"),
        api.get("/rooms/"),
        api.get("/packages/bookingsall"),
        api.get("/inventory/items?limit=1000").catch(() => ({ data: [] })),
        api.get("/services").catch(() => ({ data: [] })),
        api.get("/food-items/").catch(() => ({ data: [] }))
      ]);

      setPackages(packageRes.data || []);
      setAllRooms(roomRes.data || []);
      setRooms((roomRes.data || []).filter(r => r.status === "Available"));
      setBookings(bookingRes.data || []);
      setResources({
        inventory: itemsRes.data || [],
        services: servicesRes.data || [],
        food: foodRes.data || []
      });
    } catch (err) {
      toast.error("Failed to load data.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  // Wizard Handlers
  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSplitChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      revenue_split: { ...prev.revenue_split, [field]: parseFloat(value) || 0 }
    }));
  };

  const addInclusion = (inclusion) => {
    setFormData(prev => ({
      ...prev,
      inclusions: [...prev.inclusions, { ...inclusion, id: Date.now() }]
    }));
  };

  const removeInclusion = (id) => {
    setFormData(prev => ({
      ...prev,
      inclusions: prev.inclusions.filter(i => i.id !== id)
    }));
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
      // Basic Fields
      data.append("title", formData.title);
      data.append("description", formData.description);
      data.append("price", formData.price);
      data.append("booking_type", formData.booking_type);

      // Image Validation
      if (selectedFiles.length === 0 && (!formData.images || formData.images.length === 0)) {
        toast.error("Please upload at least one image for the package.");
        return;
      }

      // Room Types
      if (formData.booking_type === "room_type") {
        if (!formData.selected_room_types || formData.selected_room_types.length === 0) {
          toast.error("Please select at least one room type");
          return;
        }
        data.append("room_types", formData.selected_room_types.join(","));
      }

      // Extended Fields (Send as JSON string if backend supports, otherwise they might be ignored)
      data.append("code", formData.code);
      data.append("theme", formData.theme);
      data.append("target_audience", formData.target_audience);
      data.append("default_adults", formData.default_adults);
      data.append("default_children", formData.default_children);
      data.append("revenue_split", JSON.stringify(formData.revenue_split));
      data.append("inclusions", JSON.stringify(formData.inclusions));
      data.append("rules", JSON.stringify({
        min_stay_days: formData.min_stay_days,
        lead_time_days: formData.lead_time_days,
        max_daily_cap: formData.max_daily_cap,
        valid_from: formData.valid_from,
        valid_to: formData.valid_to
      }));

      // Images
      selectedFiles.forEach(img => data.append("images", img));

      if (view === 'edit' && formData.id) {
        await api.put(`/packages/${formData.id}`, data, { headers: { "Content-Type": "multipart/form-data" } });
        toast.success("Package updated successfully!");
      } else {
        await api.post("/packages/", data, { headers: { "Content-Type": "multipart/form-data" } });
        toast.success("Package created successfully!");
      }

      setView('list');
      setStep(1);
      fetchData();
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.detail || "Failed to save package");
    }
  };

  const handleCheckIn = async (bookingId, files) => {
    try {
      setIsSubmitting(true);
      const data = new FormData();
      data.append("id_card", files.id_card_image);
      data.append("guest_photo", files.guest_photo);

      await api.post(`/packages/checkin/${bookingId}`, data, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      toast.success("Guest checked in successfully!");
      setBookingToCheckIn(null);
      fetchData();
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.detail || "Failed to check in guest");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Wizard Render Steps
  const renderStep1 = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Package Name *</label>
          <input type="text" value={formData.title} onChange={(e) => handleInputChange('title', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="e.g. Honeymoon Bliss" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Rate Code *</label>
          <input type="text" value={formData.code} onChange={(e) => handleInputChange('code', e.target.value.toUpperCase())} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="e.g. PKG_HONEY" />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea value={formData.description} onChange={(e) => handleInputChange('description', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" rows="3" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
          <select value={formData.theme} onChange={(e) => handleInputChange('theme', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
            <option value="">Select Theme</option>
            <option value="Romance">Romance</option>
            <option value="Wellness">Wellness</option>
            <option value="Adventure">Adventure</option>
            <option value="Family">Family</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Booking Type</label>
          <select value={formData.booking_type} onChange={(e) => handleInputChange('booking_type', e.target.value)} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
            <option value="room_type">Selected Room Types</option>
            <option value="whole_property">Whole Property</option>
          </select>
        </div>

        {/* Guest Count Fields */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Default Adults</label>
          <input
            type="number"
            min="1"
            value={formData.default_adults}
            onChange={(e) => handleInputChange('default_adults', parseInt(e.target.value) || 1)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
            placeholder="Number of adults"
          />
          <p className="text-xs text-gray-500 mt-1">Default number of adults for this package</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Default Children</label>
          <input
            type="number"
            min="0"
            value={formData.default_children}
            onChange={(e) => handleInputChange('default_children', parseInt(e.target.value) || 0)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
            placeholder="Number of children"
          />
          <p className="text-xs text-gray-500 mt-1">Default number of children for this package</p>
        </div>

        {formData.booking_type === 'room_type' && (
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Room Types</label>
            <div className="grid grid-cols-3 gap-2 p-3 bg-gray-50 rounded-lg border">
              {Array.from(new Set(allRooms.map(r => r.type))).map(type => (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.selected_room_types.includes(type)}
                    onChange={(e) => {
                      const newTypes = e.target.checked
                        ? [...formData.selected_room_types, type]
                        : formData.selected_room_types.filter(t => t !== type);
                      handleInputChange('selected_room_types', newTypes);
                    }}
                    className="rounded text-indigo-600"
                  />
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Base Price (Total) *</label>
          <input type="number" value={formData.price} onChange={(e) => handleInputChange('price', parseFloat(e.target.value))} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tax Rate (%)</label>
          <input type="number" value={formData.tax_rate} onChange={(e) => handleInputChange('tax_rate', parseFloat(e.target.value))} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Final Price</label>
          <div className="w-full px-4 py-2 bg-gray-50 border rounded-lg font-bold text-gray-800">
            ₹{((formData.price || 0) * (1 + (formData.tax_rate || 0) / 100)).toFixed(2)}
          </div>
        </div>
      </div>
      <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Revenue Split</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {['room', 'fnb', 'service', 'other'].map(field => (
            <div key={field}>
              <label className="block text-xs font-medium text-gray-600 mb-1 capitalize">{field}</label>
              <input type="number" value={formData.revenue_split[field]} onChange={(e) => handleSplitChange(field, e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const [newInclusion, setNewInclusion] = useState({
    type: 'Service', item_id: '', name: '', schedule_type: 'Daily', schedule_time: '08:00', auto_trigger: true, trigger_offset_mins: 30
  });

  const renderStep3 = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Add Inclusion</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Type</label>
            <select value={newInclusion.type} onChange={(e) => setNewInclusion({ ...newInclusion, type: e.target.value, item_id: '', name: '' })} className="w-full px-3 py-2 border rounded-lg text-sm">
              <option value="Service">Service / Spa</option>
              <option value="Food">Food / Meal</option>
              <option value="Amenity">Amenity (Consumables)</option>
              <option value="Complimentary">Complimentary (Extra Bed, Music System)</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-xs font-medium text-gray-600 mb-1">Item</label>
            <select value={newInclusion.item_id} onChange={(e) => {
              const id = e.target.value;
              let name = '';
              if (newInclusion.type === 'Service') name = resources.services.find(s => s.id == id)?.name;
              else if (newInclusion.type === 'Food') name = resources.food.find(f => f.id == id)?.name;
              else if (newInclusion.type === 'Amenity' || newInclusion.type === 'Complimentary') name = resources.inventory.find(i => i.id == id)?.name;
              setNewInclusion({ ...newInclusion, item_id: id, name: name || '' });
            }} className="w-full px-3 py-2 border rounded-lg text-sm">
              <option value="">Select Item</option>
              {newInclusion.type === 'Service' && resources.services.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              {newInclusion.type === 'Food' && resources.food.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
              {(newInclusion.type === 'Amenity' || newInclusion.type === 'Complimentary') && resources.inventory.map(i => <option key={i.id} value={i.id}>{i.name}</option>)}
            </select>
            {(newInclusion.type === 'Amenity' || newInclusion.type === 'Complimentary') && (
              <p className="text-[10px] text-gray-400 mt-1">Items must be added to Inventory to appear here.</p>
            )}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Schedule</label>
            <select value={newInclusion.schedule_type} onChange={(e) => setNewInclusion({ ...newInclusion, schedule_type: e.target.value })} className="w-full px-3 py-2 border rounded-lg text-sm">
              <option value="Daily">Daily</option>
              <option value="Check-In">On Check-In</option>
              <option value="Check-Out">On Check-Out</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Time</label>
            <input type="time" value={newInclusion.schedule_time} onChange={(e) => setNewInclusion({ ...newInclusion, schedule_time: e.target.value })} className="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>
          <div className="flex items-center gap-2 pt-6">
            <input type="checkbox" checked={newInclusion.auto_trigger} onChange={(e) => setNewInclusion({ ...newInclusion, auto_trigger: e.target.checked })} className="rounded text-indigo-600" />
            <label className="text-sm text-gray-700">Auto-Trigger</label>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Offset (Mins)</label>
            <input type="number" value={newInclusion.trigger_offset_mins} onChange={(e) => setNewInclusion({ ...newInclusion, trigger_offset_mins: parseInt(e.target.value) })} className="w-full px-3 py-2 border rounded-lg text-sm" disabled={!newInclusion.auto_trigger} />
          </div>
        </div>
        <button onClick={() => { if (!newInclusion.item_id) return toast.error('Select an item'); addInclusion(newInclusion); setNewInclusion({ ...newInclusion, item_id: '', name: '' }); }} className="w-full py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 font-medium flex items-center justify-center gap-2"><Plus className="w-4 h-4" /> Add Inclusion</button>
      </div>
      <div className="space-y-3">
        {formData.inclusions.map((inc) => (
          <div key={inc.id} className="flex items-center justify-between p-4 bg-white border rounded-lg shadow-sm">
            <div>
              <h4 className="font-medium text-gray-900">{inc.name}</h4>
              <p className="text-xs text-gray-500">{inc.schedule_type} at {inc.schedule_time} {inc.auto_trigger && `• Triggers ${inc.trigger_offset_mins}m before`}</p>
            </div>
            <button onClick={() => removeInclusion(inc.id)} className="text-red-500 hover:text-red-700"><Trash2 className="w-4 h-4" /></button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Min Stay (Days)</label>
          <input type="number" value={formData.min_stay_days} onChange={(e) => handleInputChange('min_stay_days', parseInt(e.target.value))} className="w-full px-4 py-2 border rounded-lg" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Lead Time (Days)</label>
          <input type="number" value={formData.lead_time_days} onChange={(e) => handleInputChange('lead_time_days', parseInt(e.target.value))} className="w-full px-4 py-2 border rounded-lg" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Daily Cap</label>
          <input type="number" value={formData.max_daily_cap} onChange={(e) => handleInputChange('max_daily_cap', parseInt(e.target.value))} className="w-full px-4 py-2 border rounded-lg" placeholder="0 = Unlimited" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Valid From</label>
          <input type="date" value={formData.valid_from} onChange={(e) => handleInputChange('valid_from', e.target.value)} className="w-full px-4 py-2 border rounded-lg" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Valid To</label>
          <input type="date" value={formData.valid_to} onChange={(e) => handleInputChange('valid_to', e.target.value)} className="w-full px-4 py-2 border rounded-lg" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Images (At least one required)</label>
          <input type="file" multiple accept="image/*" onChange={handleImageChange} className="w-full mb-4" />

          {/* Image Previews */}
          <div className="flex gap-4 flex-wrap">
            {/* Existing Images (Edit Mode) */}
            {view === 'edit' && formData.images && formData.images.map((img, idx) => (
              <div key={`existing-${idx}`} className="relative w-24 h-24 group">
                <img src={getImageUrl(img.image_url)} alt="Existing" className="w-full h-full object-cover rounded-lg border border-gray-200" />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all rounded-lg"></div>
              </div>
            ))}

            {/* New Selected Images */}
            {imagePreviews.map((src, index) => (
              <div key={`new-${index}`} className="relative w-24 h-24 group">
                <img src={src} alt="Preview" className="w-full h-full object-cover rounded-lg border border-indigo-200 shadow-sm" />
                <button
                  onClick={() => handleRemoveImage(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs shadow-md hover:bg-red-600 transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Main Render
  const content = (
    <>
      {/* Image Gallery Modal */}
      {selectedPackageImages && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" onClick={() => setSelectedPackageImages(null)}>
          <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-800">{selectedPackageImages.title}</h2>
                <button onClick={() => setSelectedPackageImages(null)} className="text-gray-500 hover:text-gray-800"><i className="fas fa-times text-2xl"></i></button>
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
            <div className="flex gap-3">
              <button onClick={() => setShowReport(true)} className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center gap-2 shadow-sm">
                <Printer className="w-5 h-5" /> Daily Report
              </button>
              <button onClick={() => { setView('create'); setFormData({ title: '', code: '', description: '', theme: '', target_audience: '', booking_type: 'room_type', selected_room_types: [], price: 0, tax_rate: 18, revenue_split: { room: 0, fnb: 0, service: 0, other: 0 }, inclusions: [], min_stay_days: 1, lead_time_days: 0, max_daily_cap: 0, valid_from: '', valid_to: '', images: [] }); }} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 shadow-sm">
                <Plus className="w-5 h-5" /> Create Package
              </button>
            </div>
          </div>

          {/* KPI Section */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <KpiCard title="Total Packages" value={packages.length} color="bg-gradient-to-r from-blue-500 to-blue-700" icon={<PackageIcon />} />
            <KpiCard title="Total Bookings" value={bookings.length} color="bg-gradient-to-r from-green-500 to-green-700" icon={<Calendar />} />
            <KpiCard title="Total Revenue" value={`₹${bookings.reduce((sum, b) => sum + (b.package?.price || 0), 0).toLocaleString()}`} color="bg-gradient-to-r from-purple-500 to-purple-700" icon={<DollarSign />} />
          </div>

          {/* Packages List */}
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
                    <div className="flex justify-between items-center mt-auto pt-4 border-t border-gray-200">
                      <p className="text-green-600 font-bold text-2xl">₹{pkg.price.toLocaleString()}</p>
                      <div className="flex gap-2">
                        <button onClick={() => { setView('edit'); setFormData({ ...pkg, selected_room_types: pkg.room_types ? pkg.room_types.split(',') : [] }); }} className="text-blue-500 hover:text-blue-700 font-semibold">Edit</button>
                        <button onClick={() => { if (window.confirm('Delete?')) api.delete(`/packages/${pkg.id}`).then(fetchData); }} className="text-red-500 hover:text-red-700 font-semibold">Delete</button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>

          {/* Bookings Table */}
          <Card title="All Package Bookings" className="mt-8">
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guest</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Package</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {bookings.map(b => (
                    <tr key={b.id}>
                      <td className="px-4 py-3">{b.guest_name}</td>
                      <td className="px-4 py-3">{b.package?.title}</td>
                      <td className="px-4 py-3 capitalize">{b.status}</td>
                      <td className="px-4 py-3 text-center space-x-2">
                        <button onClick={() => setBookingToCheckIn(b)} className="text-green-600 hover:text-green-800 font-semibold" disabled={b.status !== 'booked'}>Check-in</button>
                      </td>
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
            <button onClick={() => setView('list')} className="text-gray-500 hover:text-gray-700 flex items-center gap-1 mb-4"><ArrowLeft className="w-4 h-4" /> Back</button>
            <h1 className="text-2xl font-bold text-gray-800">{view === 'create' ? 'Create New Package' : 'Edit Package'}</h1>
            <div className="mt-6 flex items-center justify-between relative">
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1 bg-gray-200 -z-10"></div>
              {[{ num: 1, label: 'Basics', icon: Settings }, { num: 2, label: 'Pricing', icon: DollarSign }, { num: 3, label: 'Inclusions', icon: Layers }, { num: 4, label: 'Rules', icon: Calendar }].map((s) => (
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
            {step === 3 && renderStep3()}
            {step === 4 && renderStep4()}
          </div>
          <div className="mt-6 flex justify-between">
            <button onClick={() => setStep(prev => Math.max(1, prev - 1))} disabled={step === 1} className={`px-6 py-2 rounded-lg font-medium ${step === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}>Previous</button>
            {step < 4 ? (
              <button onClick={() => setStep(prev => Math.min(4, prev + 1))} className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium flex items-center gap-2">Next <ArrowRight className="w-4 h-4" /></button>
            ) : (
              <button onClick={handleWizardSubmit} className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center gap-2"><Save className="w-4 h-4" /> {view === 'create' ? 'Create' : 'Update'} Package</button>
            )}
          </div>
        </div>
      )}

      {bookingToCheckIn && (
        <CheckInModal booking={bookingToCheckIn} onClose={() => setBookingToCheckIn(null)} onSave={handleCheckIn} isSubmitting={isSubmitting} resources={resources} />
      )}

      {showReport && (
        <DailyReport bookings={bookings} onClose={() => setShowReport(false)} />
      )}
    </>
  );

  if (noLayout) return content;
  return <DashboardLayout>{content}</DashboardLayout>;
};

export default Packages;
