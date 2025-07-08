import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

// Dynamic backend URL detection with fallback
const getBackendURL = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8001';
  } else {
    // For production, try the public backend URL
    return 'https://ae98d8a0-e0fa-4434-aadf-fe1df1f1101d.preview.emergentagent.com';
  }
};

const BACKEND_URL = getBackendURL();
const API = `${BACKEND_URL}/api`;

// Add axios interceptor for better error handling
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.code === 'ERR_NETWORK') {
      alert('Network error: Unable to connect to the server. Please try again.');
    }
    return Promise.reject(error);
  }
);

// Main App Component
function App() {
  const [currentScreen, setCurrentScreen] = useState('home');
  const [user, setUser] = useState(null);
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);

  // Initialize app
  useEffect(() => {
    // Check if user exists in localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setCurrentScreen('dashboard');
    }
  }, []);

  // Home Screen Component
  const HomeScreen = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-sm w-full text-center">
        <div className="mb-8">
          <div className="w-20 h-20 bg-gradient-to-r from-orange-400 to-red-500 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-3xl">🍳</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">AI Chef</h1>
          <p className="text-gray-600">Personalized recipes with instant grocery delivery</p>
        </div>
        
        <div className="space-y-4">
          <button
            onClick={() => setCurrentScreen('signup')}
            className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
          >
            Get Started
          </button>
          
          <button
            onClick={() => setCurrentScreen('login')}
            className="w-full border-2 border-gray-300 text-gray-700 font-semibold py-4 px-6 rounded-2xl hover:bg-gray-50 transition-all duration-200"
          >
            I Have an Account
          </button>
        </div>
      </div>
    </div>
  );

  // User Registration Component
  const SignupScreen = () => {
    const [formData, setFormData] = useState({
      name: '',
      email: '',
      dietary_preferences: [],
      allergies: [],
      favorite_cuisines: []
    });

    const dietaryOptions = ['vegetarian', 'vegan', 'gluten-free', 'keto', 'paleo', 'low-carb'];
    const allergyOptions = ['nuts', 'dairy', 'eggs', 'soy', 'shellfish', 'fish'];
    const cuisineOptions = ['italian', 'mexican', 'asian', 'american', 'mediterranean', 'indian'];

  const handleSubmit = async (e) => {
      e.preventDefault();
      setLoading(true);
      
      try {
        console.log('Creating user with data:', formData);
        const response = await axios.post(`${API}/users`, formData);
        const newUser = response.data;
        console.log('User created successfully:', newUser);
        
        setUser(newUser);
        localStorage.setItem('user', JSON.stringify(newUser));
        setCurrentScreen('dashboard');
      } catch (error) {
        console.error('Signup error:', error);
        alert('Failed to create account. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    const toggleOption = (field, option) => {
      setFormData(prev => ({
        ...prev,
        [field]: prev[field].includes(option)
          ? prev[field].filter(item => item !== option)
          : [...prev[field], option]
      }));
    };

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto bg-white rounded-3xl shadow-lg p-6">
          <div className="text-center mb-6">
            <button
              onClick={() => setCurrentScreen('home')}
              className="absolute top-4 left-4 p-2 text-gray-600 hover:text-gray-800"
            >
              ← Back
            </button>
            <h2 className="text-2xl font-bold text-gray-800">Tell us about yourself</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Dietary Preferences</label>
              <div className="grid grid-cols-2 gap-2">
                {dietaryOptions.map(option => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => toggleOption('dietary_preferences', option)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      formData.dietary_preferences.includes(option)
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Allergies</label>
              <div className="grid grid-cols-2 gap-2">
                {allergyOptions.map(option => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => toggleOption('allergies', option)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      formData.allergies.includes(option)
                        ? 'bg-red-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Favorite Cuisines</label>
              <div className="grid grid-cols-2 gap-2">
                {cuisineOptions.map(option => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => toggleOption('favorite_cuisines', option)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      formData.favorite_cuisines.includes(option)
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
        </div>
      </div>
    );
  };

  // Dashboard Component
  const DashboardScreen = () => {
    const [userRecipes, setUserRecipes] = useState([]);
    const [loadingRecipes, setLoadingRecipes] = useState(false);

    // Load user's recipes when dashboard mounts
    useEffect(() => {
      const loadUserRecipes = async () => {
        setLoadingRecipes(true);
        try {
          const response = await axios.get(`${API}/recipes?user_id=${user.id}`);
          setUserRecipes(response.data);
        } catch (error) {
          console.error('Error loading user recipes:', error);
        } finally {
          setLoadingRecipes(false);
        }
      };

      if (user?.id) {
        loadUserRecipes();
      }
    }, [user?.id]);

    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm p-4">
          <div className="max-w-md mx-auto flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-800">Hi, {user?.name}! 👋</h1>
              <p className="text-sm text-gray-600">What would you like to cook today?</p>
            </div>
            <button
              onClick={() => setCurrentScreen('profile')}
              className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold"
            >
              {user?.name?.[0]}
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="p-4 max-w-md mx-auto">
          <div className="space-y-4">
            {/* Generate Recipe Button */}
            <button
              onClick={() => setCurrentScreen('generate')}
              className="w-full bg-gradient-to-r from-orange-400 to-red-500 text-white font-semibold py-6 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 flex items-center justify-center space-x-3"
            >
              <span className="text-2xl">🤖</span>
              <span className="text-lg">Generate AI Recipe</span>
            </button>

            {/* My Recipes */}
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">My Recipes</h3>
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                  {userRecipes.length}
                </span>
              </div>
              
              {loadingRecipes ? (
                <div className="text-center py-4">
                  <div className="loading text-gray-500">Loading recipes...</div>
                </div>
              ) : userRecipes.length > 0 ? (
                <div className="space-y-3">
                  {userRecipes.slice(0, 3).map((recipe) => (
                    <div
                      key={recipe.id}
                      onClick={() => {
                        setCurrentScreen('recipe-detail');
                        // You'll need to pass the recipe data
                        window.currentRecipe = recipe;
                      }}
                      className="p-3 bg-gray-50 rounded-xl hover:bg-gray-100 cursor-pointer transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-800 text-sm">{recipe.title}</h4>
                          <div className="flex items-center space-x-3 mt-1">
                            <span className="text-xs text-gray-500">⏱️ {recipe.prep_time + recipe.cook_time}m</span>
                            <span className="text-xs text-gray-500">👥 {recipe.servings}</span>
                            {recipe.is_healthy && (
                              <span className="text-xs text-green-600">🍃 {recipe.calories_per_serving}cal</span>
                            )}
                          </div>
                        </div>
                        <div className="text-gray-400">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {userRecipes.length > 3 && (
                    <button
                      onClick={() => setCurrentScreen('all-recipes')}
                      className="w-full bg-blue-50 text-blue-700 font-medium py-3 px-4 rounded-xl hover:bg-blue-100 transition-all text-sm"
                    >
                      View All {userRecipes.length} Recipes
                    </button>
                  )}
                </div>
              ) : (
                <div className="text-center py-6">
                  <div className="text-4xl mb-2">📝</div>
                  <p className="text-gray-500 text-sm">No recipes yet</p>
                  <p className="text-gray-400 text-xs">Generate your first AI recipe above!</p>
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                <button className="bg-yellow-100 text-yellow-800 font-medium py-3 px-4 rounded-xl hover:bg-yellow-200 transition-all text-sm">
                  🛒 Order History
                </button>
                <button 
                  onClick={() => setCurrentScreen('all-recipes')}
                  className="bg-purple-100 text-purple-800 font-medium py-3 px-4 rounded-xl hover:bg-purple-200 transition-all text-sm"
                >
                  ❤️ All Recipes
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Recipe Generation Component
  const GenerateScreen = () => {
    const [genRequest, setGenRequest] = useState({
      cuisine_type: '',
      dietary_preferences: [],
      ingredients_on_hand: [],
      prep_time_max: '',
      servings: 4,
      difficulty: 'medium',
      // New healthy options
      is_healthy: false,
      max_calories_per_serving: 500,
      // New budget options  
      is_budget_friendly: false,
      max_budget: 25.0
    });
    const [generatedRecipe, setGeneratedRecipe] = useState(null);

    const handleGenerate = async () => {
      // Validate user is logged in
      if (!user || !user.id) {
        alert('Please log in to generate recipes');
        setCurrentScreen('home');
        return;
      }

      setLoading(true);
      try {
        console.log('Generating recipe for user:', user.id);
        console.log('Recipe request:', genRequest);
        
        const response = await axios.post(`${API}/recipes/generate`, {
          user_id: user.id,
          ...genRequest
        });
        const newRecipe = response.data;
        console.log('Recipe generated successfully:', newRecipe);
        setGeneratedRecipe(newRecipe);
        
        // Refresh user recipes in localStorage for immediate UI update
        try {
          const recipesResponse = await axios.get(`${API}/recipes?user_id=${user.id}`);
          window.userRecipes = recipesResponse.data;
          console.log('Updated user recipes:', recipesResponse.data.length);
        } catch (error) {
          console.log('Could not refresh recipes list:', error);
        }
        
      } catch (error) {
        console.error('Recipe generation error:', error);
        console.error('Error details:', error.response?.data);
        
        // If backend is not accessible, show demo recipe
        if (error.code === 'ERR_NETWORK') {
          alert('Demo Mode: Backend not accessible. Showing sample recipe.');
          const demoRecipe = {
            id: 'demo-recipe-' + Date.now(),
            title: genRequest.cuisine_type ? `${genRequest.cuisine_type.charAt(0).toUpperCase() + genRequest.cuisine_type.slice(1)} ${genRequest.is_healthy ? 'Healthy ' : ''}Demo Recipe` : 'Demo Recipe',
            description: `A delicious ${genRequest.cuisine_type || 'international'} dish perfect for ${genRequest.servings} people.${genRequest.is_healthy ? ' This healthy version contains approximately ' + genRequest.max_calories_per_serving + ' calories per serving.' : ''}`,
            ingredients: [
              '2 cups main ingredient',
              '1 onion, diced',
              '2 cloves garlic, minced',
              '2 tbsp olive oil',
              'Salt and pepper to taste',
              'Fresh herbs for garnish'
            ],
            instructions: [
              'Prepare all ingredients by washing and chopping as needed.',
              'Heat olive oil in a large pan over medium heat.',
              'Add onion and cook until translucent, about 5 minutes.',
              'Add garlic and cook for another minute until fragrant.',
              'Add main ingredient and season with salt and pepper.',
              'Cook according to ingredient requirements.',
              'Garnish with fresh herbs and serve hot.',
              'Enjoy your delicious meal!'
            ],
            prep_time: parseInt(genRequest.prep_time_max) || 15,
            cook_time: 20,
            servings: genRequest.servings,
            cuisine_type: genRequest.cuisine_type || 'international',
            dietary_tags: genRequest.dietary_preferences,
            difficulty: genRequest.difficulty,
            calories_per_serving: genRequest.is_healthy ? genRequest.max_calories_per_serving : null,
            is_healthy: genRequest.is_healthy,
            demo: true
          };
          setGeneratedRecipe(demoRecipe);
        } else {
          const errorMessage = error.response?.data?.detail || 'Failed to generate recipe. Please try again.';
          alert(`Error: ${errorMessage}`);
        }
      } finally {
        setLoading(false);
      }
    };

    if (generatedRecipe) {
      return <RecipeDetailScreen recipe={generatedRecipe} showBackButton={true} />;
    }

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto bg-white rounded-3xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="p-2 text-gray-600 hover:text-gray-800"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold text-gray-800">Generate Recipe</h2>
            <div></div>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Cuisine Type</label>
              <select
                value={genRequest.cuisine_type}
                onChange={(e) => setGenRequest({...genRequest, cuisine_type: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any cuisine</option>
                <option value="italian">Italian</option>
                <option value="mexican">Mexican</option>
                <option value="asian">Asian</option>
                <option value="american">American</option>
                <option value="mediterranean">Mediterranean</option>
                <option value="indian">Indian</option>
              </select>
            </div>

            {/* Healthy Eating Toggle */}
            <div className="bg-green-50 p-4 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium text-green-800">🍃 Healthy Recipe Mode</label>
                <button
                  type="button"
                  onClick={() => setGenRequest({...genRequest, is_healthy: !genRequest.is_healthy})}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    genRequest.is_healthy ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      genRequest.is_healthy ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {genRequest.is_healthy && (
                <div>
                  <label className="block text-xs font-medium text-green-700 mb-2">
                    Max Calories Per Serving
                  </label>
                  <select
                    value={genRequest.max_calories_per_serving}
                    onChange={(e) => setGenRequest({...genRequest, max_calories_per_serving: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
                  >
                    <option value={300}>300 calories (Very Light)</option>
                    <option value={400}>400 calories (Light)</option>
                    <option value={500}>500 calories (Moderate)</option>
                    <option value={600}>600 calories (Balanced)</option>
                    <option value={700}>700 calories (Hearty)</option>
                  </select>
                  <p className="text-xs text-green-600 mt-1">
                    AI will focus on lean proteins, vegetables, and whole grains
                  </p>
                </div>
              )}
            </div>

            {/* Budget-Friendly Toggle */}
            <div className="bg-yellow-50 p-4 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium text-yellow-800">💰 Budget-Friendly Mode</label>
                <button
                  type="button"
                  onClick={() => setGenRequest({...genRequest, is_budget_friendly: !genRequest.is_budget_friendly})}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    genRequest.is_budget_friendly ? 'bg-yellow-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      genRequest.is_budget_friendly ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              {genRequest.is_budget_friendly && (
                <div>
                  <label className="block text-xs font-medium text-yellow-700 mb-2">
                    Max Budget for Ingredients
                  </label>
                  <select
                    value={genRequest.max_budget}
                    onChange={(e) => setGenRequest({...genRequest, max_budget: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-yellow-300 rounded-lg focus:ring-2 focus:ring-yellow-500 text-sm"
                  >
                    <option value={10.0}>$10 (Ultra Budget)</option>
                    <option value={15.0}>$15 (Budget)</option>
                    <option value={20.0}>$20 (Economical)</option>
                    <option value={25.0}>$25 (Moderate)</option>
                    <option value={30.0}>$30 (Comfortable)</option>
                  </select>
                  <p className="text-xs text-yellow-600 mt-1">
                    AI will use affordable ingredients like beans, rice, and seasonal produce
                  </p>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Max Prep Time (minutes)</label>
              <input
                type="number"
                value={genRequest.prep_time_max}
                onChange={(e) => setGenRequest({...genRequest, prep_time_max: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 30"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Servings</label>
              <input
                type="number"
                value={genRequest.servings}
                onChange={(e) => setGenRequest({...genRequest, servings: parseInt(e.target.value)})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
                min="1"
                max="12"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
              <select
                value={genRequest.difficulty}
                onChange={(e) => setGenRequest({...genRequest, difficulty: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50"
            >
              {loading ? 'Generating Recipe...' : '🤖 Generate Recipe'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Recipe Detail Component
  const RecipeDetailScreen = ({ recipe, showBackButton = false }) => {
    const [showIngredients, setShowIngredients] = useState(true);
    const [groceryCart, setGroceryCart] = useState(null);

    const handleOrderGroceries = async () => {
      setLoading(true);
      try {
        const response = await axios.post(`${API}/grocery/cart`, null, {
          params: {
            recipe_id: recipe.id,
            user_id: user.id
          }
        });
        setGroceryCart(response.data);
      } catch (error) {
        console.error('Grocery cart error:', error);
        
        // If backend is not accessible, show demo cart
        if (error.code === 'ERR_NETWORK') {
          alert('Demo Mode: Showing sample grocery cart with Walmart URL.');
          const demoCart = {
            id: 'demo-cart-' + Date.now(),
            user_id: user.id,
            recipe_id: recipe.id,
            items: [
              {
                product_id: "123456789",
                name: "Main Ingredient",
                quantity: 2,
                price: 4.99,
                original_ingredient: recipe.ingredients[0] || "Main ingredient"
              },
              {
                product_id: "987654321", 
                name: "Fresh Onion",
                quantity: 1,
                price: 1.99,
                original_ingredient: "1 onion, diced"
              },
              {
                product_id: "456789123",
                name: "Fresh Garlic",
                quantity: 1,
                price: 2.49,
                original_ingredient: "2 cloves garlic, minced"
              },
              {
                product_id: "789123456",
                name: "Olive Oil",
                quantity: 1,
                price: 5.99,
                original_ingredient: "2 tbsp olive oil"
              }
            ],
            total_price: 15.46,
            walmart_url: "https://affil.walmart.com/cart/addToCart?items=123456789_2,987654321,456789123,789123456",
            demo: true
          };
          setGroceryCart(demoCart);
        } else {
          alert('Failed to create grocery cart. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    if (groceryCart) {
      return <GroceryCartScreen cart={groceryCart} />;
    }

    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm p-4">
          <div className="max-w-md mx-auto flex items-center justify-between">
            {showBackButton && (
              <button
                onClick={() => setCurrentScreen('dashboard')}
                className="p-2 text-gray-600 hover:text-gray-800"
              >
                ← Back
              </button>
            )}
            <h1 className="text-lg font-bold text-gray-800">{recipe.title}</h1>
            <button className="p-2 text-gray-600 hover:text-gray-800">
              ❤️
            </button>
          </div>
        </div>

        {/* Recipe Content */}
        <div className="p-4 max-w-md mx-auto space-y-4">
          {/* Recipe Info */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <p className="text-gray-600 mb-4">{recipe.description}</p>
            
            {/* Healthy Recipe Badge */}
            {recipe.is_healthy && (
              <div className="bg-green-100 border border-green-300 rounded-lg p-3 mb-4">
                <div className="flex items-center space-x-2">
                  <span className="text-green-600 text-lg">🍃</span>
                  <div>
                    <h4 className="text-green-800 font-semibold text-sm">Healthy Recipe</h4>
                    {recipe.calories_per_serving && (
                      <p className="text-green-700 text-xs">
                        {recipe.calories_per_serving} calories per serving
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-blue-50 p-3 rounded-xl">
                <div className="text-2xl">⏱️</div>
                <div className="text-sm text-gray-600">Prep</div>
                <div className="font-semibold">{recipe.prep_time}m</div>
              </div>
              <div className="bg-green-50 p-3 rounded-xl">
                <div className="text-2xl">🍳</div>
                <div className="text-sm text-gray-600">Cook</div>
                <div className="font-semibold">{recipe.cook_time}m</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-xl">
                <div className="text-2xl">👥</div>
                <div className="text-sm text-gray-600">Serves</div>
                <div className="font-semibold">{recipe.servings}</div>
              </div>
            </div>
            
            {/* Calorie info for healthy recipes */}
            {recipe.calories_per_serving && (
              <div className="mt-4 bg-green-50 p-3 rounded-xl text-center">
                <div className="text-2xl">🍃</div>
                <div className="text-sm text-green-600">Calories</div>
                <div className="font-semibold text-green-800">{recipe.calories_per_serving} cal</div>
              </div>
            )}
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-2xl shadow-sm p-2">
            <div className="flex space-x-2">
              <button
                onClick={() => setShowIngredients(true)}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                  showIngredients
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Ingredients
              </button>
              <button
                onClick={() => setShowIngredients(false)}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                  !showIngredients
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Instructions
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            {showIngredients ? (
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-800 mb-4">Ingredients</h3>
                {recipe.ingredients.map((ingredient, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded-lg">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-700">{ingredient}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-800 mb-4">Instructions</h3>
                {recipe.instructions.map((instruction, index) => (
                  <div key={index} className="flex space-x-4 p-3 hover:bg-gray-50 rounded-lg">
                    <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                      {index + 1}
                    </div>
                    <p className="text-gray-700 flex-1">{instruction}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Order Groceries Button */}
          <button
            onClick={handleOrderGroceries}
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Creating Cart...' : '🛒 Order Groceries from Walmart'}
          </button>
        </div>
      </div>
    );
  };

  // All Recipes Screen Component
  const AllRecipesScreen = () => {
    const [userRecipes, setUserRecipes] = useState([]);
    const [loadingRecipes, setLoadingRecipes] = useState(true);

    useEffect(() => {
      const loadUserRecipes = async () => {
        setLoadingRecipes(true);
        try {
          const response = await axios.get(`${API}/recipes?user_id=${user.id}`);
          setUserRecipes(response.data);
        } catch (error) {
          console.error('Error loading user recipes:', error);
        } finally {
          setLoadingRecipes(false);
        }
      };

      if (user?.id) {
        loadUserRecipes();
      }
    }, [user?.id]);

    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm p-4">
          <div className="max-w-md mx-auto flex items-center justify-between">
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="p-2 text-gray-600 hover:text-gray-800"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold text-gray-800">My Recipes</h2>
            <div></div>
          </div>
        </div>

        {/* Recipes List */}
        <div className="p-4 max-w-md mx-auto">
          {loadingRecipes ? (
            <div className="text-center py-8">
              <div className="loading text-gray-500">Loading your recipes...</div>
            </div>
          ) : userRecipes.length > 0 ? (
            <div className="space-y-4">
              {userRecipes.map((recipe) => (
                <div
                  key={recipe.id}
                  onClick={() => {
                    setCurrentScreen('recipe-detail');
                    window.currentRecipe = recipe;
                  }}
                  className="bg-white rounded-2xl shadow-sm p-6 hover:shadow-lg cursor-pointer transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800 mb-1">{recipe.title}</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">{recipe.description}</p>
                    </div>
                    {recipe.is_healthy && (
                      <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full ml-2">
                        🍃 Healthy
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>⏱️ {recipe.prep_time + recipe.cook_time}m</span>
                      <span>👥 {recipe.servings}</span>
                      <span>📊 {recipe.difficulty}</span>
                      {recipe.calories_per_serving && (
                        <span className="text-green-600">🍃 {recipe.calories_per_serving}cal</span>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(recipe.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📝</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">No recipes yet</h3>
              <p className="text-gray-500 mb-6">Start by generating your first AI recipe!</p>
              <button
                onClick={() => setCurrentScreen('generate')}
                className="bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
              >
                🤖 Generate Recipe
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };
  const GroceryCartScreen = ({ cart }) => {
    const handleOrderNow = () => {
      // Open Walmart URL
      window.open(cart.walmart_url, '_blank');
      
      // Show success message
      alert('Opening Walmart with your items! Complete your purchase there.');
      
      // Go back to dashboard
      setTimeout(() => {
        setCurrentScreen('dashboard');
      }, 1000);
    };

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto bg-white rounded-3xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="p-2 text-gray-600 hover:text-gray-800"
            >
              ← Back
            </button>
            <h2 className="text-xl font-bold text-gray-800">Grocery Cart</h2>
            <div></div>
          </div>

          <div className="space-y-4">
            {/* Cart Items */}
            <div className="space-y-3">
              {cart.items.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-800">{item.name}</h4>
                    <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                    {item.status === 'not_found' && (
                      <p className="text-xs text-red-500">⚠️ Not found - add manually</p>
                    )}
                  </div>
                  <div className="text-right">
                    <span className="font-semibold text-green-600">
                      ${(item.price * item.quantity).toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Total */}
            <div className="border-t pt-4">
              <div className="flex justify-between items-center mb-4">
                <span className="text-lg font-semibold text-gray-800">Total:</span>
                <span className="text-2xl font-bold text-green-600">${cart.total_price}</span>
              </div>

              <div className="bg-blue-50 p-4 rounded-xl mb-4">
                <p className="text-sm text-blue-800">
                  <strong>🛒 How it works:</strong> Clicking "Order Now" will open Walmart with these items pre-added to your cart. Complete your purchase there!
                </p>
              </div>

              <button
                onClick={handleOrderNow}
                className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
              >
                🛒 Order Now at Walmart
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render current screen
  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'home':
        return <HomeScreen />;
      case 'signup':
        return <SignupScreen />;
      case 'dashboard':
        return <DashboardScreen />;
      case 'generate':
        return <GenerateScreen />;
      case 'all-recipes':
        return <AllRecipesScreen />;
      case 'recipe-detail':
        return window.currentRecipe ? <RecipeDetailScreen recipe={window.currentRecipe} showBackButton={true} /> : <DashboardScreen />;
      default:
        return <HomeScreen />;
    }
  };

  return (
    <div className="App">
      {renderCurrentScreen()}
    </div>
  );
}

export default App;