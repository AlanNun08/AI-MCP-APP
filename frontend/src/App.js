import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // Use environment variable for backend URL
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const [currentScreen, setCurrentScreen] = useState('landing');
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [userRecipes, setUserRecipes] = useState([]);
  const [loadingRecipes, setLoadingRecipes] = useState(false);
  const [generatingRecipe, setGeneratingRecipe] = useState(false);
  const [notification, setNotification] = useState(null);

  // Notification system
  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Landing Screen Component
  const LandingScreen = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4 animate-bounce">👨‍🍳</div>
        <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg">AI Chef</h1>
        <p className="text-xl text-white mb-8 opacity-90 leading-relaxed">Personalized recipes with instant grocery delivery</p>
        <div className="space-y-4">
          <button
            onClick={() => setCurrentScreen('register')}
            className="w-full bg-white text-green-600 font-semibold py-4 px-8 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 hover:bg-gray-50 active:scale-95"
          >
            ✨ Get Started
          </button>
          <button
            onClick={() => setCurrentScreen('login')}
            className="w-full bg-transparent border-2 border-white text-white font-semibold py-4 px-8 rounded-2xl hover:bg-white hover:text-green-600 transition-all duration-200 active:scale-95"
          >
            🔑 I Have an Account
          </button>
        </div>
        <div className="mt-8 text-white/70 text-sm">
          <p>🤖 AI-powered • 🛒 Walmart delivery • 🍃 Healthy options</p>
        </div>
      </div>
    </div>
  );

  // Registration Screen Component
  const RegisterScreen = () => {
    const [formData, setFormData] = useState({
      name: '',
      email: '',
      dietary_preferences: [],
      allergies: [],
      favorite_cuisines: []
    });
    const [isCreating, setIsCreating] = useState(false);

    const dietaryOptions = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo'];
    const allergyOptions = ['nuts', 'shellfish', 'eggs', 'dairy', 'soy', 'wheat'];
    const cuisineOptions = ['italian', 'mexican', 'chinese', 'indian', 'mediterranean', 'american'];

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!formData.name || !formData.email) {
        alert('❌ Please fill in name and email');
        return;
      }

      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        alert('❌ Please enter a valid email address');
        return;
      }

      setIsCreating(true);
      try {
        const response = await axios.post(`${API}/api/users`, formData);
        setUser(response.data);
        showNotification('✅ Account created successfully! Welcome to AI Chef!', 'success');
        setCurrentScreen('dashboard');
      } catch (error) {
        console.error('Registration failed:', error);
        alert('❌ Registration failed. Please try again.');
      } finally {
        setIsCreating(false);
      }
    };

    const toggleArrayItem = (array, item, setField) => {
      const newArray = array.includes(item)
        ? array.filter(i => i !== item)
        : [...array, item];
      setField(newArray);
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">👨‍🍳</div>
            <h2 className="text-2xl font-bold text-gray-800">Create Your Account</h2>
            <p className="text-gray-600">Tell us about your preferences</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="text"
                placeholder="Your Name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <input
                type="email"
                placeholder="your.email@example.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Dietary Preferences</label>
              <div className="grid grid-cols-2 gap-2">
                {dietaryOptions.map(option => (
                  <label key={option} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.dietary_preferences.includes(option)}
                      onChange={() => toggleArrayItem(formData.dietary_preferences, option, 
                        (newArray) => setFormData({...formData, dietary_preferences: newArray}))}
                      className="rounded"
                    />
                    <span className="text-sm capitalize">{option}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Allergies</label>
              <div className="grid grid-cols-2 gap-2">
                {allergyOptions.map(option => (
                  <label key={option} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.allergies.includes(option)}
                      onChange={() => toggleArrayItem(formData.allergies, option, 
                        (newArray) => setFormData({...formData, allergies: newArray}))}
                      className="rounded"
                    />
                    <span className="text-sm capitalize">{option}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Favorite Cuisines</label>
              <div className="grid grid-cols-2 gap-2">
                {cuisineOptions.map(option => (
                  <label key={option} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.favorite_cuisines.includes(option)}
                      onChange={() => toggleArrayItem(formData.favorite_cuisines, option, 
                        (newArray) => setFormData({...formData, favorite_cuisines: newArray}))}
                      className="rounded"
                    />
                    <span className="text-sm capitalize">{option}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={isCreating}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {isCreating ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating Account...</span>
                </div>
              ) : (
                '✨ Create Account'
              )}
            </button>
          </form>

          <button
            onClick={() => setCurrentScreen('landing')}
            className="w-full mt-4 text-gray-600 hover:text-gray-800 transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  };

  // Login Screen Component
  const LoginScreen = () => {
    const [email, setEmail] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!email) {
        alert('Please enter your email');
        return;
      }

      setIsLoggingIn(true);
      try {
        // For demo purposes, create a user with this email if not exists
        const response = await axios.post(`${API}/api/users`, {
          name: email.split('@')[0],
          email: email,
          dietary_preferences: [],
          allergies: [],
          favorite_cuisines: []
        });
        setUser(response.data);
        setCurrentScreen('dashboard');
      } catch (error) {
        console.error('Login failed:', error);
        alert('Login failed. Please try again.');
      } finally {
        setIsLoggingIn(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">👨‍🍳</div>
            <h2 className="text-2xl font-bold text-gray-800">Welcome Back</h2>
            <p className="text-gray-600">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="email"
                placeholder="your.email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50"
            >
              {isLoggingIn ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          <button
            onClick={() => setCurrentScreen('landing')}
            className="w-full mt-4 text-gray-600 hover:text-gray-800 transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  };

  // Dashboard Screen Component
  const DashboardScreen = () => (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-2xl shadow-sm p-6 mb-4">
          <div className="flex items-center space-x-3 mb-6">
            <div className="text-3xl">👨‍🍳</div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">Hi, {user?.name}!</h2>
              <p className="text-gray-600 text-sm">Ready to cook something amazing?</p>
            </div>
          </div>
          
          <div className="space-y-3">
            <button
              onClick={() => setCurrentScreen('generate-recipe')}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 active:scale-95"
            >
              🎯 Generate AI Recipe
            </button>
            
            <button
              onClick={() => setCurrentScreen('all-recipes')}
              className="w-full bg-purple-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 active:scale-95"
            >
              📚 Recipe History
            </button>
          </div>
        </div>
        
        {/* Quick Stats */}
        <div className="bg-gradient-to-r from-green-100 to-blue-100 rounded-2xl p-4 mb-4">
          <h3 className="font-semibold text-gray-800 mb-2">🌟 Welcome to AI Chef!</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <p>• Generate personalized recipes with AI</p>
            <p>• Instant Walmart grocery delivery</p>
            <p>• Healthy & budget-friendly options</p>
          </div>
        </div>
        
        {/* Logout Button */}
        <button
          onClick={() => {
            setUser(null);
            setCurrentScreen('landing');
          }}
          className="w-full text-gray-500 hover:text-gray-700 transition-colors py-2"
        >
          🚪 Sign Out
        </button>
      </div>
    </div>
  );

  // Recipe Generation Screen Component
  const RecipeGenerationScreen = () => {
    const [formData, setFormData] = useState({
      cuisine_type: '',
      dietary_preferences: user?.dietary_preferences || [],
      ingredients_on_hand: '',
      servings: 2,
      difficulty: 'medium',
      is_healthy: false,
      max_calories_per_serving: '',
      is_budget: false,
      max_budget_total: ''
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (!formData.cuisine_type) {
        alert('Please select a cuisine type');
        return;
      }

      setGeneratingRecipe(true);
      try {
        const requestData = {
          user_id: user.id,
          cuisine_type: formData.cuisine_type,
          dietary_preferences: formData.dietary_preferences,
          ingredients_on_hand: formData.ingredients_on_hand ? formData.ingredients_on_hand.split(',').map(i => i.trim()) : [],
          servings: parseInt(formData.servings),
          difficulty: formData.difficulty,
          is_healthy: formData.is_healthy,
          max_calories_per_serving: formData.is_healthy ? parseInt(formData.max_calories_per_serving) : null,
          is_budget: formData.is_budget,
          max_budget_total: formData.is_budget ? parseFloat(formData.max_budget_total) : null
        };

        const response = await axios.post(`${API}/api/recipes/generate`, requestData);
        
        window.currentRecipe = response.data;
        setCurrentScreen('recipe-detail');
        
      } catch (error) {
        console.error('Recipe generation failed:', error);
        
        // Demo mode fallback
        const demoRecipe = {
          id: 'demo-' + Date.now(),
          title: `${formData.cuisine_type.charAt(0).toUpperCase() + formData.cuisine_type.slice(1)} Fusion Delight`,
          description: `A delicious ${formData.cuisine_type} recipe crafted by our AI chef. Perfect for ${formData.servings} ${formData.servings === 1 ? 'person' : 'people'}!`,
          ingredients: [
            "2 cups premium flour", 
            "1 cup filtered water", 
            "1 tsp sea salt", 
            "2 tbsp olive oil",
            "1 tsp fresh herbs",
            "½ cup seasonal vegetables"
          ],
          instructions: [
            "Prepare all ingredients and set up your workspace",
            "Mix dry ingredients in a large bowl",
            "Gradually add liquids while stirring",
            "Knead until smooth and elastic",
            "Let rest for 15 minutes",
            "Cook according to traditional method",
            "Serve hot and enjoy!"
          ],
          prep_time: 15,
          cook_time: 30,
          servings: formData.servings,
          difficulty: formData.difficulty,
          calories_per_serving: formData.is_healthy ? parseInt(formData.max_calories_per_serving) || 350 : 425,
          is_healthy: formData.is_healthy,
          user_id: user.id,
          created_at: new Date().toISOString(),
          demo: true
        };
        
        window.currentRecipe = demoRecipe;
        setCurrentScreen('recipe-detail');
      } finally {
        setGeneratingRecipe(false);
      }
    };

    const cuisineOptions = ['italian', 'mexican', 'chinese', 'indian', 'mediterranean', 'american', 'japanese', 'thai'];

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold text-gray-800">Generate Recipe</h2>
            <div></div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Cuisine Type</label>
              <select
                value={formData.cuisine_type}
                onChange={(e) => setFormData({...formData, cuisine_type: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              >
                <option value="">Select a cuisine</option>
                {cuisineOptions.map(cuisine => (
                  <option key={cuisine} value={cuisine}>
                    {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="bg-white rounded-2xl shadow-sm p-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Ingredients on Hand (optional)</label>
              <input
                type="text"
                placeholder="chicken, rice, tomatoes (comma separated)"
                value={formData.ingredients_on_hand}
                onChange={(e) => setFormData({...formData, ingredients_on_hand: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Servings</label>
                  <select
                    value={formData.servings}
                    onChange={(e) => setFormData({...formData, servings: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value={1}>1 person</option>
                    <option value={2}>2 people</option>
                    <option value={4}>4 people</option>
                    <option value={6}>6 people</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                  <select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <label className="text-sm font-medium text-gray-700">Healthy Mode</label>
                <button
                  type="button"
                  onClick={() => setFormData({...formData, is_healthy: !formData.is_healthy})}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    formData.is_healthy ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    formData.is_healthy ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              {formData.is_healthy && (
                <input
                  type="number"
                  placeholder="Enter max calories (300-700)"
                  value={formData.max_calories_per_serving}
                  onChange={(e) => setFormData({...formData, max_calories_per_serving: e.target.value})}
                  min="300"
                  max="700"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              )}
            </div>

            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <label className="text-sm font-medium text-gray-700">Budget Mode</label>
                <button
                  type="button"
                  onClick={() => setFormData({...formData, is_budget: !formData.is_budget})}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    formData.is_budget ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    formData.is_budget ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              {formData.is_budget && (
                <input
                  type="number"
                  placeholder="Enter max budget ($10-30)"
                  value={formData.max_budget_total}
                  onChange={(e) => setFormData({...formData, max_budget_total: e.target.value})}
                  min="10"
                  max="30"
                  step="0.50"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              )}
            </div>

            <button
              type="submit"
              disabled={generatingRecipe}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {generatingRecipe ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>AI is cooking up your recipe...</span>
                </div>
              ) : (
                '🤖 Generate Recipe'
              )}
            </button>
          </form>
        </div>
      </div>
    );
  };

  // Recipe Detail Screen Component
  const RecipeDetailScreen = ({ recipe, showBackButton = false }) => {
    const [showIngredients, setShowIngredients] = useState(true);
    const [groceryCart, setGroceryCart] = useState(null);
    const [generating, setGenerating] = useState(false);

    // Generate cart function
    const handleGenerateCart = async () => {
      if (!user || !recipe) {
        alert('❌ Please try again.');
        return;
      }
      
      setGenerating(true);
      setGroceryCart(null);
      
      try {
        const response = await axios.post(`${API}/api/grocery/cart-options?recipe_id=${recipe.id}&user_id=${user.id}`);
        
        const cartOptions = response.data;
        const simpleCart = {
          id: cartOptions.id,
          user_id: cartOptions.user_id,
          recipe_id: cartOptions.recipe_id,
          simple_items: cartOptions.ingredient_options.map(option => {
            if (option.options && option.options.length > 0) {
              const firstOption = option.options[0];
              return {
                name: firstOption.name,
                original_ingredient: option.original_ingredient,
                product_id: firstOption.product_id,
                price: firstOption.price,
                thumbnail: firstOption.thumbnail_image
              };
            } else {
              return {
                name: option.ingredient_name,
                original_ingredient: option.original_ingredient,
                product_id: null,
                price: 0.0,
                status: "not_found"
              };
            }
          }),
          total_price: cartOptions.ingredient_options.reduce((sum, option) => {
            return sum + (option.options && option.options.length > 0 ? option.options[0].price : 0);
          }, 0),
          walmart_url: cartOptions.ingredient_options.length > 0 ? 
            `https://affil.walmart.com/cart/addToCart?items=${cartOptions.ingredient_options.map(opt => opt.options && opt.options.length > 0 ? opt.options[0].product_id : '').filter(id => id).join(',')}` : 
            "https://walmart.com"
        };
        
        setGroceryCart(simpleCart);
        
        // Save URL to recipe
        if (recipe && recipe.id && simpleCart.walmart_url) {
          window.currentRecipe = { 
            ...recipe, 
            walmart_url: simpleCart.walmart_url, 
            cart_generated: true, 
            cart_id: simpleCart.id, 
            last_updated: new Date().toISOString() 
          };
        }
        
      } catch (error) {
        console.error('Cart generation failed:', error);
        
        // Fallback cart
        const fallbackCart = {
          id: 'fallback-cart-' + Date.now(),
          user_id: user.id,
          recipe_id: recipe.id,
          simple_items: recipe.ingredients.map((ingredient, index) => {
            const cleanName = ingredient.replace(/^\d+[\s\w\/]*\s+/, '').replace(/,.*$/, '').trim();
            return {
              name: cleanName,
              original_ingredient: ingredient,
              product_id: `fallback_${index}`,
              price: Math.floor(Math.random() * 10) + 2
            };
          }),
          walmart_url: `https://walmart.com/search?q=${encodeURIComponent(recipe.ingredients.join(' '))}`,
          total_price: recipe.ingredients.length * 5,
          fallback: true
        };
        
        setGroceryCart(fallbackCart);
        
        if (recipe && recipe.id) {
          window.currentRecipe = { 
            ...recipe, 
            walmart_url: fallbackCart.walmart_url, 
            cart_generated: true, 
            cart_id: fallbackCart.id, 
            last_updated: new Date().toISOString() 
          };
        }
      } finally {
        setGenerating(false);
      }
    };

    // Open Walmart function
    const openWalmart = (url) => {
      try {
        const link = document.createElement('a');
        link.href = url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (e) {
        navigator.clipboard.writeText(url);
        alert(`🛒 URL copied to clipboard!\n\nPaste in a new tab: ${url}`);
      }
    };

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-6">
            {showBackButton && (
              <button
                onClick={() => setCurrentScreen('all-recipes')}
                className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
              >
                ← Back
              </button>
            )}
            <h2 className="text-xl font-bold text-gray-800">Recipe Detail</h2>
            <div></div>
          </div>

          {/* Recipe Header */}
          <div className="bg-white rounded-2xl shadow-sm p-6 mb-4">
            <h1 className="text-2xl font-bold text-gray-800 mb-2">{recipe.title}</h1>
            <p className="text-gray-600 mb-4">{recipe.description}</p>
            
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>⏱️ {recipe.prep_time + recipe.cook_time}m</span>
              <span>👥 {recipe.servings}</span>
              <span>📊 {recipe.difficulty}</span>
              {recipe.calories_per_serving && (
                <span className="text-green-600">🍃 {recipe.calories_per_serving}cal</span>
              )}
            </div>
          </div>

          {/* Recipe Content */}
          <div className="bg-white rounded-2xl shadow-sm p-6 mb-4">
            <div className="flex space-x-4 border-b border-gray-200 mb-4">
              <button
                onClick={() => setShowIngredients(true)}
                className={`pb-2 px-1 ${showIngredients ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-600'}`}
              >
                Ingredients
              </button>
              <button
                onClick={() => setShowIngredients(false)}
                className={`pb-2 px-1 ${!showIngredients ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-600'}`}
              >
                Instructions
              </button>
            </div>

            {showIngredients ? (
              <div className="space-y-2">
                {recipe.ingredients.map((ingredient, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50">
                    <span className="text-sm font-medium text-green-600 min-w-[20px]">{index + 1}</span>
                    <span className="text-gray-700">{ingredient}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {recipe.instructions.map((instruction, index) => (
                  <div key={index} className="flex space-x-3 p-2 rounded-lg hover:bg-gray-50">
                    <span className="text-sm font-medium text-blue-600 min-w-[20px]">{index + 1}</span>
                    <span className="text-gray-700">{instruction}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Generating indicator */}
          {generating && (
            <div className="bg-blue-50 border border-blue-300 rounded-2xl shadow-sm p-6 mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <div>
                  <h4 className="text-blue-800 font-semibold">Finding Walmart Products...</h4>
                  <p className="text-blue-600 text-sm">Generating grocery list for your recipe</p>
                </div>
              </div>
            </div>
          )}

          {/* Check if recipe already has saved Walmart URL */}
          {recipe.walmart_url && !generating && !groceryCart ? (
            <div className="bg-green-50 border border-green-300 rounded-2xl shadow-sm p-6 mb-4">
              <div className="text-center">
                <h4 className="text-green-800 font-semibold mb-2">🛒 Cart Already Ready!</h4>
                <p className="text-green-600 text-sm mb-4">Your Walmart cart was previously generated for this recipe.</p>
                <button
                  onClick={() => openWalmart(recipe.walmart_url)}
                  className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 mb-2"
                >
                  🚀 Go to Saved Walmart Cart
                </button>
                <button
                  onClick={() => {
                    window.currentRecipe = { ...recipe, walmart_url: null, cart_generated: false };
                    handleGenerateCart();
                  }}
                  className="w-full bg-gray-500 text-white font-medium py-2 px-4 rounded-xl hover:bg-gray-600 transition-colors"
                >
                  🔄 Generate New Cart
                </button>
              </div>
            </div>
          ) : (
            /* Generate Cart Button - show when no cart exists and not generating */
            !generating && !groceryCart && (
              <button
                onClick={handleGenerateCart}
                className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 mb-4"
              >
                🛒 Generate Walmart Cart
              </button>
            )
          )}

          {/* Cart Ready State - Prominent and Easy */}
          {!generating && groceryCart && (
            <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300 rounded-2xl shadow-lg p-6 mb-4">
              <div className="text-center">
                <div className="text-4xl mb-3">🛒✨</div>
                <h3 className="text-2xl font-bold text-green-800 mb-2">Your Walmart Cart is Ready!</h3>
                <p className="text-green-700 mb-4">
                  {groceryCart.simple_items?.filter(item => item.status !== 'not_found').length || 0} items • 
                  ${groceryCart.total_price?.toFixed(2) || '0.00'} estimated total
                </p>
                
                {/* ONE-CLICK WALMART BUTTON */}
                <button
                  onClick={() => openWalmart(groceryCart.walmart_url)}
                  className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-bold text-xl py-6 px-8 rounded-2xl shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300 mb-4"
                >
                  🚀 SHOP NOW AT WALMART
                </button>
                
                {/* Quick Copy URL */}
                <div className="bg-white rounded-xl p-4 mb-4">
                  <p className="text-sm text-gray-600 mb-2">Or copy this link:</p>
                  <div className="flex items-center space-x-2">
                    <input 
                      type="text" 
                      value={groceryCart.walmart_url || ''} 
                      readOnly 
                      className="flex-1 text-xs bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 font-mono"
                      onClick={(e) => e.target.select()}
                    />
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(groceryCart.walmart_url);
                        alert('✅ Link copied to clipboard!');
                      }}
                      className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                    >
                      📋 Copy
                    </button>
                  </div>
                </div>
                
                {/* Generate New Cart Option */}
                <button
                  onClick={() => {
                    setGroceryCart(null);
                    handleGenerateCart();
                  }}
                  className="text-gray-600 hover:text-gray-800 text-sm underline"
                >
                  🔄 Generate New Cart
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // All Recipes Screen Component
  const AllRecipesScreen = () => {
    useEffect(() => {
      const fetchRecipes = async () => {
        setLoadingRecipes(true);
        try {
          // For demo purposes, use local storage or mock data
          const savedRecipes = JSON.parse(localStorage.getItem('userRecipes') || '[]');
          setUserRecipes(savedRecipes);
        } catch (error) {
          console.error('Failed to fetch recipes:', error);
          setUserRecipes([]);
        } finally {
          setLoadingRecipes(false);
        }
      };

      fetchRecipes();
    }, []);

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold text-gray-800">Recipe History</h2>
            <div></div>
          </div>

          {/* Recipes List */}
          <div className="p-4 max-w-md mx-auto">
            {loadingRecipes ? (
              <div className="text-center py-8">
                <div className="text-gray-500">Loading your recipes...</div>
              </div>
            ) : userRecipes.length > 0 ? (
              <div className="space-y-6">
                {/* Recipe Stats */}
                <div className="bg-gradient-to-r from-green-100 to-blue-100 rounded-2xl p-4">
                  <h3 className="font-semibold text-gray-800 mb-2">📊 Your Recipe Activity</h3>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-green-600">{userRecipes.length}</div>
                      <div className="text-xs text-gray-600">Total Recipes</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-blue-600">
                        {userRecipes.filter(r => r.is_healthy).length}
                      </div>
                      <div className="text-xs text-gray-600">Healthy Recipes</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-600">
                        {userRecipes.filter(r => new Date(r.created_at) > new Date(Date.now() - 7*24*60*60*1000)).length}
                      </div>
                      <div className="text-xs text-gray-600">This Week</div>
                    </div>
                  </div>
                </div>

                {/* Recent Activity */}
                <div>
                  <h3 className="font-semibold text-gray-800 mb-3">🕒 Recent Activity</h3>
                  <div className="space-y-4">
                    {userRecipes
                      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                      .map((recipe) => (
                      <div
                        key={recipe.id}
                        onClick={() => {
                          setCurrentScreen('recipe-detail');
                          window.currentRecipe = recipe;
                        }}
                        className="bg-white rounded-2xl shadow-sm p-6 hover:shadow-lg cursor-pointer transition-all border-l-4 border-green-400"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-800 mb-1">{recipe.title}</h3>
                            <p className="text-sm text-gray-600 line-clamp-2">{recipe.description}</p>
                          </div>
                          <div className="flex flex-col items-end space-y-1">
                            {recipe.is_healthy && (
                              <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
                                🍃 Healthy
                              </span>
                            )}
                            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                              🛒 Order Ready
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>⏱️ {recipe.prep_time + recipe.cook_time}m</span>
                            <span>👥 {recipe.servings}</span>
                            {recipe.calories_per_serving && (
                              <span className="text-green-600">🍃 {recipe.calories_per_serving}cal</span>
                            )}
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-gray-400">
                              {new Date(recipe.created_at).toLocaleDateString()}
                            </div>
                            <div className="text-xs text-blue-600 font-medium">
                              Click to order groceries
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">👨‍🍳</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No Recipes Yet</h3>
                <p className="text-gray-500 mb-6">Generate your first AI recipe to get started!</p>
                <button
                  onClick={() => setCurrentScreen('generate-recipe')}
                  className="bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-3 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
                >
                  🎯 Generate Your First Recipe
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Main render
  const renderScreen = () => {
    switch (currentScreen) {
      case 'landing':
        return <LandingScreen />;
      case 'register':
        return <RegisterScreen />;
      case 'login':
        return <LoginScreen />;
      case 'dashboard':
        return <DashboardScreen />;
      case 'generate-recipe':
        return <RecipeGenerationScreen />;
      case 'all-recipes':
        return <AllRecipesScreen />;
      case 'recipe-detail':
        return <RecipeDetailScreen recipe={window.currentRecipe} showBackButton={true} />;
      default:
        return <LandingScreen />;
    }
  };

  return renderScreen();
}

export default App;