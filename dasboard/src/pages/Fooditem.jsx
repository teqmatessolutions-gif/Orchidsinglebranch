import React, { useEffect, useState } from "react";
import DashboardLayout from "../layout/DashboardLayout";
import API from "../services/api";
import { getMediaBaseUrl } from "../utils/env";
import { ChefHat, Plus, X, ChevronDown, ChevronUp } from "lucide-react";

// Helper function to construct image URLs
const getImageUrl = (imagePath) => {
  if (!imagePath) return 'https://placehold.co/400x300/e2e8f0/a0aec0?text=No+Image';
  if (imagePath.startsWith('http')) return imagePath;
  const baseUrl = getMediaBaseUrl();
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  return `${baseUrl}${path}`;
};

const bgColors = [
  "bg-red-50",
  "bg-green-50",
  "bg-yellow-50",
  "bg-blue-100",
  "bg-purple-50",
  "bg-pink-50",
  "bg-orange-50",
];

const FoodItems = () => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [foodItems, setFoodItems] = useState([]);
  const [editingItemId, setEditingItemId] = useState(null);
  const [available, setAvailable] = useState(true);
  
  // Recipe/Ingredients state
  const [showIngredients, setShowIngredients] = useState(false);
  const [recipeName, setRecipeName] = useState("");
  const [recipeDescription, setRecipeDescription] = useState("");
  const [servings, setServings] = useState(1);
  const [prepTime, setPrepTime] = useState("");
  const [cookTime, setCookTime] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [inventoryItems, setInventoryItems] = useState([]);

  const token = localStorage.getItem("token");

  useEffect(() => {
    fetchCategories();
    fetchFoodItems();
    fetchInventoryItems();
  }, []);

  // Auto-set recipe name when food item name changes (only if recipe name is empty)
  useEffect(() => {
    if (name && !recipeName && !editingItemId) {
      setRecipeName(name);
    }
  }, [name]);

  const fetchCategories = async () => {
    try {
      const res = await API.get("/food-categories", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCategories(res.data);
    } catch (err) {
      console.error("Failed to load categories:", err);
    }
  };

  const fetchFoodItems = async () => {
    try {
      const res = await API.get("/food-items/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setFoodItems(res.data);
    } catch (err) {
      console.error("Failed to fetch items", err);
    }
  };

  const fetchInventoryItems = async () => {
    try {
      const res = await API.get("/inventory/items?limit=1000");
      setInventoryItems(res.data || []);
    } catch (err) {
      console.error("Failed to fetch inventory items", err);
      setInventoryItems([]);
    }
  };

  const handleImageChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setImages((prevImages) => [...prevImages, ...newFiles]);
    const newPreviews = newFiles.map((file) => URL.createObjectURL(file));
    setImagePreviews((prev) => [...prev, ...newPreviews]);
  };

  const handleRemoveImage = (index) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
    setImagePreviews((prev) => prev.filter((_, i) => i !== index));
  };

  const handleEdit = (item) => {
    setEditingItemId(item.id);
    setName(item.name);
    setDescription(item.description);
    setPrice(item.price);
    setSelectedCategory(item.category_id);
    setAvailable(item.available);
    setImagePreviews(item.images?.map((img) => getImageUrl(img.image_url)) || []);
    setImages([]);
    // Reset recipe fields when editing
    setShowIngredients(false);
    setRecipeName("");
    setRecipeDescription("");
    setServings(1);
    setPrepTime("");
    setCookTime("");
    setIngredients([]);
  };

  const resetForm = () => {
    setName("");
    setDescription("");
    setPrice("");
    setSelectedCategory("");
    setImages([]);
    setImagePreviews([]);
    setEditingItemId(null);
    setAvailable(true);
    // Reset recipe fields
    setShowIngredients(false);
    setRecipeName("");
    setRecipeDescription("");
    setServings(1);
    setPrepTime("");
    setCookTime("");
    setIngredients([]);
  };

  const handleAddIngredient = () => {
    setIngredients([...ingredients, {
      inventory_item_id: "",
      quantity: "",
      unit: "pcs",
      notes: ""
    }]);
  };

  const handleIngredientChange = (index, field, value) => {
    const updated = [...ingredients];
    updated[index][field] = value;
    
    // Auto-set unit from inventory item if available
    if (field === "inventory_item_id" && value) {
      const invItem = inventoryItems.find(item => item.id === parseInt(value));
      if (invItem && invItem.unit) {
        updated[index].unit = invItem.unit;
      }
    }
    
    setIngredients(updated);
  };

  const handleRemoveIngredient = (index) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("name", name);
    formData.append("description", description);
    formData.append("price", price);
    formData.append("category_id", selectedCategory);
    formData.append("available", available);
    images.forEach((img) => formData.append("images", img));

    try {
      let foodItemId;
      if (editingItemId) {
        await API.put(`/food-items/${editingItemId}/`, formData, {
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" },
        });
        foodItemId = editingItemId;
      } else {
        const response = await API.post("/food-items/", formData, {
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" },
        });
        foodItemId = response.data.id;
      }

      // Create recipe if ingredients are provided
      if (showIngredients && ingredients.length > 0 && foodItemId) {
        try {
          const recipeData = {
            food_item_id: foodItemId,
            name: recipeName || name,
            description: recipeDescription || description,
            servings: parseInt(servings) || 1,
            prep_time_minutes: prepTime ? parseInt(prepTime) : null,
            cook_time_minutes: cookTime ? parseInt(cookTime) : null,
            ingredients: ingredients
              .filter(ing => ing.inventory_item_id && ing.quantity)
              .map(ing => ({
                inventory_item_id: parseInt(ing.inventory_item_id),
                quantity: parseFloat(ing.quantity),
                unit: ing.unit || "pcs",
                notes: ing.notes || ""
              }))
          };

          if (recipeData.ingredients.length > 0) {
            await API.post("/recipes", recipeData);
            console.log("Recipe created successfully");
          }
        } catch (recipeErr) {
          console.error("Failed to create recipe:", recipeErr);
          // Don't block food item creation if recipe fails
          alert("Food item created, but recipe creation failed. You can add recipe later from Inventory → Recipe section.");
        }
      }

      fetchFoodItems();
      resetForm();
    } catch (err) {
      console.error("Failed to save food item", err);
      alert("Failed to save food item. Please try again.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;
    try {
      await API.delete(`/food-items/${id}`, { headers: { Authorization: `Bearer ${token}` } });
      fetchFoodItems();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const toggleAvailability = async (item) => {
    try {
      await API.patch(
        `/food-items/${item.id}/toggle-availability?available=${!item.available}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchFoodItems();
    } catch (err) {
      console.error("Failed to toggle availability", err);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 flex flex-col items-center gap-8">
        {/* Food Item Form */}
        <form
          onSubmit={handleSubmit}
          className="bg-white shadow-xl rounded-3xl p-8 flex flex-col md:flex-row items-center gap-8 w-full max-w-4xl"
        >
          <div className="flex-1 w-full">
            <h2 className="text-2xl font-bold mb-6 text-gray-700 text-center md:text-left">
              {editingItemId ? "Edit Food Item" : "Add Food Item"}
            </h2>

            <input
              type="text"
              placeholder="Name"
              className="w-full border rounded-xl px-4 py-3 mb-4 focus:ring-2 focus:ring-indigo-500 transition"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <textarea
              placeholder="Description"
              className="w-full border rounded-xl px-4 py-3 mb-4 focus:ring-2 focus:ring-indigo-500 transition"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
            <input
              type="number"
              placeholder="Price"
              className="w-full border rounded-xl px-4 py-3 mb-4 focus:ring-2 focus:ring-indigo-500 transition"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
            />
            <select
              className="w-full border rounded-xl px-4 py-3 mb-4 focus:ring-2 focus:ring-indigo-500 transition"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              required
            >
              <option value="">Select Category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-2 mb-4">
              <input
                type="checkbox"
                checked={available}
                onChange={() => setAvailable(!available)}
              />
              Available
            </label>

            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleImageChange}
              className="border rounded-xl px-4 py-2 mb-4"
            />

            {/* Recipe/Ingredients Section */}
            <div className="border-t pt-4 mt-4">
              <button
                type="button"
                onClick={() => setShowIngredients(!showIngredients)}
                className="w-full flex items-center justify-between p-3 bg-indigo-50 hover:bg-indigo-100 rounded-xl transition-colors"
              >
                <span className="flex items-center gap-2 font-semibold text-indigo-700">
                  <ChefHat size={20} />
                  Add Recipe & Ingredients {showIngredients ? "(Optional)" : ""}
                </span>
                {showIngredients ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </button>

              {showIngredients && (
                <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-xl">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Recipe Name
                      </label>
                      <input
                        type="text"
                        placeholder="Recipe name (defaults to food item name)"
                        className="w-full border rounded-xl px-4 py-2 focus:ring-2 focus:ring-indigo-500"
                        value={recipeName}
                        onChange={(e) => setRecipeName(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Servings
                      </label>
                      <input
                        type="number"
                        min="1"
                        placeholder="Number of servings"
                        className="w-full border rounded-xl px-4 py-2 focus:ring-2 focus:ring-indigo-500"
                        value={servings}
                        onChange={(e) => setServings(e.target.value)}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Recipe Description
                    </label>
                    <textarea
                      placeholder="Cooking instructions or recipe notes"
                      className="w-full border rounded-xl px-4 py-2 focus:ring-2 focus:ring-indigo-500"
                      rows="2"
                      value={recipeDescription}
                      onChange={(e) => setRecipeDescription(e.target.value)}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Prep Time (minutes)
                      </label>
                      <input
                        type="number"
                        min="0"
                        placeholder="Optional"
                        className="w-full border rounded-xl px-4 py-2 focus:ring-2 focus:ring-indigo-500"
                        value={prepTime}
                        onChange={(e) => setPrepTime(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Cook Time (minutes)
                      </label>
                      <input
                        type="number"
                        min="0"
                        placeholder="Optional"
                        className="w-full border rounded-xl px-4 py-2 focus:ring-2 focus:ring-indigo-500"
                        value={cookTime}
                        onChange={(e) => setCookTime(e.target.value)}
                      />
                    </div>
                  </div>

                  {/* Ingredients List */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <label className="block text-sm font-medium text-gray-700">
                        Ingredients *
                      </label>
                      <button
                        type="button"
                        onClick={handleAddIngredient}
                        className="flex items-center gap-1 px-3 py-1 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        <Plus size={16} />
                        Add Ingredient
                      </button>
                    </div>

                    <div className="space-y-3">
                      {ingredients.map((ingredient, index) => (
                        <div key={index} className="grid grid-cols-12 gap-2 items-end p-3 bg-white rounded-lg border">
                          <div className="col-span-5">
                            <label className="block text-xs text-gray-600 mb-1">Inventory Item</label>
                            <select
                              className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
                              value={ingredient.inventory_item_id}
                              onChange={(e) => handleIngredientChange(index, "inventory_item_id", e.target.value)}
                              required={ingredients.length > 0}
                            >
                              <option value="">Select Item</option>
                              {inventoryItems.map((item) => (
                                <option key={item.id} value={item.id}>
                                  {item.name} {item.item_code ? `(${item.item_code})` : ""}
                                </option>
                              ))}
                            </select>
                          </div>
                          <div className="col-span-3">
                            <label className="block text-xs text-gray-600 mb-1">Quantity</label>
                            <input
                              type="number"
                              step="0.01"
                              min="0"
                              placeholder="0.00"
                              className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
                              value={ingredient.quantity}
                              onChange={(e) => handleIngredientChange(index, "quantity", e.target.value)}
                              required={ingredients.length > 0}
                            />
                          </div>
                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Unit</label>
                            <input
                              type="text"
                              placeholder="kg, pcs, etc"
                              className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
                              value={ingredient.unit}
                              onChange={(e) => handleIngredientChange(index, "unit", e.target.value)}
                              required={ingredients.length > 0}
                            />
                          </div>
                          <div className="col-span-2 flex gap-1">
                            <button
                              type="button"
                              onClick={() => handleRemoveIngredient(index)}
                              className="w-full px-2 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                            >
                              <X size={16} className="mx-auto" />
                            </button>
                          </div>
                          {ingredient.inventory_item_id && (
                            <div className="col-span-12">
                              <label className="block text-xs text-gray-600 mb-1">Notes (optional)</label>
                              <input
                                type="text"
                                placeholder="e.g., chopped, diced"
                                className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
                                value={ingredient.notes}
                                onChange={(e) => handleIngredientChange(index, "notes", e.target.value)}
                              />
                            </div>
                          )}
                        </div>
                      ))}
                      {ingredients.length === 0 && (
                        <p className="text-sm text-gray-500 text-center py-4">
                          Click "Add Ingredient" to add inventory items needed for this recipe
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-4 flex-wrap mb-4">
              {imagePreviews.map((src, index) => (
                <div key={index} className="relative group">
                  <img
                    src={src}
                    alt={`Preview ${index}`}
                    className="w-[100px] h-[100px] object-cover border rounded-xl shadow"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveImage(index)}
                    className="absolute top-1 right-1 bg-red-600 text-white rounded-full px-2 py-1 text-xs opacity-0 group-hover:opacity-100 transition"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>

            <button className="w-full bg-gradient-to-r from-green-500 to-green-700 text-white font-bold py-3 rounded-2xl shadow-lg hover:scale-105 transform transition">
              {editingItemId ? "Update Item" : "Add Item"}
            </button>
          </div>
        </form>

        {/* Food Items Grid */}
        <div className="w-full max-w-6xl">
          <h3 className="text-2xl font-semibold mb-6 text-gray-700 text-center">All Food Items</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {foodItems.map((item, index) => (
              <div
                key={item.id}
                className={`relative border rounded-2xl p-4 shadow hover:shadow-2xl transition ${bgColors[index % bgColors.length]} group`}
              >
                <h4 className="font-semibold text-lg">{item.name}</h4>
                <p className="text-sm text-gray-600">{item.description}</p>
                <p className="text-sm mt-1 font-medium">₹{item.price}</p>
                <p className="text-sm text-gray-700 mt-1">
                  Status:{" "}
                  <span className={item.available ? "text-green-600" : "text-red-500"}>
                    {item.available ? "Available" : "Not Available"}
                  </span>
                </p>

                <div className="flex gap-2 mt-2 flex-wrap">
                  {item.images?.map((img, idx) => (
                    <img
                      key={idx}
                      src={getImageUrl(img.image_url)}
                      alt={`Food ${idx}`}
                      className="w-[60px] h-[60px] object-cover border rounded-xl shadow-sm hover:scale-110 transition"
                    />
                  ))}
                </div>

                {/* Inline Buttons */}
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => handleEdit(item)}
                    className="flex-1 px-3 py-1 text-sm bg-blue-600 text-white rounded-xl shadow hover:bg-blue-700 transition"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="flex-1 px-3 py-1 text-sm bg-red-600 text-white rounded-xl shadow hover:bg-red-700 transition"
                  >
                    Delete
                  </button>
                  <button
                    onClick={() => toggleAvailability(item)}
                    className="flex-1 px-3 py-1 text-sm bg-yellow-600 text-white rounded-xl shadow hover:bg-yellow-700 transition"
                  >
                    Toggle Availability
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default FoodItems;
